#!/usr/bin/env python3
"""Build the static LibPub catalog, article HTML, PDF, feeds and reports."""

from __future__ import annotations

import argparse
import html
import json
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

from lxml import etree

from libpub import LibPubError, load_json, run, validate_article_xml, validate_metadata


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
TEMPLATES = ROOT / "templates"


def esc(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def author_name(author: dict[str, object]) -> str:
    return " ".join(part for part in (str(author.get("given", "")).strip(), str(author.get("family", "")).strip()) if part)


def pandoc_body(xml_path: Path) -> str:
    result = run(["pandoc", str(xml_path), "--from", "jats", "--to", "html5", "--wrap", "none"])
    body = result.stdout.strip()
    if not body:
        raise LibPubError(f"Pandoc không sinh được HTML từ {xml_path}.")
    return body


def meta_tags(metadata: dict[str, object], article_url: str) -> str:
    values: list[tuple[str, str]] = [
        ("citation_title", str(metadata["title"])),
        ("citation_publication_date", str(metadata["publishedDate"])),
        ("citation_pdf_url", f"{article_url}article.pdf"),
        ("citation_abstract", str(metadata["abstract"])),
        ("citation_language", str(metadata["language"])),
    ]
    if metadata.get("doi"):
        values.append(("citation_doi", str(metadata["doi"])))
    for author in metadata["authors"]:  # type: ignore[index]
        values.append(("citation_author", author_name(author)))
    for keyword in metadata["keywords"]:  # type: ignore[index]
        values.append(("citation_keywords", str(keyword)))
    return "\n".join(f'<meta name="{esc(name)}" content="{esc(value)}">' for name, value in values)


def render_article(template: str, metadata: dict[str, object], body: str, config: dict[str, object], article_url: str) -> str:
    authors = metadata["authors"]  # type: ignore[index]
    affiliations = {item["id"]: item for item in metadata.get("affiliations", [])}  # type: ignore[union-attr]
    author_html: list[str] = []
    for author in authors:
        refs = [str(ref) for ref in author.get("affiliations", [])]
        markers = ",".join(esc(ref) for ref in refs)
        name = esc(author_name(author))
        orcid = str(author.get("orcid", "")).strip()
        orcid_html = f' <a class="orcid" href="{esc(orcid)}" rel="me">ORCID</a>' if orcid else ""
        marker_html = f"<sup>{markers}</sup>" if markers else ""
        author_html.append(f'<span class="author">{name}{marker_html}{orcid_html}</span>')
    affiliation_html = "".join(
        f'<li><strong>{esc(key)}</strong> {esc(value.get("name", ""))}'
        f'{", " + esc(value.get("city", "")) if value.get("city") else ""}'
        f'{", " + esc(value.get("country", "")) if value.get("country") else ""}</li>'
        for key, value in affiliations.items()
    )
    doi = str(metadata.get("doi", "")).strip()
    doi_html = (
        f'<a href="https://doi.org/{quote(doi, safe="/.:;()")}">{esc(doi)}</a>'
        if doi
        else '<span class="muted">Chưa khai báo DOI</span>'
    )
    json_ld = {
        "@context": "https://schema.org",
        "@type": "ScholarlyArticle",
        "headline": metadata["title"],
        "abstract": metadata["abstract"],
        "datePublished": metadata["publishedDate"],
        "inLanguage": metadata["language"],
        "version": metadata["version"],
        "license": metadata["license"]["url"],  # type: ignore[index]
        "identifier": f"https://doi.org/{doi}" if doi else article_url,
        "url": article_url,
        "author": [
            {
                "@type": "Person",
                "name": author_name(author),
                **({"sameAs": author["orcid"]} if author.get("orcid") else {}),
            }
            for author in authors
        ],
        "keywords": metadata["keywords"],
        "publisher": {"@type": "Organization", "name": config["publisher"]},
    }
    replacements = {
        "{{LANG}}": esc(metadata["language"]),
        "{{TITLE}}": esc(metadata["title"]),
        "{{SUBTITLE}}": esc(metadata.get("subtitle", "")),
        "{{PUBLISHER}}": esc(config["publisher"]),
        "{{SITE_NAME}}": esc(config["name"]),
        "{{META_TAGS}}": meta_tags(metadata, article_url),
        "{{JSON_LD}}": json.dumps(json_ld, ensure_ascii=False).replace("<", "\\u003c"),
        "{{AUTHORS}}": " · ".join(author_html),
        "{{AFFILIATIONS}}": affiliation_html,
        "{{ABSTRACT}}": esc(metadata["abstract"]),
        "{{KEYWORDS}}": "".join(f"<li>{esc(keyword)}</li>" for keyword in metadata["keywords"]),  # type: ignore[index]
        "{{ARTICLE_TYPE}}": esc(metadata["articleType"]),
        "{{STATUS}}": esc(metadata["status"]),
        "{{VERSION}}": esc(metadata["version"]),
        "{{DATE}}": esc(metadata["publishedDate"]),
        "{{DOI}}": doi_html,
        "{{LICENSE_ID}}": esc(metadata["license"]["id"]),  # type: ignore[index]
        "{{LICENSE_URL}}": esc(metadata["license"]["url"]),  # type: ignore[index]
        "{{BODY}}": body,
    }
    rendered = template
    for marker, value in replacements.items():
        rendered = rendered.replace(marker, value)
    return rendered


def render_pdf(print_html: str, output: Path, resource_path: Path) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
        handle.write(print_html)
        temporary = Path(handle.name)
    try:
        run([
            "pandoc",
            str(temporary),
            "--from",
            "html",
            "--pdf-engine",
            "xelatex",
            "--resource-path",
            str(resource_path),
            "--variable",
            "mainfont=DejaVu Serif",
            "--variable",
            "sansfont=DejaVu Sans",
            "--variable",
            "geometry:margin=2.2cm",
            "--variable",
            "fontsize=10pt",
            "--variable",
            "colorlinks=true",
            "--output",
            str(output),
        ])
    finally:
        temporary.unlink(missing_ok=True)


def print_document(metadata: dict[str, object], body: str) -> str:
    author_line = ", ".join(esc(author_name(author)) for author in metadata["authors"])  # type: ignore[index]
    return f"""<!DOCTYPE html><html lang="{esc(metadata['language'])}"><head><meta charset="utf-8"></head><body>
<h1>{esc(metadata['title'])}</h1><p><strong>{author_line}</strong></p>
<p>Phiên bản {esc(metadata['version'])} · {esc(metadata['publishedDate'])}</p>
<h2>Tóm tắt</h2><p>{esc(metadata['abstract'])}</p><hr>{body}
<hr><p>Giấy phép: {esc(metadata['license']['id'])}. Nguồn: LibPub.</p></body></html>"""  # type: ignore[index]


def build_feed(records: list[dict[str, object]], config: dict[str, object], output: Path) -> None:
    atom = "http://www.w3.org/2005/Atom"
    feed = etree.Element(f"{{{atom}}}feed", nsmap={None: atom})
    etree.SubElement(feed, f"{{{atom}}}title").text = str(config["name"])
    etree.SubElement(feed, f"{{{atom}}}id").text = str(config["baseUrl"])
    etree.SubElement(feed, f"{{{atom}}}updated").text = datetime.now(timezone.utc).isoformat()
    etree.SubElement(feed, f"{{{atom}}}link", href=f"{config['baseUrl']}/feed.xml", rel="self")
    for record in records:
        entry = etree.SubElement(feed, f"{{{atom}}}entry")
        etree.SubElement(entry, f"{{{atom}}}title").text = str(record["title"])
        etree.SubElement(entry, f"{{{atom}}}id").text = str(record.get("doiUrl") or record["url"])
        etree.SubElement(entry, f"{{{atom}}}updated").text = f"{record['publishedDate']}T00:00:00+00:00"
        etree.SubElement(entry, f"{{{atom}}}link", href=str(record["url"]))
        etree.SubElement(entry, f"{{{atom}}}summary").text = str(record["abstract"])
    output.write_bytes(etree.tostring(feed, encoding="utf-8", xml_declaration=True, pretty_print=True))


def build_sitemap(records: list[dict[str, object]], config: dict[str, object], output: Path) -> None:
    namespace = "http://www.sitemaps.org/schemas/sitemap/0.9"
    root = etree.Element(f"{{{namespace}}}urlset", nsmap={None: namespace})
    for url, lastmod in [(f"{config['baseUrl']}/", None)] + [(str(item["url"]), str(item["publishedDate"])) for item in records]:
        node = etree.SubElement(root, f"{{{namespace}}}url")
        etree.SubElement(node, f"{{{namespace}}}loc").text = url
        if lastmod:
            etree.SubElement(node, f"{{{namespace}}}lastmod").text = lastmod
    output.write_bytes(etree.tostring(root, encoding="utf-8", xml_declaration=True, pretty_print=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    parser.add_argument("--skip-pdf", action="store_true")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    config = load_json(ROOT / "publication.config.json")
    template = (TEMPLATES / "article.html").read_text(encoding="utf-8")
    records: list[dict[str, object]] = []
    warnings: list[str] = []
    for article_dir in sorted(path for path in ARTICLES.iterdir() if path.is_dir() and not path.name.startswith(".")):
        slug = article_dir.name
        metadata = load_json(article_dir / "metadata.json")
        warnings.extend(f"{slug}: {item}" for item in validate_metadata(metadata, slug))
        xml_path = article_dir / "article.xml"
        if not xml_path.exists():
            work_xml = ROOT / ".libpub" / "work" / slug / "article.xml"
            if work_xml.exists():
                xml_path = work_xml
            else:
                raise LibPubError(f"{slug}: chưa có article.xml; hãy chạy prepare_sources.py.")
        warnings.extend(f"{slug}: {item}" for item in validate_article_xml(xml_path))
        body = pandoc_body(xml_path)
        target = output / "articles" / slug
        target.mkdir(parents=True, exist_ok=True)
        article_url = f"{str(config['baseUrl']).rstrip('/')}/articles/{slug}/"
        page = render_article(template, metadata, body, config, article_url)
        (target / "index.html").write_text(page, encoding="utf-8")
        shutil.copy2(xml_path, target / "article.xml")
        if (article_dir / "manuscript.docx").exists():
            shutil.copy2(article_dir / "manuscript.docx", target / "manuscript.docx")
        if not args.skip_pdf:
            render_pdf(print_document(metadata, body), target / "article.pdf", article_dir)
        doi = str(metadata.get("doi", "")).strip()
        record = {
            "slug": slug,
            "title": metadata["title"],
            "subtitle": metadata.get("subtitle", ""),
            "abstract": metadata["abstract"],
            "authors": [author_name(author) for author in metadata["authors"]],
            "keywords": metadata["keywords"],
            "language": metadata["language"],
            "articleType": metadata["articleType"],
            "status": metadata["status"],
            "version": metadata["version"],
            "doi": doi,
            "doiUrl": f"https://doi.org/{doi}" if doi else "",
            "publishedDate": metadata["publishedDate"],
            "license": metadata["license"],
            "url": article_url,
            "pdf": f"{article_url}article.pdf" if not args.skip_pdf else "",
            "xml": f"{article_url}article.xml",
        }
        records.append(record)
        print(f"✓ build {slug}")
    records.sort(key=lambda item: str(item["publishedDate"]), reverse=True)
    for asset in ("assets",):
        shutil.copytree(ROOT / asset, output / asset)
    shutil.copy2(ROOT / "publication.config.json", output / "publication.config.json")
    shutil.copytree(ROOT / "schemas", output / "schemas")
    index_source = (ROOT / "index.html").read_text(encoding="utf-8")
    inline = json.dumps(records, ensure_ascii=False).replace("</", "<\\/")
    index_source = index_source.replace("window.LIBPUB_ARTICLES = [];", f"window.LIBPUB_ARTICLES = {inline};")
    (output / "index.html").write_text(index_source, encoding="utf-8")
    (output / "articles.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    build_report = {
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "articleCount": len(records),
        "warnings": warnings,
        "pdfEnabled": not args.skip_pdf,
    }
    (output / "build-report.json").write_text(json.dumps(build_report, ensure_ascii=False, indent=2), encoding="utf-8")
    build_feed(records, config, output / "feed.xml")
    build_sitemap(records, config, output / "sitemap.xml")
    (output / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {config['baseUrl']}/sitemap.xml\n", encoding="utf-8")
    (output / ".nojekyll").write_text("", encoding="utf-8")
    print(f"✓ {len(records)} bài báo → {output}")
    for warning in warnings:
        print(f"! {warning}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except LibPubError as exc:
        print(f"Lỗi build: {exc}", file=sys.stderr)
        raise SystemExit(1)
