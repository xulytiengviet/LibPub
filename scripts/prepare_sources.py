#!/usr/bin/env python3
"""Prepare JATS XML from author-supplied XML or DOCX manuscripts."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

from libpub import LibPubError, load_json, run, sync_generated_jats_metadata, validate_article_xml, validate_metadata


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
WORK = ROOT / ".libpub" / "work"


def xsweet_convert(docx: Path, html: Path, endpoint: str) -> None:
    result = run([
        "curl",
        "--fail",
        "--silent",
        "--show-error",
        "--max-time",
        "180",
        "-F",
        f"input=@{docx}",
        endpoint,
    ])
    if "<" not in result.stdout:
        raise LibPubError("XSweet không trả về HTML hợp lệ.")
    html.write_text(result.stdout, encoding="utf-8")


def pandoc_to_jats(source: Path, source_format: str, output: Path, media_dir: Path) -> None:
    command = ["pandoc", str(source), "--from", source_format, "--to", "jats", "--output", str(output)]
    if source_format == "docx":
        command.extend(["--extract-media", str(media_dir)])
    run(command)


def prepare_article(article_dir: Path, write_back: bool, force: bool, xsweet_url: str) -> dict[str, object]:
    slug = article_dir.name
    metadata_path = article_dir / "metadata.json"
    if not metadata_path.exists():
        raise LibPubError(f"{article_dir} thiếu metadata.json.")
    metadata = load_json(metadata_path)
    warnings = validate_metadata(metadata, slug)
    supplied_xml = article_dir / "article.xml"
    docx = article_dir / "manuscript.docx"
    work_dir = WORK / slug
    work_dir.mkdir(parents=True, exist_ok=True)
    target_xml = supplied_xml if write_back else work_dir / "article.xml"
    needs_conversion = docx.exists() and (
        force or not supplied_xml.exists() or docx.stat().st_mtime > supplied_xml.stat().st_mtime
    )
    engine = "JATS XML supplied"
    if needs_conversion:
        temporary_xml = work_dir / "article.generated.xml"
        if xsweet_url:
            try:
                xsweet_html = work_dir / "xsweet.html"
                xsweet_convert(docx, xsweet_html, xsweet_url)
                pandoc_to_jats(xsweet_html, "html", temporary_xml, work_dir / "media")
                engine = "XSweet + Pandoc"
            except LibPubError as exc:
                warnings.append(f"XSweet lỗi; đã dùng Pandoc dự phòng: {exc}")
                pandoc_to_jats(docx, "docx", temporary_xml, work_dir / "media")
                engine = "Pandoc fallback"
        else:
            warnings.append("Không có LIBPUB_XSWEET_URL; đã dùng Pandoc dự phòng.")
            pandoc_to_jats(docx, "docx", temporary_xml, work_dir / "media")
            engine = "Pandoc fallback"
        sync_generated_jats_metadata(temporary_xml, metadata)
        target_xml.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(temporary_xml, target_xml)
    elif supplied_xml.exists() and not write_back:
        shutil.copy2(supplied_xml, target_xml)
    elif not supplied_xml.exists():
        raise LibPubError(f"{article_dir} cần article.xml hoặc manuscript.docx.")
    warnings.extend(validate_article_xml(target_xml))
    return {
        "slug": slug,
        "engine": engine,
        "source": "manuscript.docx" if needs_conversion else "article.xml",
        "xml": str(target_xml.relative_to(ROOT)),
        "warnings": warnings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-back", action="store_true", help="Ghi article.xml sinh ra vào thư mục bài báo.")
    parser.add_argument("--force", action="store_true", help="Chuyển lại DOCX kể cả khi XML mới hơn.")
    args = parser.parse_args()
    xsweet_url = os.environ.get("LIBPUB_XSWEET_URL", "").strip()
    reports: list[dict[str, object]] = []
    errors: list[str] = []
    WORK.mkdir(parents=True, exist_ok=True)
    for article_dir in sorted(path for path in ARTICLES.iterdir() if path.is_dir() and not path.name.startswith(".")):
        try:
            report = prepare_article(article_dir, args.write_back, args.force, xsweet_url)
            reports.append(report)
            print(f"✓ {article_dir.name}: {report['engine']}")
            for warning in report["warnings"]:
                print(f"  ! {warning}")
        except LibPubError as exc:
            errors.append(str(exc))
            print(f"✗ {article_dir.name}: {exc}", file=sys.stderr)
    report_path = ROOT / ".libpub" / "preparation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps({"articles": reports, "errors": errors}, ensure_ascii=False, indent=2), encoding="utf-8")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

