# DOI và quản lý phiên bản

## LibPub làm gì với DOI?

LibPub:

- kiểm tra mẫu cú pháp DOI;
- ghi DOI vào JATS XML sinh từ DOCX;
- thêm `citation_doi` và JSON-LD cho trang bài báo;
- tạo liên kết tới `https://doi.org/<doi>`.

LibPub không đăng ký DOI và không xác nhận DOI có tồn tại hay thuộc quyền của tác giả. Trách nhiệm này thuộc chủ repository và cơ quan đăng ký DOI.

## Khi chưa có DOI

Để `doi` là chuỗi rỗng. Bài báo vẫn có URL ổn định theo `baseUrl/articles/<slug>/` và lịch sử commit. Có thể thêm DOI ở phiên bản sau bằng một commit mới.

## Phiên bản

- Tăng `version` khi nội dung khoa học thay đổi.
- Giữ `slug` để duy trì URL trang đích.
- Cập nhật `publishedDate` cho phiên bản mới.
- Không ghi đè lịch sử Git hoặc xóa bản cũ khỏi lịch sử.
- Nếu cơ quan đăng ký cấp DOI riêng cho từng phiên bản, cập nhật DOI tương ứng; nếu dùng DOI khái niệm, tuân theo chính sách của cơ quan đó.

## Rút lại

Đặt `status: "withdrawn"` và công bố thông báo rút lại minh bạch. Không tái sử dụng DOI của bài đã rút cho một công trình khác.

