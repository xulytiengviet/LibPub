<div align="center">
  <img src="assets/libpub-banner.svg" alt="LibPub — GitHub-native preprint publishing" width="100%">

**[Tiếng Việt](README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md)**

# LibPub

**A GitHub-native, serverless preprint publisher with automated Zenodo DOI synchronization.**

[Publication site](https://xulytiengviet.github.io/LibPub) · [Submit a manuscript](https://xulytiengviet.github.io/LibPub/#submit) · [Zenodo setup](docs/ZENODO_SETUP.md) · [Architecture](docs/ARCHITECTURE.md)
</div>

## What it does

LibPub stores each paper as declarative metadata plus either DOCX or JATS XML. GitHub Actions then performs the complete publication path:

1. validate metadata, DOI syntax, ORCID and source files;
2. convert DOCX with **XSweet → semantic HTML → Pandoc JATS XML** (with a documented Pandoc fallback);
3. generate scholarly HTML, PDF, JATS XML, JSON-LD, citation meta, an Atom feed and a sitemap;
4. deploy the static `output/` directory to GitHub Pages;
5. create an immutable tag and GitHub Release with PDF/XML/JSON assets;
6. let Zenodo archive the release and mint a DOI;
7. write the DOI and Zenodo record URL back to the article and redeploy Pages.

No application server, database or CMS is required.

## One-time repository setup

1. In **Settings → Pages**, select **GitHub Actions** as the deployment source.
2. In **Settings → Actions → General**, give workflows **Read and write permissions**.
3. Open [Zenodo’s LibPub repository setting](https://zenodo.org/account/settings/github/repository/xulytiengviet/LibPub), connect GitHub and enable this repository.
4. Keep `zenodo.mode` set to `github-release`. This default mode needs no Zenodo token.

See [the complete Zenodo setup](docs/ZENODO_SETUP.md) for the optional direct REST API mode.

## Submit a manuscript

Use the trilingual dashboard or create a pull request containing:

```text
articles/article-slug/
├── metadata.json
└── manuscript.docx      # or article.xml
```

Pull requests run read-only validation. After editorial review, merge into `main`; publication and DOI synchronization then run automatically.

For direct dashboard publishing, use **Create the correct token**, select resource owner `xulytiengviet`, **Only select repositories → LibPub**, and **Contents: Read and write**. Paste it and click **Check token** before publishing. LibPub normalizes pasted `Bearer`/`token` prefixes, quotes and whitespace, then verifies the authenticated user, repository and branch. A `401` now reports an invalid, expired or revoked token separately from missing permissions (`403`).

Minimal metadata:

```json
{
  "schemaVersion": "1.0",
  "slug": "article-slug",
  "title": "A complete scholarly article title",
  "abstract": "The abstract must contain at least twenty characters.",
  "keywords": ["JATS XML", "preprint"],
  "language": "en",
  "articleType": "research-article",
  "status": "preprint",
  "version": 1,
  "autoDoi": true,
  "doi": "",
  "publishedDate": "2026-08-04",
  "license": {"id": "CC-BY-4.0", "url": "https://creativecommons.org/licenses/by/4.0/"},
  "authors": [{"given": "Given", "family": "Family", "orcid": "", "email": "", "corresponding": true, "affiliations": []}],
  "affiliations": []
}
```

Leave `doi` empty for automatic Zenodo DOI creation. If a valid external DOI already exists, enter it and LibPub will not create a duplicate Zenodo record. Set `autoDoi` to `false` for examples or drafts that must never create a Release/DOI.

## Versioning

The default tag is `v<version>.0-<slug>`. For a scientifically revised version, keep the slug, increment `version`, update the date/source, and intentionally clear the previous `doi` and `zenodo` block before requesting a new version DOI. Never overwrite a published tag or Release.

## Local development

```bash
python -m pip install -r requirements.txt
python scripts/prepare_sources.py --write-back
python -m unittest discover -s tests -v
python scripts/build.py --output output
python -m http.server 8000 --directory output
```

## Security boundaries

The dashboard’s direct publishing option is for repository owners or explicitly authorized contributors. A fine-grained token remains in tab memory and is not stored, but a public submission portal should disable `directPublishEnabled` and use pull requests or an authenticated backend. Secrets belong only in GitHub Actions. LibPub automates packaging and DOI deposit; it does not replace editorial review, plagiarism checks or preservation policy.

Code: [MIT](LICENSE). Article content retains the license declared by each `metadata.json`.
