# Đóng góp cho LibPub

1. Fork repository và tạo nhánh mô tả rõ thay đổi.
2. Chạy `python scripts/prepare_sources.py`, sau đó `python -m unittest discover -s tests -v`.
3. Kiểm tra bản dựng bằng `python scripts/build.py --output output --skip-pdf`.
4. Mở pull request, nêu rõ thay đổi đối với schema, pipeline hoặc giao diện.

Không commit token, tệp `.env`, dữ liệu tác giả chưa được phép công bố hoặc nội dung trong `output/`. Thư mục `output/` là sản phẩm có thể tái tạo từ nguồn.
