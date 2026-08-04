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

ARTICLE_UI = {
    "vi": {
        "skip": "Đi đến nội dung", "actions": "Tác vụ bài báo", "submit": "Gửi bản thảo",
        "version": "phiên bản", "published": "Công bố", "license": "Giấy phép", "abstract": "Tóm tắt",
        "tools": "Công cụ bài báo", "download": "Tải toàn văn", "status": "Trạng thái",
        "status_note": "Preprint được lưu phiên bản bằng lịch sử Git.", "built_with": "Xuất bản bằng",
        "no_doi": "Đang chờ DOI", "zenodo": "Bản ghi Zenodo ↗",
        "pdf_version": "Phiên bản", "pdf_license": "Giấy phép", "pdf_source": "Nguồn",
    },
    "en": {
        "skip": "Skip to content", "actions": "Article actions", "submit": "Submit a manuscript",
        "version": "version", "published": "Published", "license": "License", "abstract": "Abstract",
        "tools": "Article tools", "download": "Download full text", "status": "Status",
        "status_note": "This preprint is versioned through Git history.", "built_with": "Published with",
        "no_doi": "DOI pending", "zenodo": "Zenodo record ↗",
        "pdf_version": "Version", "pdf_license": "License", "pdf_source": "Source",
    },
    "zh": {
        "skip": "跳至正文", "actions": "论文操作", "submit": "提交稿件",
        "version": "版本", "published": "发布日期", "license": "许可证", "abstract": "摘要",
        "tools": "论文工具", "download": "下载全文", "status": "状态",
        "status_note": "该预印本的各版本均保存在 Git 历史中。", "built_with": "出版工具",
        "no_doi": "DOI 生成中", "zenodo": "Zenodo 记录 ↗",
        "pdf_version": "版本", "pdf_license": "许可证", "pdf_source": "来源",
    },
}

ARTICLE_TYPES = {
    "vi": {"research-article": "Bài nghiên cứu", "review-article": "Bài tổng quan", "methods-article": "Bài phương pháp", "data-paper": "Bài dữ liệu", "policy-paper": "Bài chính sách", "case-report": "Báo cáo trường hợp", "other": "Khác"},
    "en": {"research-article": "Research article", "review-article": "Review article", "methods-article": "Methods article", "data-paper": "Data paper", "policy-paper": "Policy paper", "case-report": "Case report", "other": "Other"},
    "zh": {"research-article": "研究论文", "review-article": "综述论文", "methods-article": "方法论文", "data-paper": "数据论文", "policy-paper": "政策论文", "case-report": "病例报告", "other": "其他"},
}

ARTICLE_STATUSES = {
    "vi": {"preprint": "Preprint", "revised": "Đã sửa", "published": "Đã xuất bản", "withdrawn": "Đã rút"},
    "en": {"preprint": "Preprint", "revised": "Revised", "published": "Published", "withdrawn": "Withdrawn"},
    "zh": {"preprint": "预印本", "revised": "修订版", "published": "已出版", "withdrawn": "已撤稿"},
}


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
    language = str(metadata.get("language", "vi"))
    ui = ARTICLE_UI.get(language, ARTICLE_UI["vi"])
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
        else f'<span class="muted">{esc(ui["no_doi"])}</span>'
    )
    zenodo = metadata.get("zenodo", {})
    record_url = str(zenodo.get("recordUrl", "")).strip() if isinstance(zenodo, dict) else ""
    zenodo_link = f'<a href="{esc(record_url)}" target="_blank" rel="noopener">{esc(ui["zenodo"])}</a>' if record_url else ""
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
        "{{ARTICLE_TYPE}}": esc(ARTICLE_TYPES.get(language, ARTICLE_TYPES["vi"]).get(str(metadata["articleType"]), str(metadata["articleType"]))),
        "{{STATUS}}": esc(ARTICLE_STATUSES.get(language, ARTICLE_STATUSES["vi"]).get(str(metadata["status"]), str(metadata["status"]))),
        "{{VERSION}}": esc(metadata["version"]),
        "{{DATE}}": esc(metadata["publishedDate"]),
        "{{DOI}}": doi_html,
        "{{LICENSE_ID}}": esc(metadata["license"]["id"]),  # type: ignore[index]
        "{{LICENSE_URL}}": esc(metadata["license"]["url"]),  # type: ignore[index]
        "{{BODY}}": body,
        "{{LABEL_SKIP}}": esc(ui["skip"]),
        "{{LABEL_ARTICLE_ACTIONS}}": esc(ui["actions"]),
        "{{LABEL_SUBMIT}}": esc(ui["submit"]),
        "{{LABEL_VERSION}}": esc(ui["version"]),
        "{{LABEL_PUBLISHED}}": esc(ui["published"]),
        "{{LABEL_LICENSE}}": esc(ui["license"]),
        "{{LABEL_ABSTRACT}}": esc(ui["abstract"]),
        "{{LABEL_ARTICLE_TOOLS}}": esc(ui["tools"]),
        "{{LABEL_DOWNLOAD}}": esc(ui["download"]),
        "{{LABEL_STATUS}}": esc(ui["status"]),
        "{{LABEL_STATUS_NOTE}}": esc(ui["status_note"]),
        "{{LABEL_BUILT_WITH}}": esc(ui["built_with"]),
        "{{ZENODO_LINK}}": zenodo_link,
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
    ui = ARTICLE_UI.get(str(metadata.get("language", "vi")), ARTICLE_UI["vi"])
    author_line = ", ".join(esc(author_name(author)) for author in metadata["authors"])  # type: ignore[index]
    return f"""<!DOCTYPE html><html lang="{esc(metadata['language'])}"><head><meta charset="utf-8"></head><body>
<h1>{esc(metadata['title'])}</h1><p><strong>{author_line}</strong></p>
<p>{esc(ui['pdf_version'])} {esc(metadata['version'])} · {esc(metadata['publishedDate'])}</p>
<h2>{esc(ui['abstract'])}</h2><p>{esc(metadata['abstract'])}</p><hr>{body}
<hr><p>{esc(ui['pdf_license'])}: {esc(metadata['license']['id'])}. {esc(ui['pdf_source'])}: LibPub.</p></body></html>"""  # type: ignore[index]


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
    parser.add_argument("--output", type=Path, default=ROOT / "output")
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
        shutil.copy2(article_dir / "metadata.json", target / "metadata.json")
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
            "zenodo": metadata.get("zenodo", {}),
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
