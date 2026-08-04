<div align="center">
  <img src="assets/libpub-banner.svg" alt="LibPub — GitHub 原生预印本出版" width="100%">

**[Tiếng Việt](README.md) · [English](README.en.md) · [简体中文](README.zh-CN.md)**

# LibPub

**基于 GitHub 的无服务器预印本出版系统，并可自动同步 Zenodo DOI。**

[出版网站](https://xulytiengviet.github.io/LibPub) · [提交稿件](https://xulytiengviet.github.io/LibPub/#submit) · [Zenodo 设置](docs/ZENODO_SETUP.md) · [系统架构](docs/ARCHITECTURE.md)
</div>

## 系统功能

每篇论文由声明式元数据和 DOCX 或 JATS XML 源文件组成。GitHub Actions 自动完成：

1. 校验元数据、DOI 格式、ORCID 和源文件；
2. 通过 **XSweet → 语义 HTML → Pandoc JATS XML** 转换 DOCX（并提供明确记录的 Pandoc 回退方案）；
3. 生成学术 HTML、PDF、JATS XML、JSON-LD、引用元标签、Atom feed 和 sitemap；
4. 将静态 `output/` 部署至 GitHub Pages；
5. 创建不可变版本标签及带 PDF/XML/JSON 附件的 GitHub Release；
6. 由 Zenodo 归档 Release 并生成 DOI；
7. 将 DOI 和 Zenodo 记录网址回写论文元数据，再次部署 Pages。

整个系统不需要应用服务器、数据库或动态 CMS。

## 首次设置

1. 在 **Settings → Pages** 中将发布来源设为 **GitHub Actions**。
2. 在 **Settings → Actions → General** 中为 workflow 选择 **Read and write permissions**。
3. 打开 [Zenodo GitHub 设置](https://zenodo.org/account/settings/github/)，点击 **Sync now**，找到 `xulytiengviet/LibPub` 并启用其开关。请勿使用旧版的单仓库网址，该网址现在会返回 404。
4. 保持 `zenodo.mode` 为 `github-release`；默认模式无需 Zenodo token。

REST API 直传模式请参阅 [Zenodo 完整设置](docs/ZENODO_SETUP.md)。

## 提交稿件

可使用支持越南语、英语、中文的网页控制台，也可创建 pull request：

```text
articles/article-slug/
├── metadata.json
└── manuscript.docx      # 或 article.xml
```

Pull request 只运行只读校验。编辑审核通过后合并至 `main`，系统会自动出版并同步 DOI。

如需通过控制台直接发布，请点击 **创建正确权限的令牌**，资源所有者选择 `xulytiengviet`，选择 **Only select repositories → LibPub**，并授予 **Contents: Read and write**。粘贴后先点击 **检查令牌**。LibPub 会自动清除 `Bearer`/`token` 前缀、引号与空格，并验证用户、仓库和分支；`401` 会明确提示令牌无效、过期或已撤销，`403` 则提示权限不足。

最小元数据示例：

```json
{
  "schemaVersion": "1.0",
  "slug": "article-slug",
  "title": "完整的学术论文标题",
  "abstract": "摘要内容不得少于二十个字符。",
  "keywords": ["JATS XML", "预印本"],
  "language": "zh",
  "articleType": "research-article",
  "status": "preprint",
  "version": 1,
  "autoDoi": true,
  "doi": "",
  "publishedDate": "2026-08-04",
  "license": {"id": "CC-BY-4.0", "url": "https://creativecommons.org/licenses/by/4.0/"},
  "authors": [{"given": "名", "family": "姓", "orcid": "", "email": "", "corresponding": true, "affiliations": []}],
  "affiliations": []
}
```

需要自动创建 Zenodo DOI 时，将 `doi` 留空。如果已有合法的外部 DOI，请直接填写；LibPub 不会重复创建 Zenodo 记录。示例或草稿可设为 `autoDoi: false`，从而禁止创建 Release/DOI。

## 版本规则

默认标签为 `v<version>.0-<slug>`。论文内容发生科学性修订时，请保持 slug 不变、增加 `version`、更新日期和源文件，并在申请新版本 DOI 前有意删除旧的 `doi` 与 `zenodo` 区块。不得覆盖已发布的标签或 Release。

## 本地运行

```bash
python -m pip install -r requirements.txt
python scripts/prepare_sources.py --write-back
python -m unittest discover -s tests -v
python scripts/build.py --output output
python -m http.server 8000 --directory output
```

## 安全边界

控制台的直接发布功能仅适合仓库所有者或明确授权的贡献者。细粒度 token 只保存在浏览器标签页内存中，不会被持久化；公开投稿平台应关闭 `directPublishEnabled`，改用 pull request 或具有身份验证的后端。Secret 只能保存在 GitHub Actions。LibPub 自动打包并存档 DOI，但不能代替编辑审核、查重或长期保存政策。

代码采用 [MIT](LICENSE) 许可证；论文内容沿用各自 `metadata.json` 中声明的许可证。
