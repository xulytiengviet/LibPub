(() => {
  "use strict";

  const $ = (selector, scope = document) => scope.querySelector(selector);
  const $$ = (selector, scope = document) => [...scope.querySelectorAll(selector)];
  const DEFAULT_CONFIG = {
    repository: "xulytiengviet/LibPub",
    defaultBranch: "main",
    baseUrl: "https://xulytiengviet.github.io/LibPub",
    directPublishEnabled: true,
    zenodo: {
      repositorySettingsUrl: "https://zenodo.org/account/settings/github/",
    },
  };
  const LICENSE_URLS = {
    "CC-BY-4.0": "https://creativecommons.org/licenses/by/4.0/",
    "CC-BY-SA-4.0": "https://creativecommons.org/licenses/by-sa/4.0/",
    "CC0-1.0": "https://creativecommons.org/publicdomain/zero/1.0/",
    ARR: "https://rightsstatements.org/page/InC/1.0/",
  };
  let config = DEFAULT_CONFIG;
  let articles = Array.isArray(window.LIBPUB_ARTICLES) ? window.LIBPUB_ARTICLES : [];
  const githubApi = window.LibPubGitHub;

  const tr = (key, fallback = "") => window.LibPubI18n?.translate(key, fallback) || fallback;
  const formatMessage = (key, values = {}, fallback = "") => Object.entries(values).reduce(
    (message, [name, value]) => message.replaceAll(`{${name}}`, String(value)),
    tr(key, fallback),
  );

  const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;",
  })[char]);

  function slugify(value) {
    return String(value)
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/đ/g, "d")
      .replace(/Đ/g, "D")
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/^-|-$/g, "")
      .slice(0, 100);
  }

  function validOrcid(uri) {
    const match = String(uri).match(/^https:\/\/orcid\.org\/(\d{4}-\d{4}-\d{4}-\d{3}[\dX])$/);
    if (!match) return false;
    const digits = match[1].replaceAll("-", "");
    let total = 0;
    for (const char of digits.slice(0, 15)) total = (total + Number(char)) * 2;
    const result = (12 - (total % 11)) % 11;
    return (result === 10 ? "X" : String(result)) === digits.at(-1);
  }

  async function loadConfig() {
    try {
      const response = await fetch("publication.config.json", { cache: "no-store" });
      if (response.ok) config = { ...DEFAULT_CONFIG, ...(await response.json()) };
    } catch (_) {
      config = DEFAULT_CONFIG;
    }
    const branch = $("#target-branch");
    if (branch && !branch.dataset.touched) branch.value = config.defaultBranch;
    const zenodoLink = $("#zenodo-settings-link");
    if (zenodoLink) {
      zenodoLink.href = config.zenodo?.repositorySettingsUrl || DEFAULT_CONFIG.zenodo.repositorySettingsUrl;
    }
  }

  async function loadArticles() {
    if (!articles.length) {
      try {
        const response = await fetch("articles.json", { cache: "no-store" });
        if (response.ok) articles = await response.json();
      } catch (_) {
        articles = [];
      }
    }
    updateStats();
    renderCatalog();
  }

  function updateStats() {
    const authorCount = new Set(articles.flatMap((item) => item.authors || [])).size;
    $("#stat-articles").textContent = String(articles.length);
    $("#stat-authors").textContent = String(authorCount);
  }

  function renderCatalog() {
    const grid = $("#catalog-grid");
    const empty = $("#catalog-empty");
    if (!grid) return;
    const query = ($("#catalog-search")?.value || "").trim().toLocaleLowerCase("vi");
    const language = $("#catalog-language")?.value || "";
    const filtered = articles.filter((article) => {
      const haystack = [article.title, article.abstract, ...(article.authors || []), ...(article.keywords || [])]
        .join(" ").toLocaleLowerCase("vi");
      return (!query || haystack.includes(query)) && (!language || article.language === language);
    });
    grid.innerHTML = filtered.map((article) => {
      const doi = article.doi
        ? `<a href="${escapeHtml(article.doiUrl)}" target="_blank" rel="noopener">${escapeHtml(article.doi)}</a>`
        : `<span>${escapeHtml(tr("catalog.noDoi", "Đang chờ DOI"))}</span>`;
      return `<article class="publication-card">
        <div class="card-meta"><span>${escapeHtml(article.articleType || "preprint")}</span><span>v${escapeHtml(article.version || 1)} · ${escapeHtml(article.language || "")}</span></div>
        <h3><a href="${escapeHtml(article.url)}">${escapeHtml(article.title)}</a></h3>
        <div class="authors">${escapeHtml((article.authors || []).join(", "))}</div>
        <p class="abstract">${escapeHtml(article.abstract || "")}</p>
        <div class="card-footer">${doi}<a href="${escapeHtml(article.url)}">${escapeHtml(tr("catalog.read", "Đọc toàn văn →"))}</a></div>
      </article>`;
    }).join("");
    empty.hidden = filtered.length > 0;
    if (!articles.length) {
      empty.hidden = false;
      empty.textContent = tr("catalog.empty", "Kho preprint sẽ xuất hiện sau lần build đầu tiên.");
    } else {
      empty.textContent = tr("catalog.noMatch", "Chưa tìm thấy bài báo phù hợp.");
    }
  }

  function metadataFromForm(form) {
    const data = new FormData(form);
    const affiliations = [];
    const affiliationName = String(data.get("affiliation") || "").trim();
    const affiliationId = affiliationName ? "aff1" : "";
    if (affiliationId) affiliations.push({ id: affiliationId, name: affiliationName, city: "", country: "Vietnam" });
    const authors = [{
      given: String(data.get("given") || "").trim(),
      family: String(data.get("family") || "").trim(),
      orcid: String(data.get("orcid") || "").trim(),
      email: String(data.get("email") || "").trim(),
      corresponding: true,
      affiliations: affiliationId ? [affiliationId] : [],
    }];
    $$("[data-coauthor]", form).forEach((row, index) => {
      const number = index + 2;
      const coAffiliation = $("[data-field='affiliation']", row).value.trim();
      const coAffiliationId = coAffiliation ? `aff${number}` : "";
      if (coAffiliationId) affiliations.push({ id: coAffiliationId, name: coAffiliation, city: "", country: "Vietnam" });
      authors.push({
        given: $("[data-field='given']", row).value.trim(),
        family: $("[data-field='family']", row).value.trim(),
        orcid: $("[data-field='orcid']", row).value.trim(),
        email: $("[data-field='email']", row).value.trim(),
        corresponding: false,
        affiliations: coAffiliationId ? [coAffiliationId] : [],
      });
    });
    return {
      schemaVersion: "1.0",
      slug: String(data.get("slug") || "").trim(),
      title: String(data.get("title") || "").trim(),
      subtitle: "",
      abstract: String(data.get("abstract") || "").trim(),
      keywords: String(data.get("keywords") || "").split(";").map((item) => item.trim()).filter(Boolean),
      language: String(data.get("language") || "vi"),
      articleType: String(data.get("articleType") || "research-article"),
      status: String(data.get("status") || "preprint"),
      version: Number(data.get("version") || 1),
      autoDoi: true,
      doi: String(data.get("doi") || "").trim(),
      publishedDate: String(data.get("publishedDate") || ""),
      license: {
        id: String(data.get("license") || "CC-BY-4.0"),
        url: LICENSE_URLS[String(data.get("license") || "CC-BY-4.0")],
      },
      authors,
      affiliations,
      funding: "",
      conflictOfInterest: "",
      dataAvailability: "",
    };
  }

  function validateSubmission(metadata, file) {
    if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(metadata.slug)) throw new Error(tr("error.slug"));
    if (metadata.title.length < 10) throw new Error(tr("error.title"));
    if (metadata.abstract.length < 20) throw new Error(tr("error.abstract"));
    if (!metadata.keywords.length) throw new Error(tr("error.keywords"));
    if (metadata.doi && !/^10\.\d{4,9}\/[-._;()/:A-Za-z0-9]+$/.test(metadata.doi)) throw new Error(tr("error.doi"));
    if (!Number.isInteger(metadata.version) || metadata.version < 1) throw new Error(tr("error.version"));
    metadata.authors.forEach((author, index) => {
      if (!author.given || !author.family) throw new Error(formatMessage("error.author", { n: index + 1 }));
      if (author.orcid && !validOrcid(author.orcid)) throw new Error(formatMessage("error.orcid", { n: index + 1 }));
    });
    if (!file) throw new Error(tr("error.noFile"));
    const lower = file.name.toLowerCase();
    if (!lower.endsWith(".docx") && !lower.endsWith(".xml")) throw new Error(tr("error.fileType"));
    if (file.size > 25 * 1024 * 1024) throw new Error(tr("error.fileSize"));
  }

  function setStatus(message, kind = "info", markup = false) {
    const status = $("#form-status");
    status.hidden = false;
    status.className = `form-status ${kind}`;
    if (markup) status.innerHTML = message;
    else status.textContent = message;
  }

  function githubErrorMessage(error) {
    if (!(error instanceof githubApi.GitHubApiError)) return error?.message || tr("error.unknown");
    const values = { repository: config.repository, detail: error.detail || "", status: error.status };
    let message;
    if (error.status === 0) message = tr("error.token");
    else if (error.status === -1) message = tr("error.githubNetwork");
    else if (error.status === 401) message = tr("error.github401");
    else if (error.status === 403) message = tr("error.github403");
    else if (error.status === 404) message = formatMessage("error.github404", values);
    else if (error.status === 409) message = tr("error.github409");
    else if (error.status === 410) message = tr("error.github410");
    else if (error.status === 422) message = tr("error.github422");
    else message = formatMessage("error.githubGeneric", values);
    if (error.acceptedPermissions) {
      message += ` ${formatMessage("error.githubPermissions", { permissions: error.acceptedPermissions })}`;
    }
    return message;
  }

  function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    const chunk = 0x8000;
    let binary = "";
    for (let offset = 0; offset < bytes.length; offset += chunk) {
      binary += String.fromCharCode(...bytes.subarray(offset, Math.min(offset + chunk, bytes.length)));
    }
    return btoa(binary);
  }

  async function pathExists(repository, branch, slug, token) {
    const path = `/repos/${repository}/contents/articles/${encodeURIComponent(slug)}/metadata.json?ref=${encodeURIComponent(branch)}`;
    try {
      await githubApi.request(path, token);
      return true;
    } catch (error) {
      if (error instanceof githubApi.GitHubApiError && error.status === 404) return false;
      throw error;
    }
  }

  async function publishAtomic({ metadata, file, token, branch }) {
    const repository = config.repository;
    const branchRef = await githubApi.request(`/repos/${repository}/git/ref/heads/${encodeURIComponent(branch)}`, token);
    const parentSha = branchRef.object.sha;
    const parentCommit = await githubApi.request(`/repos/${repository}/git/commits/${parentSha}`, token);
    const metadataText = `${JSON.stringify(metadata, null, 2)}\n`;
    const manuscriptBase64 = arrayBufferToBase64(await file.arrayBuffer());
    const [metadataBlob, manuscriptBlob] = await Promise.all([
      githubApi.request(`/repos/${repository}/git/blobs`, token, { method: "POST", body: JSON.stringify({ content: metadataText, encoding: "utf-8" }) }),
      githubApi.request(`/repos/${repository}/git/blobs`, token, { method: "POST", body: JSON.stringify({ content: manuscriptBase64, encoding: "base64" }) }),
    ]);
    const filename = file.name.toLowerCase().endsWith(".xml") ? "article.xml" : "manuscript.docx";
    const tree = await githubApi.request(`/repos/${repository}/git/trees`, token, {
      method: "POST",
      body: JSON.stringify({
        base_tree: parentCommit.tree.sha,
        tree: [
          { path: `articles/${metadata.slug}/metadata.json`, mode: "100644", type: "blob", sha: metadataBlob.sha },
          { path: `articles/${metadata.slug}/${filename}`, mode: "100644", type: "blob", sha: manuscriptBlob.sha },
        ],
      }),
    });
    const commit = await githubApi.request(`/repos/${repository}/git/commits`, token, {
      method: "POST",
      body: JSON.stringify({
        message: `publish: ${metadata.slug} v${metadata.version}`,
        tree: tree.sha,
        parents: [parentSha],
      }),
    });
    await githubApi.request(`/repos/${repository}/git/refs/heads/${encodeURIComponent(branch)}`, token, {
      method: "PATCH",
      body: JSON.stringify({ sha: commit.sha, force: false }),
    });
    return commit;
  }

  function downloadMetadata(metadata) {
    const blob = new Blob([`${JSON.stringify(metadata, null, 2)}\n`], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "metadata.json";
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function bindForm() {
    const form = $("#submission-form");
    if (!form) return;
    const title = $("#title");
    const slug = $("#slug");
    let slugEdited = false;
    slug.addEventListener("input", () => { slugEdited = true; });
    title.addEventListener("input", () => { if (!slugEdited) slug.value = slugify(title.value); });
    $("#abstract").addEventListener("input", (event) => { $("#abstract-count").textContent = String(event.target.value.length); });
    $("#published-date").value = new Date().toISOString().slice(0, 10);
    $("#target-branch").addEventListener("input", (event) => { event.target.dataset.touched = "true"; });
    $("#github-token").addEventListener("blur", (event) => {
      event.target.value = githubApi.normalizeToken(event.target.value);
    });
    $("#manuscript").addEventListener("change", (event) => {
      const file = event.target.files[0];
      $("#file-label").textContent = file ? `${file.name} · ${(file.size / 1024 / 1024).toFixed(2)} MB` : tr("form.file", "Chọn manuscript.docx hoặc article.xml");
    });
    let authorNumber = 1;
    $("#add-author").addEventListener("click", () => {
      authorNumber += 1;
      const row = document.createElement("div");
      row.className = "coauthor";
      row.dataset.coauthor = String(authorNumber);
      row.innerHTML = `<h4><span data-i18n="coauthor.title">${escapeHtml(tr("coauthor.title", "Đồng tác giả"))}</span> ${authorNumber}</h4><button class="remove-author" type="button" aria-label="${escapeHtml(tr("coauthor.remove", "Xóa"))} ${authorNumber}" data-i18n="coauthor.remove">${escapeHtml(tr("coauthor.remove", "Xóa"))}</button>
        <div class="field"><label for="co-given-${authorNumber}"><span data-i18n="form.given">${escapeHtml(tr("form.given", "Tên"))}</span> <b>*</b></label><input id="co-given-${authorNumber}" data-field="given" type="text" required></div>
        <div class="field"><label for="co-family-${authorNumber}"><span data-i18n="form.family">${escapeHtml(tr("form.family", "Họ"))}</span> <b>*</b></label><input id="co-family-${authorNumber}" data-field="family" type="text" required></div>
        <div class="field"><label for="co-orcid-${authorNumber}">ORCID</label><input id="co-orcid-${authorNumber}" data-field="orcid" type="url" placeholder="https://orcid.org/…"></div>
        <div class="field"><label for="co-email-${authorNumber}" data-i18n="form.email">${escapeHtml(tr("form.email", "Email"))}</label><input id="co-email-${authorNumber}" data-field="email" type="email"></div>
        <div class="field span-2"><label for="co-affiliation-${authorNumber}" data-i18n="form.affiliation">${escapeHtml(tr("form.affiliation", "Cơ quan công tác"))}</label><input id="co-affiliation-${authorNumber}" data-field="affiliation" type="text"></div>`;
      $("#coauthor-list").append(row);
      $(".remove-author", row).addEventListener("click", () => row.remove());
    });
    $("#download-metadata").addEventListener("click", () => {
      const metadata = metadataFromForm(form);
      try {
        if (!metadata.slug || !metadata.title) throw new Error(tr("error.formMeta"));
        downloadMetadata(metadata);
        setStatus(tr("status.metadata"), "success");
      } catch (error) {
        setStatus(error.message, "error");
      }
    });
    $("#check-github-token").addEventListener("click", async (event) => {
      const checkButton = event.currentTarget;
      const tokenInput = $("#github-token");
      const token = githubApi.normalizeToken(tokenInput.value);
      const branch = $("#target-branch").value.trim();
      tokenInput.value = token;
      try {
        if (!token) throw new githubApi.GitHubApiError(0, "TOKEN_REQUIRED");
        checkButton.disabled = true;
        setStatus(tr("status.verifyingToken"), "info");
        const verified = await githubApi.verify({ repository: config.repository, branch, token });
        if (verified.canPush === false) throw new githubApi.GitHubApiError(403, "NO_PUSH_PERMISSION");
        setStatus(formatMessage("status.tokenValid", verified), "success");
      } catch (error) {
        setStatus(githubErrorMessage(error), "error");
      } finally {
        checkButton.disabled = false;
      }
    });
    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!form.reportValidity()) return;
      const metadata = metadataFromForm(form);
      const file = $("#manuscript").files[0];
      const tokenInput = $("#github-token");
      const token = githubApi.normalizeToken(tokenInput.value);
      const branch = $("#target-branch").value.trim();
      const button = $("#submit-button");
      try {
        validateSubmission(metadata, file);
        if (!config.directPublishEnabled) throw new Error(tr("error.disabled"));
        if (!token) throw new Error(tr("error.token"));
        tokenInput.value = token;
        button.disabled = true;
        setStatus(tr("status.verifyingToken"), "info");
        const verified = await githubApi.verify({ repository: config.repository, branch, token });
        if (verified.canPush === false) throw new githubApi.GitHubApiError(403, "NO_PUSH_PERMISSION");
        setStatus(tr("status.preparing"), "info");
        const exists = await pathExists(config.repository, branch, metadata.slug, token);
        if (exists && !window.confirm(formatMessage("confirm.exists", { slug: metadata.slug }))) {
          setStatus(tr("status.cancelled"), "info");
          return;
        }
        setStatus(tr("status.uploading"), "info");
        const commit = await publishAtomic({ metadata, file, token, branch });
        tokenInput.value = "";
        const repoUrl = `https://github.com/${config.repository}`;
        const commitLink = `<a href="${repoUrl}/commit/${commit.sha}" target="_blank" rel="noopener">${escapeHtml(commit.sha.slice(0, 7))}</a>`;
        const actionsLink = `<a href="${repoUrl}/actions" target="_blank" rel="noopener">GitHub Actions</a>`;
        setStatus(formatMessage("publish.success", { commit: commitLink, actions: actionsLink }), "success", true);
      } catch (error) {
        setStatus(githubErrorMessage(error), "error");
      } finally {
        button.disabled = false;
      }
    });
  }

  function bindTheme() {
    const toggle = $("#theme-toggle");
    const preferred = localStorage.getItem("libpub-theme");
    if (preferred) document.documentElement.dataset.theme = preferred;
    toggle?.addEventListener("click", () => {
      const next = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
      document.documentElement.dataset.theme = next;
      localStorage.setItem("libpub-theme", next);
    });
  }

  function bindLanguage() {
    const browserLanguage = String(navigator.language || "vi").toLowerCase();
    const detected = browserLanguage.startsWith("zh") ? "zh" : browserLanguage.startsWith("en") ? "en" : "vi";
    const selected = localStorage.getItem("libpub-language") || detected;
    window.LibPubI18n?.apply(selected);
    $("#ui-language")?.addEventListener("change", (event) => window.LibPubI18n?.apply(event.target.value));
    document.addEventListener("libpub:language", renderCatalog);
  }

  async function init() {
    bindTheme();
    bindLanguage();
    bindForm();
    $("#catalog-search")?.addEventListener("input", renderCatalog);
    $("#catalog-language")?.addEventListener("change", renderCatalog);
    await loadConfig();
    await loadArticles();
  }

  init();
})();
