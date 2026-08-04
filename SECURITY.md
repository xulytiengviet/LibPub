# Chính sách bảo mật

## Token GitHub trong dashboard

Dashboard cần fine-grained personal access token khi tác giả chọn **Submit & Publish**. Token:

- chỉ được giữ trong biến bộ nhớ của tab hiện tại;
- không được ghi vào `localStorage`, `sessionStorage`, URL, cookie hoặc tệp metadata;
- chỉ được gửi trực tiếp từ trình duyệt đến `api.github.com`;
- được xóa khỏi ô nhập sau khi commit thành công.

Chỉ cấp quyền **Contents: Read and write** cho riêng repository `LibPub`, đặt thời hạn ngắn và thu hồi token sau khi dùng. Không sử dụng token có quyền quản trị tổ chức hoặc quyền vượt quá nhu cầu.

## Mô hình tin cậy

LibPub là hệ thống xuất bản do chủ repository kiểm soát, không phải cổng nộp bài công cộng không cần xác thực. Bất kỳ ai có quyền ghi vào nhánh công bố đều có thể thay đổi nội dung được triển khai. Nên bật branch protection và dùng pull request khi có nhiều cộng tác viên.

## Báo cáo lỗ hổng

Không công bố token, dữ liệu cá nhân hoặc bản thảo mật trong issue công khai. Hãy dùng kênh báo cáo bảo mật riêng của GitHub repository nếu được bật.

