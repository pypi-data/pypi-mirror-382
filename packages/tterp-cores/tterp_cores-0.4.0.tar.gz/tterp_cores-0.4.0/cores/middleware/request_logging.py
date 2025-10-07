"""
Module cung cấp middleware để ghi log các requests và responses.

Module này định nghĩa RequestLoggingMiddleware để:
- Ghi log thông tin về mỗi request và response
- Tạo request_id duy nhất cho mỗi request
- Thiết lập LogContext để truyền thông tin request vào các log khác
- Đo thời gian xử lý request
"""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from cores.logger.context import LogContext
from cores.logger.enhanced_logging import logger, LogCategory


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware theo dõi và log các request và response.

    Tính năng:
    - Tạo request_id duy nhất cho mỗi request
    - Ghi log thông tin request (method, path, params)
    - Ghi log thông tin response (status code, thời gian xử lý)
    - Thiết lập LogContext để thông tin request_id, user_id được truyền vào các log khác
    - Thêm header X-Request-ID vào response
    - Ghi log lỗi nếu xảy ra exception trong quá trình xử lý
    """

    def __init__(self, app: FastAPI) -> None:
        """
        Khởi tạo middleware logging.

        Args:
            app: Ứng dụng FastAPI
        """
        super().__init__(app)

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Xử lý request và ghi log thông tin liên quan.

        Args:
            request: Đối tượng Request
            call_next: Hàm để gọi middleware tiếp theo hoặc endpoint

        Returns:
            Response: Kết quả xử lý request

        Raises:
            Exception: Truyền tiếp bất kỳ exception nào xảy ra trong quá trình xử lý
        """
        # Tạo request_id duy nhất
        request_id = str(uuid.uuid4())
        start_time = time.time()

        # Lấy thông tin user_id từ request nếu có
        user_id: int | None = None
        if hasattr(request.state, "user") and hasattr(
            request.state.user, "id"
        ):
            user_id = request.state.user.id

        # Log request
        logger.info(
            f"Request started: {request.method} {request.url.path}",
            category=LogCategory.API,
            extra_fields={
                "request_id": request_id,
                "method": request.method,
                "path": request.url.path,
                "query_params": str(request.query_params),
            },
        )

        # Sử dụng LogContext để gắn request_id và user_id vào các log sau này
        with LogContext(
            request_id=request_id,
            user_id=user_id,
            method=request.method,
            path=request.url.path,
        ):
            try:
                # Xử lý request
                response = await call_next(request)

                # Tính thời gian xử lý
                process_time = time.time() - start_time

                # Log response
                logger.info(
                    f"Request completed: {request.method} {request.url.path}",
                    category=LogCategory.API,
                    extra_fields={
                        "status_code": response.status_code,
                        "process_time": f"{process_time:.4f}s",
                    },
                )

                # Thêm header X-Request-ID vào response
                response.headers["X-Request-ID"] = request_id

                return response
            except Exception as e:
                # Log lỗi nếu có
                process_time = time.time() - start_time
                logger.error(
                    f"Request failed: {request.method} {request.url.path}",
                    category=LogCategory.API,
                    extra_fields={
                        "error": str(e),
                        "process_time": f"{process_time:.4f}s",
                    },
                )
                raise


def setup_request_logging(app: FastAPI) -> None:
    """
    Thiết lập Request Logging middleware cho ứng dụng FastAPI.

    Thêm RequestLoggingMiddleware vào ứng dụng để ghi log tất cả các requests.

    Args:
        app: Ứng dụng FastAPI cần thêm middleware
    """
    app.add_middleware(RequestLoggingMiddleware)
