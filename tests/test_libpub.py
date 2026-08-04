from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from libpub import LibPubError, load_json, valid_orcid, validate_article_xml, validate_metadata  # noqa: E402


class MetadataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = load_json(ROOT / "articles" / "demo-libpub" / "metadata.json")

    def test_demo_metadata_is_valid(self) -> None:
        self.assertEqual(validate_metadata(self.metadata, "demo-libpub"), [])

    def test_invalid_doi_is_rejected(self) -> None:
        altered = json.loads(json.dumps(self.metadata))
        altered["doi"] = "doi:123"
        with self.assertRaises(LibPubError):
            validate_metadata(altered, "demo-libpub")

    def test_orcid_checksum(self) -> None:
        self.assertTrue(valid_orcid("https://orcid.org/0000-0002-1825-0097"))
        self.assertFalse(valid_orcid("https://orcid.org/0000-0002-1825-0098"))


class ArticleTests(unittest.TestCase):
    def test_demo_jats_is_valid(self) -> None:
        warnings = validate_article_xml(ROOT / "articles" / "demo-libpub" / "article.xml")
        self.assertEqual(warnings, [])

    def test_builds_static_preview(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "build.py"), "--output", str(output), "--skip-pdf"],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((output / "index.html").exists())
            self.assertTrue((output / "articles" / "demo-libpub" / "index.html").exists())
            records = json.loads((output / "articles.json").read_text(encoding="utf-8"))
            self.assertEqual(records[0]["slug"], "demo-libpub")


class SecurityTests(unittest.TestCase):
    def test_dashboard_does_not_embed_a_token(self) -> None:
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("github_pat_11", source)
        self.assertNotIn("ghp_", source)


if __name__ == "__main__":
    unittest.main()

