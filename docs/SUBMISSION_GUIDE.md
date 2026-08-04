# Hướng dẫn gửi bản thảo lên LibPub

## Trước khi gửi

Tác giả cần chuẩn bị:

1. bản thảo `manuscript.docx` hoặc JATS XML tên `article.xml`;
2. tiêu đề, tóm tắt, từ khóa và danh sách tác giả;
3. ORCID đầy đủ dạng `https://orcid.org/0000-0000-0000-0000` nếu có;
4. DOI đã được cấp nếu muốn dùng DOI ngoài; để trống nếu muốn Zenodo tạo tự động;
5. giấy phép nội dung và xác nhận quyền công bố.

Không tải lên dữ liệu nhạy cảm, phản biện mật, chữ ký số riêng, token, khóa API hoặc thông tin cá nhân không cần thiết.

## Cách 1: dùng dashboard

1. Mở trang LibPub và đi tới **Gửi bản thảo**.
2. Nhập tiêu đề; dashboard tự tạo `slug`. Có thể sửa `slug` trước khi gửi.
3. Nhập DOI nếu DOI ngoài đã được cấp. Để trống để yêu cầu DOI Zenodo sau khi merge.
4. Nhập tóm tắt và các từ khóa, phân cách từ khóa bằng dấu chấm phẩy.
5. Khai báo tác giả chính, ORCID và cơ quan công tác.
6. Chọn DOCX hoặc XML, tối đa 25 MB.
7. Tạo fine-grained personal access token cho riêng repository:
   - dùng liên kết **Tạo token đúng quyền** ngay dưới ô token;
   - Resource owner: `xulytiengviet`;
   - Repository access: **Only select repositories → LibPub**;
   - Repository permissions: **Contents → Read and write**;
   - thời hạn: ngắn nhất phù hợp.
8. Dán token vào ô xác thực, bấm **Kiểm tra token**, sau đó bấm **Submit & Publish**.
9. Mở liên kết commit và GitHub Actions trong thông báo thành công.
10. Thu hồi token sau khi không còn sử dụng.

Dashboard tạo blob cho metadata và bản thảo, tạo tree, commit rồi cập nhật branch bằng thao tác fast-forward. Vì hai tệp nằm trong cùng một commit, workflow không quan sát trạng thái dở dang chỉ có metadata hoặc chỉ có bản thảo.

## Khắc phục lỗi xác thực GitHub

| Mã lỗi | Nguyên nhân thường gặp | Cách xử lý |
|---|---|---|
| `401 Bad credentials` | Token sai, hết hạn, bị thu hồi; hoặc dán cả tiền tố `Bearer`/`token` | Tạo token mới bằng liên kết trên dashboard. LibPub tự loại bỏ tiền tố, dấu nháy, ký tự ẩn và khoảng trắng khi dán. |
| `403 Forbidden` | Token thiếu `Contents: Read and write`, đang chờ phê duyệt hoặc tài khoản không có quyền push | Chọn đúng resource owner/repository/quyền; kiểm tra trạng thái token trên GitHub. |
| `404 Not Found` | Token không được cấp cho `xulytiengviet/LibPub` hoặc tên nhánh sai | Chọn `Only select repositories → LibPub` và kiểm tra nhánh. |
| `422 Validation failed` | Nhánh được bảo vệ hoặc ref không còn fast-forward | Gửi qua pull request hoặc tải lại trang và thử trên nhánh được phép. |

LibPub xác minh lần lượt tài khoản GitHub, repository và branch trước khi tải tệp. Token chỉ tồn tại trong giá trị ô nhập của tab hiện tại; không ghi vào localStorage, cookie, URL, log hoặc metadata.

## Cách 2: dùng giao diện GitHub hoặc Git

Sao chép thư mục `articles/demo-libpub`, đổi tên thư mục và chỉnh `metadata.json`. Xóa nguồn mẫu, sau đó thêm một trong hai tệp:

- `article.xml`, hoặc
- `manuscript.docx`.

Tên thư mục phải khớp chính xác `metadata.slug`.

## Theo dõi kết quả

Trong tab **Actions**, workflow trải qua các giai đoạn:

1. checkout và cài toolchain;
2. khởi động XSweet nếu có DOCX;
3. chuyển đổi/kiểm tra JATS;
4. commit XML sinh ra nếu cần;
5. chạy unit test;
6. dựng HTML/PDF/index/feed/sitemap vào `output/`;
7. tạo tag và GitHub Release kèm PDF/XML/JSON;
8. kích hoạt Zenodo, đồng bộ DOI về metadata;
9. deploy/redeploy GitHub Pages với DOI.

Nếu pipeline thất bại, mở job lỗi và đọc dòng bắt đầu bằng `Lỗi build`, `✗` hoặc `::warning::`.

## Sửa và công bố phiên bản mới

Giữ nguyên `slug`, tăng `version`, cập nhật `publishedDate` và thay nội dung nguồn. Nếu muốn Zenodo cấp DOI phiên bản mới, xóa có chủ đích `doi` và khối `zenodo` cũ trong commit mới. DOI cũ vẫn được bảo toàn trong lịch sử Git và Release. Không ghi đè tag đã phát hành.

## Rút lại preprint

Đặt `status` thành `withdrawn`, tăng `version`, thay abstract bằng thông báo lý do ở mức phù hợp và giữ trang cũ có dấu rút lại. Không xóa lịch sử Git nếu mục tiêu là duy trì dấu vết học thuật.
