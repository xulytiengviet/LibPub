# Zenodo automatic DOI setup · Thiết lập DOI tự động · Zenodo 自动 DOI 设置

## Tiếng Việt

### Chế độ khuyến nghị: GitHub Release

1. Đăng nhập Zenodo và trong menu hồ sơ chọn **Linked accounts** để kết nối tài khoản GitHub nếu chưa kết nối.
2. Mở `https://zenodo.org/account/settings/github/`, bấm **Sync now**, tìm **xulytiengviet/LibPub** và bật công tắc repository. URL cũ có thêm `/repository/xulytiengviet/LibPub` không còn hợp lệ và trả về 404.
3. Trong GitHub, đặt **Settings → Actions → General → Workflow permissions** thành **Read and write permissions**.
4. Đặt **Settings → Pages → Source** thành **GitHub Actions**.
5. Giữ cấu hình:

```json
"zenodo": {
  "enabled": true,
  "autoDoi": true,
  "mode": "github-release",
  "apiUrl": "https://zenodo.org",
  "pollAttempts": 40,
  "pollIntervalSeconds": 15
}
```

Khi bài có `doi: ""` được merge, `publish.yml` tạo tag `v<version>.0-<slug>` và Release. Commit của tag chứa `.zenodo.json` riêng cho bài; Zenodo lấy metadata này, tạo bản ghi và DOI. `zenodo-sync.yml` tra bản ghi qua API công khai, ghi DOI về `articles/<slug>/metadata.json` rồi deploy lại Pages.

Zenodo xử lý bất đồng bộ, nên DOI không nhất thiết xuất hiện ngay trong cùng giây. Nếu job hết thời gian chờ, chạy lại **Actions → Zenodo DOI Sync** với slug/tag đã có; không tạo Release mới.

### Chế độ tùy chọn: Zenodo REST API

Chế độ này tải trực tiếp PDF, XML và JSON lên Zenodo:

1. Tạo Zenodo access token có quyền deposit/write.
2. Lưu token dưới tên GitHub Actions secret `ZENODO_ACCESS_TOKEN`.
3. Đổi `zenodo.mode` thành `api`.
4. **Tắt repository trong Zenodo GitHub integration**, nếu không một Release có thể tạo hai bản ghi.

Không đặt token trong `publication.config.json`, dashboard, commit hoặc Pages artifact. Có thể dùng `https://sandbox.zenodo.org` để thử nghiệm bằng token Sandbox tương ứng.

## English

### Recommended mode: GitHub Release

Sign in to Zenodo, connect GitHub under **Linked accounts**, open `https://zenodo.org/account/settings/github/`, click **Sync now**, and enable **xulytiengviet/LibPub**. The legacy per-repository URL is no longer valid. Grant GitHub Actions read/write workflow permission and select GitHub Actions as the Pages source. Keep `zenodo.mode` as `github-release`; no Zenodo secret is needed.

For an article with an empty `doi`, `publish.yml` creates `v<version>.0-<slug>` and a GitHub Release. The tagged archive contains article-specific `.zenodo.json` metadata. Zenodo archives it asynchronously; `zenodo-sync.yml` polls the public Records API, writes the DOI/record URL into article metadata and redeploys Pages. If polling times out, rerun **Zenodo DOI Sync** with the existing slug and tag.

For direct upload, create `ZENODO_ACCESS_TOKEN`, set mode to `api`, and disable the repository in Zenodo’s GitHub integration to prevent duplicate records. Test against Zenodo Sandbox before production.

## 简体中文

### 推荐模式：GitHub Release

登录 Zenodo，在 **Linked accounts** 中连接 GitHub，然后打开 `https://zenodo.org/account/settings/github/`，点击 **Sync now** 并启用 **xulytiengviet/LibPub**。旧版单仓库网址已失效。同时允许 GitHub Actions 读写仓库，并将 Pages 发布来源设为 GitHub Actions。保持 `zenodo.mode` 为 `github-release`，无需配置 Zenodo secret。

当 `doi` 为空的论文合并后，`publish.yml` 会创建 `v<version>.0-<slug>` 标签与 GitHub Release。标签归档中包含该论文专用的 `.zenodo.json`。Zenodo 异步归档后，`zenodo-sync.yml` 轮询公开 Records API，把 DOI 和记录网址回写元数据并重新部署 Pages。如果等待超时，可使用相同 slug 和 tag 重新运行 **Zenodo DOI Sync**，无需创建新 Release。

如需通过 REST API 直接上传 PDF/XML/JSON，请创建 secret `ZENODO_ACCESS_TOKEN`，将模式改为 `api`，并关闭 Zenodo GitHub integration 中的该仓库，以免生成重复记录。建议先在 Zenodo Sandbox 测试。

## Operational checklist / Danh sách kiểm tra / 运维检查

- `metadata.version` was incremented for a scientific revision.
- `doi` and `zenodo` are empty only when requesting a new DOI.
- The target tag and Release do not already exist.
- `ZENODO_ACCESS_TOKEN` is present only for `api` mode.
- Only one ingestion mode is enabled.
- A failed sync is rerun against the existing tag; the published tag is never overwritten.
