"use strict";

const assert = require("node:assert/strict");
global.window = {};
require("../assets/github-auth.js");

const api = window.LibPubGitHub;

assert.equal(api.normalizeToken(" Bearer github_pat_example \n"), "github_pat_example");
assert.equal(api.normalizeToken("'token ghp_example'"), "ghp_example");
assert.equal(api.normalizeToken('"github_pat_quoted"'), "github_pat_quoted");
assert.equal(api.normalizeToken("github_pat_\u200Bhidden"), "github_pat_hidden");
assert.equal(api.tokenType("github_pat_example"), "fine-grained");

global.fetch = async () => ({
  ok: false,
  status: 401,
  statusText: "Unauthorized",
  headers: { get: () => "contents=write" },
  json: async () => ({ message: "Bad credentials", documentation_url: "https://docs.github.com/rest" }),
});

(async () => {
  await assert.rejects(
    api.request("/user", "github_pat_invalid"),
    (error) => error instanceof api.GitHubApiError
      && error.status === 401
      && error.detail === "Bad credentials"
      && error.acceptedPermissions === "contents=write",
  );
  process.stdout.write("GitHub auth tests passed\n");
})().catch((error) => {
  process.stderr.write(`${error.stack}\n`);
  process.exitCode = 1;
});
