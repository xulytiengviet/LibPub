# DOI và quản lý phiên bản

## DOI được tạo khi nào?

Khi `metadata.json` để `doi` trống, `zenodo.enabled` và `zenodo.autoDoi` đều là `true`, một merge vào `main` sẽ tạo tag `v<version>.0-<slug>` và GitHub Release. Workflow tiếp theo lấy DOI Zenodo rồi ghi các trường sau về bài:

```json
{
  "doi": "10.5281/zenodo.12345678",
  "zenodo": {
    "doi": "10.5281/zenodo.12345678",
    "conceptDoi": "10.5281/zenodo.12345677",
    "recordId": "12345678",
    "recordUrl": "https://zenodo.org/records/12345678",
    "source": "github-release",
    "tag": "v1.0-ten-bai-bao",
    "syncedAt": "..."
  }
}
```

DOI xuất hiện trên dashboard, trang bài báo, citation meta và JSON-LD. DOI nhập tay không bị thay thế và sẽ làm LibPub bỏ qua auto-DOI cho bài đó.

## Quy tắc phiên bản bất biến

- Giữ nguyên `slug` để duy trì URL trang đích.
- Tăng `version` khi nội dung khoa học thay đổi.
- Cập nhật `publishedDate` và nguồn DOCX/XML.
- Trước khi xin DOI cho phiên bản mới, xóa có chủ đích `doi` và khối `zenodo` của phiên bản cũ; lịch sử Git vẫn giữ DOI cũ.
- Không xóa, di chuyển hoặc ghi đè tag/Release đã công bố.
- Nếu chỉ sửa lỗi website không thay đổi nội dung bài, không tăng `version`; release planner chỉ xem bài có thay đổi và bỏ qua tag đã đồng bộ.

## DOI phiên bản và DOI khái niệm

Zenodo thường trả DOI riêng cho bản ghi phiên bản và có thể trả `conceptDoi` nối các phiên bản. LibPub lưu cả hai nhưng dùng DOI phiên bản trong trường `doi`. Chính sách trích dẫn cuối cùng thuộc đơn vị xuất bản.

## Chạy lại khi Zenodo xử lý chậm

Vào **Actions → Zenodo DOI Sync → Run workflow**, nhập đúng `slug` và tag đã tạo. Workflow không ghi đè một DOI khác, vì vậy thao tác chạy lại an toàn theo cùng phiên bản.

## Rút lại

Đặt `status: "withdrawn"` và công bố thông báo rút lại minh bạch. Release planner không tạo DOI mới cho bài đã rút. Không tái sử dụng DOI hoặc tag của công trình đã rút.
