#!/usr/bin/env python3
"""Generate Zenodo metadata, publish through REST, resolve GitHub records and apply DOI."""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from libpub import LibPubError, load_json, parse_xml, validate_metadata


ROOT = Path(__file__).resolve().parents[1]
LICENSE_MAP = {
    "CC-BY-4.0": "cc-by-4.0",
    "CC-BY-SA-4.0": "cc-by-sa-4.0",
    "CC0-1.0": "cc-zero",
    "ARR": "other-open",
}
LANGUAGE_MAP = {"vi": "vie", "en": "eng", "zh": "zho"}


def affiliation_map(metadata: dict[str, Any]) -> dict[str, str]:
    return {item["id"]: item["name"] for item in metadata.get("affiliations", [])}


def zenodo_creators(metadata: dict[str, Any]) -> list[dict[str, str]]:
    affiliations = affiliation_map(metadata)
    creators = []
    for author in metadata["authors"]:
        item = {"name": f"{author['family']}, {author['given']}"}
        if author.get("orcid"):
            item["orcid"] = author["orcid"].removeprefix("https://orcid.org/")
        names = [affiliations[ref] for ref in author.get("affiliations", []) if ref in affiliations]
        if names:
            item["affiliation"] = "; ".join(names)
        creators.append(item)
    return creators


def zenodo_metadata(metadata: dict[str, Any], repository: str, tag: str) -> dict[str, Any]:
    slug = metadata["slug"]
    release_url = f"https://github.com/{repository}/releases/tag/{tag}"
    language = str(metadata.get("language", "en")).split("-")[0]
    result: dict[str, Any] = {
        "title": metadata["title"],
        "upload_type": "publication",
        "publication_type": "article",
        "description": metadata["abstract"],
        "creators": zenodo_creators(metadata),
        "keywords": metadata.get("keywords", []),
        "publication_date": metadata["publishedDate"],
        "version": str(metadata["version"]),
        "language": LANGUAGE_MAP.get(language, "eng"),
        "access_right": "open",
        "license": LICENSE_MAP.get(metadata["license"]["id"], "cc-by-4.0"),
        "related_identifiers": [
            {
                "identifier": release_url,
                "relation": "isSupplementTo",
                "resource_type": "publication-article",
            },
            {
                "identifier": f"https://github.com/{repository}/tree/{tag}/articles/{slug}",
                "relation": "isSupplementTo",
                "resource_type": "publication-article",
            },
        ],
    }
    return result


def request_json(url: str, method: str = "GET", payload: Any = None, token: str = "") -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Accept": "application/json", "User-Agent": "LibPub/1.1"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LibPubError(f"Zenodo API {exc.code}: {detail[:1000]}") from exc


def upload_file(bucket_url: str, path: Path, token: str) -> None:
    url = f"{bucket_url.rstrip('/')}/{urllib.parse.quote(path.name)}"
    request = urllib.request.Request(
        url,
        data=path.read_bytes(),
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/octet-stream", "User-Agent": "LibPub/1.1"},
        method="PUT",
    )
    try:
        with urllib.request.urlopen(request, timeout=300) as response:
            if response.status not in {200, 201}:
                raise LibPubError(f"Zenodo từ chối tệp {path.name}: HTTP {response.status}")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise LibPubError(f"Không upload được {path.name}: {exc.code} {detail[:500]}") from exc


def publish_api(metadata: dict[str, Any], repository: str, tag: str, assets: list[Path], base_url: str, token: str) -> dict[str, Any]:
    if not token:
        raise LibPubError("Thiếu ZENODO_ACCESS_TOKEN cho chế độ Zenodo REST API.")
    deposit = request_json(
        f"{base_url.rstrip('/')}/api/deposit/depositions",
        method="POST",
        payload={"metadata": {**zenodo_metadata(metadata, repository, tag), "prereserve_doi": True}},
        token=token,
    )
    for asset in assets:
        if asset.exists() and asset.is_file():
            upload_file(deposit["links"]["bucket"], asset, token)
    published = request_json(deposit["links"]["publish"], method="POST", payload={}, token=token)
    return normalize_record(published, source="zenodo-api", tag=tag)


def normalize_record(record: dict[str, Any], source: str, tag: str) -> dict[str, Any]:
    metadata = record.get("metadata", {})
    doi = record.get("doi") or metadata.get("doi")
    if not doi:
        prereg = metadata.get("prereserve_doi") or {}
        doi = prereg.get("doi")
    record_id = str(record.get("id") or "")
    links = record.get("links", {})
    record_url = links.get("html") or links.get("self_html") or (f"https://zenodo.org/records/{record_id}" if record_id else "")
    return {
        "doi": doi or "",
        "conceptDoi": record.get("conceptdoi") or metadata.get("conceptdoi") or "",
        "recordId": record_id,
        "recordUrl": record_url,
        "source": source,
        "tag": tag,
    }


