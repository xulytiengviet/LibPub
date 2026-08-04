(() => {
  "use strict";

  const API_VERSION = "2026-03-10";

  class GitHubApiError extends Error {
    constructor(status, detail, options = {}) {
      super(detail || `GitHub API HTTP ${status}`);
      this.name = "GitHubApiError";
      this.status = status;
      this.detail = detail || "";
      this.documentationUrl = options.documentationUrl || "";
      this.acceptedPermissions = options.acceptedPermissions || "";
    }
  }

  function normalizeToken(value) {
    let token = String(value || "")
      .replace(/[\u200B-\u200D\uFEFF]/g, "")
      .trim();
    if ((token.startsWith('"') && token.endsWith('"')) || (token.startsWith("'") && token.endsWith("'"))) {
      token = token.slice(1, -1).trim();
    }
    return token.replace(/^(?:Bearer|token)\s+/i, "").replace(/\s+/g, "");
  }

  function tokenType(token) {
    const normalized = normalizeToken(token);
    if (normalized.startsWith("github_pat_")) return "fine-grained";
    if (/^gh[pousr]_/.test(normalized)) return "classic-or-app";
    return normalized ? "unknown" : "empty";
  }

  async function request(path, token, options = {}) {
    const normalized = normalizeToken(token);
    if (!normalized) throw new GitHubApiError(0, "TOKEN_REQUIRED");
    const headers = {
      Accept: "application/vnd.github+json",
      Authorization: `Bearer ${normalized}`,
      "X-GitHub-Api-Version": API_VERSION,
      ...(options.headers || {}),
    };
    if (options.body && !headers["Content-Type"]) headers["Content-Type"] = "application/json";
    let response;
    try {
      response = await fetch(`https://api.github.com${path}`, { ...options, headers });
    } catch (error) {
      const wrapped = new GitHubApiError(-1, error?.message || "NETWORK_ERROR");
      wrapped.cause = error;
      throw wrapped;
    }
    if (!response.ok) {
      let payload = {};
      try { payload = await response.json(); } catch (_) { /* response has no JSON body */ }
      const detail = payload.message || `${response.status} ${response.statusText}`;
      throw new GitHubApiError(response.status, detail, {
        documentationUrl: payload.documentation_url,
        acceptedPermissions: response.headers.get("x-accepted-github-permissions"),
      });
    }
    if (response.status === 204) return {};
    return response.json();
  }

  async function verify({ repository, branch, token }) {
    const normalized = normalizeToken(token);
    const user = await request("/user", normalized);
    const repo = await request(`/repos/${repository}`, normalized);
    const ref = await request(`/repos/${repository}/git/ref/heads/${encodeURIComponent(branch)}`, normalized);
    return {
      login: user.login,
      repository: repo.full_name,
      branch,
      sha: ref.object?.sha || "",
      canPush: repo.permissions ? Boolean(repo.permissions.push) : null,
      tokenType: tokenType(normalized),
    };
  }

  window.LibPubGitHub = { API_VERSION, GitHubApiError, normalizeToken, tokenType, request, verify };
})();
