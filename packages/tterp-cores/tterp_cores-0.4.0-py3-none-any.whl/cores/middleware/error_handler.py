"""
Module cung cấp middleware xử lý lỗi tập trung cho ứng dụng.

Module này định nghĩa:
- GlobalErrorHandler: Middleware bắt và xử lý tất cả các exceptions trong ứng
- Hàm tiện ích để thiết lập middleware cho FastAPI
"""

from __future__ import annotations

import traceback
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from cores.errors.base_error import BaseHTTPError
from cores.logger.enhanced_logging import LogCategory, logger
from cores.model.error_model import GenericHTTPException


class GlobalErrorHandler(BaseHTTPMiddleware):
    """
    Middleware xử lý lỗi tập trung cho toàn bộ API.

    Bắt tất cả các exceptions xảy ra trong quá trình xử lý request và
    trả về response lỗi với format nhất quán. Đồng thểm ghi log chi tiết
    về lỗi để phục vụ việc debug.

    Lợi ích:
    - Tất cả các exception được xử lý tại một nơi
    - Format response lỗi nhất quán
    - Logging tập trung
    - Dễ dàng thêm xử lý lỗi đặc biệt cho từng loại exception

    Attributes:
        project_root: Đường dẫn gốc của project, dùng để lọc stacktrace
    """

    def __init__(self, app: FastAPI, project_root: str) -> None:
        """
        Khởi tạo middleware xử lý lỗi.

        Args:
            app: Ứng dụng FastAPI
            project_root: Đường dẫn gốc của project, dùng để lọc stacktrace
        """
        super().__init__(app)
        self.project_root = project_root

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        Xử lý request và bắt các exceptions.

        Args:
            request: Đối tượng Request
            call_next: Hàm để gọi middleware tiếp theo hoặc endpoint

        Returns:
            Response: Kết quả xử lý request hoặc response lỗi
        """
        try:
            return await call_next(request)
        except GenericHTTPException as e:
            # Xử lý các HTTP exception đã được định nghĩa trong codebase
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "code": e.code,
                    "message": e.message,
                    "data": None,
                },
            )
        except BaseHTTPError as e:
            # Xử lý BaseHTTPError (business error tự định nghĩa không kế thừa HTTPException)
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "code": e.code,
                    "message": e.message,
                    "data": e.data if hasattr(e, "data") else None,
                },
            )
        except HTTPException as e:
            # Xử lý các HTTPException tiêu chuẩn của FastAPI
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "success": False,
                    "code": "HTTP_EXCEPTION",  # Có thể tùy chỉnh mã lỗi này
                    "message": e.detail,
                    "data": None,
                },
            )
        except Exception as e:
            # Xử lý các exception không được xác định trước
            error_id = f"err-{id(e)}"
            tb = traceback.format_exc()
            lines = tb.splitlines()
            filtered_lines: list[str] = []

            # Luôn giữ dòng đầu và dòng cuối
            if lines:
                filtered_lines.append(lines[0])
            for line in lines[1:-1]:
                if self.project_root in line:
                    filtered_lines.append(line)
            if len(lines) > 1:
                filtered_lines.append(lines[-1])

            filtered_tb = "\n".join(filtered_lines)
            logger.error(
                "Unhandled exception",
                category=LogCategory.API,
                extra_fields={
                    "error_id": error_id,
                    "detail": str(e),
                    "traceback": filtered_tb,
                },
                exc_info=True,
            )

            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "success": False,
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": ("Đã xảy ra lỗi không mong đợi, vui lòng thử lại sau"),
                    "error_id": error_id,
                    "data": None,
                },
            )


def setup_global_error_handler(app: FastAPI, project_root: str) -> None:
    """
    Thiết lập Global Error Handler middleware cho ứng dụng FastAPI.

    Thêm middleware xử lý lỗi vào ứng dụng FastAPI để bắt và xử lý
    tất cả các exceptions.

    Args:
        app: Ứng dụng FastAPI cần thêm middleware
        project_root: Đường dẫn gốc của project, dùng để lọc stacktrace
    """
    app.add_middleware(GlobalErrorHandler, project_root=project_root)