def search_records(api_url: str, repository: str, tag: str) -> dict[str, Any] | None:
    release_url = f"https://github.com/{repository}/releases/tag/{tag}"
    tree_url = f"https://github.com/{repository}/tree/{tag}"
    queries = [
        f'related.identifiers.identifier:"{release_url}"',
        f'related_identifiers.identifier:"{release_url}"',
        f'related.identifiers.identifier:"{tree_url}"',
        f'"{repository}" AND "{tag}"',
    ]
    for query in queries:
        params = urllib.parse.urlencode({"q": query, "size": 10, "sort": "newest"})
        try:
            response = request_json(f"{api_url.rstrip('/')}/api/records?{params}")
        except LibPubError:
            continue
        for record in response.get("hits", {}).get("hits", []):
            normalized = normalize_record(record, source="github-release", tag=tag)
            text = json.dumps(record, ensure_ascii=False)
            if normalized["doi"] and (tag in text or release_url in text or tree_url in text):
                return normalized
    return None


def resolve_github(api_url: str, repository: str, tag: str, attempts: int, interval: int) -> dict[str, Any]:
    for attempt in range(1, attempts + 1):
        record = search_records(api_url, repository, tag)
        if record:
            return record
        print(f"Zenodo chưa có DOI cho {tag} (lần {attempt}/{attempts}).", flush=True)
        if attempt < attempts:
            time.sleep(interval)
    raise LibPubError(f"Hết thời gian chờ DOI cho {tag}; hãy chạy lại workflow Zenodo Sync sau.")


def apply_doi(metadata_path: Path, result: dict[str, Any]) -> None:
    metadata = load_json(metadata_path)
    existing = str(metadata.get("doi", "")).strip()
    doi = str(result.get("doi", "")).strip()
    if not doi:
        raise LibPubError("Kết quả Zenodo không chứa DOI.")
    if existing and existing != doi:
        raise LibPubError(f"Không ghi đè DOI hiện có {existing} bằng {doi}; hãy tăng version và xóa DOI cũ có chủ đích.")
    metadata["doi"] = doi
    metadata["zenodo"] = {
        **result,
        "doi": doi,
        "syncedAt": datetime.now(timezone.utc).isoformat(),
    }
    validate_metadata(metadata, metadata["slug"])
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    xml_path = metadata_path.with_name("article.xml")
    if xml_path.exists():
        tree = parse_xml(xml_path)
        article_meta = tree.xpath("/*[local-name()='article']/*[local-name()='front']/*[local-name()='article-meta']")
        if article_meta:
            doi_nodes = article_meta[0].xpath("./*[local-name()='article-id' and @pub-id-type='doi']")
            if doi_nodes:
                doi_nodes[0].text = doi
            else:
                node = article_meta[0].makeelement("article-id", {"pub-id-type": "doi"})
                node.text = doi
                article_meta[0].insert(0, node)
            tree.write(str(xml_path), encoding="utf-8", xml_declaration=True, pretty_print=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    metadata_parser = subparsers.add_parser("metadata")
    metadata_parser.add_argument("--article", type=Path, required=True)
    metadata_parser.add_argument("--repository", required=True)
    metadata_parser.add_argument("--tag", required=True)
    metadata_parser.add_argument("--output", type=Path, required=True)

    resolve_parser = subparsers.add_parser("resolve")
    resolve_parser.add_argument("--repository", required=True)
    resolve_parser.add_argument("--tag", required=True)
    resolve_parser.add_argument("--api-url", default="https://zenodo.org")
    resolve_parser.add_argument("--attempts", type=int, default=40)
    resolve_parser.add_argument("--interval", type=int, default=15)
    resolve_parser.add_argument("--output", type=Path, required=True)

    deposit_parser = subparsers.add_parser("deposit")
    deposit_parser.add_argument("--article", type=Path, required=True)
    deposit_parser.add_argument("--repository", required=True)
    deposit_parser.add_argument("--tag", required=True)
    deposit_parser.add_argument("--assets", type=Path, required=True)
    deposit_parser.add_argument("--api-url", default="https://zenodo.org")
    deposit_parser.add_argument("--output", type=Path, required=True)

    apply_parser = subparsers.add_parser("apply")
    apply_parser.add_argument("--metadata", type=Path, required=True)
    apply_parser.add_argument("--result", type=Path, required=True)

    args = parser.parse_args()
    if args.command == "metadata":
        metadata = load_json(args.article / "metadata.json")
        validate_metadata(metadata, args.article.name)
        result = zenodo_metadata(metadata, args.repository, args.tag)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif args.command == "resolve":
        result = resolve_github(args.api_url, args.repository, args.tag, args.attempts, args.interval)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif args.command == "deposit":
        metadata = load_json(args.article / "metadata.json")
        validate_metadata(metadata, args.article.name)
        assets = [
            path for path in args.assets.iterdir()
            if path.is_file() and path.name in {"article.pdf", "article.xml", "metadata.json", "zenodo.json", "manuscript.docx"}
        ]
        result = publish_api(metadata, args.repository, args.tag, assets, args.api_url, os.environ.get("ZENODO_ACCESS_TOKEN", ""))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    elif args.command == "apply":
        apply_doi(args.metadata, load_json(args.result))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LibPubError as exc:
        print(f"Lỗi Zenodo: {exc}")
        raise SystemExit(1)
