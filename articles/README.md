# Cấu trúc thư mục bài báo

Mỗi bài báo là một thư mục có tên trùng với `metadata.slug`:

```text
articles/
└── ten-bai-bao/
    ├── metadata.json       # bắt buộc
    ├── article.xml         # JATS XML, chọn một trong hai nguồn
    ├── manuscript.docx     # DOCX, chọn một trong hai nguồn
    └── media/              # hình bổ sung nếu XML tham chiếu tệp cục bộ
```

Nếu có cả `manuscript.docx` và `article.xml`, pipeline chỉ chuyển đổi lại khi DOCX mới hơn XML hoặc khi chạy với `--force`.

