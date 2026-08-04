#!/usr/bin/env python3
"""Calculate which changed articles need a versioned GitHub/Zenodo release."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from libpub import LibPubError, load_json, validate_metadata


ROOT = Path(__file__).resolve().parents[1]
ARTICLES = ROOT / "articles"
ZERO_SHA = "0" * 40


def git_changed_paths(before: str, after: str) -> list[str]:
    if not before or before == ZERO_SHA:
        return [str(path.relative_to(ROOT)) for path in ARTICLES.glob("*/metadata.json")]
    result = subprocess.run(
        ["git", "diff", "--name-only", before, after, "--", "articles"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", default="")
    parser.add_argument("--after", default="HEAD")
    parser.add_argument("--slug", default="", help="Chỉ lập kế hoạch cho một bài (workflow thủ công).")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    config = load_json(ROOT / "publication.config.json")
    zenodo_config = config.get("zenodo", {})
    if not zenodo_config.get("enabled", False) or not zenodo_config.get("autoDoi", False):
        plans: list[dict[str, object]] = []
    else:
        if args.slug:
            slugs = {args.slug}
        else:
            slugs = {
                Path(path).parts[1]
                for path in git_changed_paths(args.before, args.after)
                if len(Path(path).parts) >= 3 and Path(path).parts[0] == "articles"
            }
        plans = []
        for slug in sorted(slugs):
            metadata_path = ARTICLES / slug / "metadata.json"
            if not metadata_path.exists():
                continue
            metadata = load_json(metadata_path)
            validate_metadata(metadata, slug)
            if metadata.get("status") == "withdrawn":
                print(f"! {slug}: withdrawn, không tạo DOI mới.", file=sys.stderr)
                continue
            if metadata.get("autoDoi", True) is False:
                print(f"! {slug}: autoDoi=false, bỏ qua release/DOI tự động.", file=sys.stderr)
                continue
            zenodo = metadata.get("zenodo") or {}
            tag = f"v{metadata['version']}.0-{slug}"
            if metadata.get("doi") and not zenodo:
                print(f"! {slug}: đã có DOI bên ngoài; bỏ qua Zenodo auto-DOI.", file=sys.stderr)
                continue
            if zenodo.get("tag") == tag and zenodo.get("doi"):
                print(f"! {slug}: DOI của {tag} đã đồng bộ.", file=sys.stderr)
                continue
            plans.append({
                "slug": slug,
                "tag": tag,
                "version": metadata["version"],
                "title": metadata["title"],
                "metadata": str(metadata_path.relative_to(ROOT)),
            })
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(plans, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(plans, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (LibPubError, subprocess.CalledProcessError) as exc:
        print(f"Lỗi lập kế hoạch release: {exc}", file=sys.stderr)
        raise SystemExit(1)
