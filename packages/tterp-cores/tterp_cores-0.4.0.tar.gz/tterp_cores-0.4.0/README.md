# Package `cores`

`cores` là một shared repository chứa các thành phần dùng chung cho các microservice trong hệ thống ERP. Package này cung cấp các module cốt lõi như cấu hình, các thành phần dùng chung (Redis, RabbitMQ, SQLAlchemy, JWT, v.v.), các models, middleware, logger, và các RPC clients để giao tiếp giữa các service.

## Tính năng chính

*   **Cấu hình tập trung:** Quản lý cấu hình ứng dụng một cách linh hoạt thông qua biến môi trường và file `.env`.
*   **Thành phần dùng chung:** Cung cấp các client và handler cho các dịch vụ phổ biến như Redis, RabbitMQ, MongoDB, Firebase, và các công cụ xác thực JWT.
*   **ORM và Database:** Hỗ trợ SQLAlchemy Async cho MySQL/MariaDB và Motor cho MongoDB.
*   **Middleware FastAPI:** Bao gồm các middleware cho xác thực, xử lý lỗi, và logging.
*   **Hệ thống Logging:** Logging tập trung với khả năng tích hợp ELK Stack.
*   **RPC Clients:** Giúp các microservice giao tiếp với nhau một cách dễ dàng và an toàn.

## Tài liệu

*   **[Hướng dẫn sử dụng (USAGE.md)](./USAGE.md):** Hướng dẫn chi tiết cách cài đặt, sử dụng và cấu hình package `cores` trong dự án của bạn.
*   **[Hướng dẫn đóng góp (CONTRIBUTING.md)](./CONTRIBUTING.md):** Dành cho các nhà phát triển muốn đóng góp vào package này, bao gồm quy trình phát triển, tiêu chuẩn code và cách chạy test.
*   **[Kế hoạch đóng gói PyPI (PYPI_PACKAGING_PLAN.md)](./PYPI_PACKAGING_PLAN.md):** Mô tả quy trình và các bước để đóng gói và xuất bản package lên PyPI.

## Cài đặt

Bạn có thể cài đặt package này bằng `pip`:

```bash
pip install cores
```

## Cấu hình

Package `cores` sử dụng các biến môi trường để cấu hình. Vui lòng tham khảo file [USAGE.md](./USAGE.md) để biết chi tiết về cách cấu hình bằng file `.env`.

## Đóng góp

Chúng tôi hoan nghênh mọi đóng góp! Vui lòng xem [CONTRIBUTING.md](./CONTRIBUTING.md) để biết cách đóng góp vào dự án này.