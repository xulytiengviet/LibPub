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
from zenodo import apply_doi, zenodo_metadata  # noqa: E402


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

    def test_auto_doi_must_be_boolean(self) -> None:
        altered = json.loads(json.dumps(self.metadata))
        altered["autoDoi"] = "false"
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
            self.assertTrue((output / "articles" / "demo-libpub" / "metadata.json").exists())
            records = json.loads((output / "articles.json").read_text(encoding="utf-8"))
            self.assertEqual(records[0]["slug"], "demo-libpub")
            self.assertIn("i18n.js", (output / "index.html").read_text(encoding="utf-8"))

    def test_docx_conversion_produces_standalone_jats(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "prepare_sources.py"), "--force"],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        generated = ROOT / ".libpub" / "work" / "geoplan-verifiable-geoworkflows-iccies2027" / "article.xml"
        self.assertTrue(generated.exists())
        source = generated.read_text(encoding="utf-8")
        self.assertIn("<article", source)
        body = source.split("<body>", 1)[1]
        self.assertNotIn("<bold>From Natural Language to Verifiable GeoWorkflows", body)
        self.assertNotIn("<bold>Abstract.</bold>", body)


class ZenodoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = load_json(ROOT / "articles" / "demo-libpub" / "metadata.json")

    def test_generates_article_specific_zenodo_metadata(self) -> None:
        result = zenodo_metadata(self.metadata, "xulytiengviet/LibPub", "v1.0-demo-libpub")
        self.assertEqual(result["language"], "vie")
        self.assertEqual(result["publication_type"], "article")
        self.assertEqual(result["creators"][0]["name"], "Ngo, Long")
        self.assertIn("v1.0-demo-libpub", result["related_identifiers"][0]["identifier"])

    def test_demo_article_opts_out_of_automatic_doi(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            plan = Path(directory) / "plan.json"
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "release_plan.py"), "--slug", "demo-libpub", "--output", str(plan)],
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(plan.read_text(encoding="utf-8")), [])

    def test_applies_doi_to_metadata_and_jats(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            article_dir = Path(directory) / "demo-libpub"
            article_dir.mkdir()
            metadata_path = article_dir / "metadata.json"
            xml_path = article_dir / "article.xml"
            metadata_path.write_text(json.dumps(self.metadata, ensure_ascii=False), encoding="utf-8")
            xml_path.write_bytes((ROOT / "articles" / "demo-libpub" / "article.xml").read_bytes())
            apply_doi(metadata_path, {
                "doi": "10.5281/zenodo.12345678",
                "conceptDoi": "10.5281/zenodo.12345677",
                "recordId": "12345678",
                "recordUrl": "https://zenodo.org/records/12345678",
                "source": "github-release",
                "tag": "v1.0-demo-libpub",
            })
            updated = load_json(metadata_path)
            self.assertEqual(updated["doi"], "10.5281/zenodo.12345678")
            self.assertEqual(updated["zenodo"]["recordId"], "12345678")
            self.assertIn(b'pub-id-type="doi">10.5281/zenodo.12345678', xml_path.read_bytes())


class SecurityTests(unittest.TestCase):
    def test_dashboard_does_not_embed_a_token(self) -> None:
        source = (ROOT / "index.html").read_text(encoding="utf-8")
        self.assertNotIn("github_pat_11", source)
        self.assertNotIn("ghp_", source)

    def test_github_auth_helpers(self) -> None:
        result = subprocess.run(
            ["node", str(ROOT / "tests" / "test_github_auth.js")],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_uses_current_zenodo_github_settings_url(self) -> None:
        legacy = "account/settings/github/repository/"
        config = load_json(ROOT / "publication.config.json")
        self.assertEqual(
            config["zenodo"]["repositorySettingsUrl"],
            "https://zenodo.org/account/settings/github/",
        )
        for path in [
            ROOT / "index.html",
            ROOT / "README.md",
            ROOT / "README.en.md",
            ROOT / "README.zh-CN.md",
            ROOT / "docs" / "ZENODO_SETUP.md",
        ]:
            self.assertNotIn(legacy, path.read_text(encoding="utf-8"), str(path))

    def test_publish_toolchain_tracks_generated_xml_and_builds_pdf(self) -> None:
        publish = (ROOT / ".github" / "workflows" / "publish.yml").read_text(encoding="utf-8")
        zenodo = (ROOT / ".github" / "workflows" / "zenodo-sync.yml").read_text(encoding="utf-8")
        dockerfile = (ROOT / "tools" / "xsweet" / "Dockerfile").read_text(encoding="utf-8")
        required_pdf_fonts = "texlive-fonts-recommended lmodern fonts-dejavu-core"
        self.assertIn(required_pdf_fonts, publish)
        self.assertIn(required_pdf_fonts, zenodo)
        self.assertIn("git status --porcelain -- 'articles/*/article.xml'", publish)
        self.assertIn("libz-dev libzip-dev", dockerfile)


if __name__ == "__main__":
    unittest.main()
