"""Shared validation and JATS helpers for LibPub."""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from datetime import date
from pathlib import Path
from typing import Any, Iterable

from lxml import etree


DOI_RE = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ORCID_RE = re.compile(r"^https://orcid\.org/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])$")
LICENSES = {
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    "ARR": "https://rightsstatements.org/page/InC/1.0/",
}
ARTICLE_TYPES = {
    "research-article",
    "review-article",
    "case-report",
    "methods-article",
    "data-paper",
    "policy-paper",
    "other",
}


class LibPubError(RuntimeError):
    """An actionable authoring or build error."""


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise LibPubError(f"Không đọc được JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise LibPubError(f"{path} phải chứa một đối tượng JSON.")
    return value


def _required_text(data: dict[str, Any], key: str, minimum: int = 1) -> str:
    value = data.get(key)
    if not isinstance(value, str) or len(value.strip()) < minimum:
        raise LibPubError(f"Trường metadata '{key}' phải có ít nhất {minimum} ký tự.")
    return value.strip()


def _valid_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def valid_orcid(uri: str) -> bool:
    match = ORCID_RE.match(uri)
    if not match:
        return False
    digits = match.group(1).replace("-", "")
    total = 0
    for char in digits[:15]:
        total = (total + int(char)) * 2
    result = (12 - (total % 11)) % 11
    check = "X" if result == 10 else str(result)
    return check == digits[-1]


def validate_metadata(data: dict[str, Any], expected_slug: str | None = None) -> list[str]:
    warnings: list[str] = []
    if data.get("schemaVersion") != "1.0":
        raise LibPubError("schemaVersion phải là '1.0'.")
    slug = _required_text(data, "slug", 3)
    if not SLUG_RE.match(slug) or len(slug) > 100:
        raise LibPubError("slug chỉ gồm chữ thường ASCII, số và dấu gạch ngang.")
    if expected_slug and slug != expected_slug:
        raise LibPubError(f"metadata.slug '{slug}' khác tên thư mục '{expected_slug}'.")
    _required_text(data, "title", 10)
    _required_text(data, "abstract", 20)
    keywords = data.get("keywords")
    if not isinstance(keywords, list) or not keywords or not all(isinstance(v, str) and len(v.strip()) >= 2 for v in keywords):
        raise LibPubError("keywords phải là mảng có ít nhất một từ khóa hợp lệ.")
    if len(keywords) != len(set(v.strip().casefold() for v in keywords)):
        raise LibPubError("keywords không được trùng lặp.")
    language = _required_text(data, "language", 2)
    if not re.match(r"^[a-z]{2}(?:-[A-Z]{2})?$", language):
        raise LibPubError("language phải theo BCP 47 rút gọn, ví dụ 'vi' hoặc 'en-US'.")
    if data.get("articleType") not in ARTICLE_TYPES:
        raise LibPubError("articleType không thuộc danh mục LibPub hỗ trợ.")
    if data.get("status") not in {"preprint", "published", "revised", "withdrawn"}:
        raise LibPubError("status không hợp lệ.")
    if not isinstance(data.get("version"), int) or data["version"] < 1:
        raise LibPubError("version phải là số nguyên từ 1.")
    if "autoDoi" in data and not isinstance(data["autoDoi"], bool):
        raise LibPubError("autoDoi phải là true hoặc false.")
    for field in ("publishedDate", "receivedDate", "acceptedDate"):
        value = data.get(field)
        if value and (not isinstance(value, str) or not _valid_iso_date(value)):
            raise LibPubError(f"{field} phải theo định dạng YYYY-MM-DD.")
    _required_text(data, "publishedDate", 10)
    doi = str(data.get("doi", "")).strip()
    if doi and not DOI_RE.match(doi):
        raise LibPubError("DOI không đúng cú pháp, ví dụ 10.1234/libpub.2026.001.")
    license_data = data.get("license")
    if not isinstance(license_data, dict) or license_data.get("id") not in LICENSES:
        raise LibPubError("license.id không hợp lệ.")
    if license_data.get("url") != LICENSES[license_data["id"]]:
        warnings.append("license.url khác URL chuẩn; LibPub vẫn giữ giá trị đã khai báo.")
    authors = data.get("authors")
    if not isinstance(authors, list) or not authors:
        raise LibPubError("Phải khai báo ít nhất một tác giả.")
    for index, author in enumerate(authors, start=1):
        if not isinstance(author, dict):
            raise LibPubError(f"Tác giả {index} phải là một đối tượng JSON.")
        _required_text(author, "given")
        _required_text(author, "family")
        if not isinstance(author.get("affiliations", []), list):
            raise LibPubError(f"affiliations của tác giả {index} phải là một mảng.")
        orcid = str(author.get("orcid", "")).strip()
        if orcid and not valid_orcid(orcid):
            raise LibPubError(f"ORCID của tác giả {index} không hợp lệ hoặc sai checksum.")
    affiliation_ids = {item.get("id") for item in data.get("affiliations", []) if isinstance(item, dict)}
    for author in authors:
        unknown = set(author.get("affiliations", [])) - affiliation_ids
        if unknown:
            raise LibPubError(f"Tác giả tham chiếu affiliation chưa khai báo: {', '.join(sorted(unknown))}.")
    return warnings


def parse_xml(path: Path) -> etree._ElementTree:
    parser = etree.XMLParser(resolve_entities=False, no_network=True, recover=False, remove_blank_text=False)
    try:
        return etree.parse(str(path), parser)
    except (OSError, etree.XMLSyntaxError) as exc:
        raise LibPubError(f"XML không hợp lệ {path}: {exc}") from exc


def local_name(node: etree._Element) -> str:
    return etree.QName(node).localname


def validate_article_xml(path: Path) -> list[str]:
    tree = parse_xml(path)
    root = tree.getroot()
    if local_name(root) != "article":
        raise LibPubError(f"{path} phải có phần tử gốc <article> theo JATS.")
    bodies = root.xpath("./*[local-name()='body']")
    if not bodies:
        raise LibPubError(f"{path} thiếu phần tử <body>.")
    text = " ".join("".join(bodies[0].itertext()).split())
    if len(text) < 20:
        raise LibPubError(f"Nội dung <body> trong {path} quá ngắn.")
    warnings: list[str] = []
    if not root.xpath("./*[local-name()='front']"):
        warnings.append("JATS chưa có <front>; metadata.json sẽ cung cấp metadata hiển thị.")
    return warnings


def add_text(parent: etree._Element, tag: str, value: str | None, **attributes: str) -> etree._Element | None:
    if not value:
        return None
    element = etree.SubElement(parent, tag, **attributes)
    element.text = value
    return element


def sync_generated_jats_metadata(path: Path, metadata: dict[str, Any]) -> None:
    """Create a complete JATS front section for XML generated from DOCX."""
    tree = parse_xml(path)
    root = tree.getroot()
    for existing in root.xpath("./*[local-name()='front']"):
        root.remove(existing)
    front = etree.Element("front")
    article_meta = etree.SubElement(front, "article-meta")
    if metadata.get("doi"):
        add_text(article_meta, "article-id", metadata["doi"], **{"pub-id-type": "doi"})
    title_group = etree.SubElement(article_meta, "title-group")
    add_text(title_group, "article-title", metadata["title"])
    add_text(title_group, "subtitle", metadata.get("subtitle"))
    contrib_group = etree.SubElement(article_meta, "contrib-group")
    for author in metadata["authors"]:
        contrib = etree.SubElement(contrib_group, "contrib", **{"contrib-type": "author"})
        if author.get("corresponding"):
            contrib.set("corresp", "yes")
        name = etree.SubElement(contrib, "name", **{"name-style": "western"})
        add_text(name, "surname", author["family"])
        add_text(name, "given-names", author["given"])
        if author.get("orcid"):
            add_text(contrib, "contrib-id", author["orcid"], **{"contrib-id-type": "orcid"})
        for aff_id in author.get("affiliations", []):
            etree.SubElement(contrib, "xref", **{"ref-type": "aff", "rid": aff_id})
        add_text(contrib, "email", author.get("email"))
    for affiliation in metadata.get("affiliations", []):
        aff = etree.SubElement(article_meta, "aff", id=affiliation["id"])
        parts = [affiliation.get("name"), affiliation.get("city"), affiliation.get("country")]
        aff.text = ", ".join(part for part in parts if part)
    published = date.fromisoformat(metadata["publishedDate"])
    pub_date = etree.SubElement(article_meta, "pub-date", **{"pub-type": "epub"})
    add_text(pub_date, "day", str(published.day))
    add_text(pub_date, "month", str(published.month))
    add_text(pub_date, "year", str(published.year))
    abstract = etree.SubElement(article_meta, "abstract")
    add_text(abstract, "p", metadata["abstract"])
    keyword_group = etree.SubElement(article_meta, "kwd-group")
    for keyword in metadata["keywords"]:
        add_text(keyword_group, "kwd", keyword)
    permissions = etree.SubElement(article_meta, "permissions")
    license_el = etree.SubElement(permissions, "license", **{"{http://www.w3.org/1999/xlink}href": metadata["license"]["url"]})
    add_text(license_el, "license-p", metadata["license"]["id"])
    first_content = next(iter(root), None)
    if first_content is None:
        root.append(front)
    else:
        root.insert(root.index(first_content), front)
    tree.write(str(path), encoding="utf-8", xml_declaration=True, pretty_print=True)


def run(command: Iterable[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    command_list = [str(part) for part in command]
    try:
        return subprocess.run(
            command_list,
            cwd=str(cwd) if cwd else None,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except FileNotFoundError as exc:
        raise LibPubError(f"Thiếu công cụ bắt buộc: {command_list[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise LibPubError(f"Lệnh thất bại ({' '.join(command_list)}): {detail}") from exc


def slugify(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", normalized.casefold()).strip("-")
    return slug[:100] or "ban-thao-moi"
