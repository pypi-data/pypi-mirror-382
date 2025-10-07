"""
Exception middleware - Xử lý các exception trong ứng dụng
"""

import traceback
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from cores.logger.enhanced_logging import LogCategory, logger


class ExceptionMiddleware(BaseHTTPMiddleware):
    """
    Middleware để xử lý các exception trong ứng dụng

    Ghi log các exception và cho phép ứng dụng tiếp tục xử lý
    thông qua các exception handler đã đăng ký.
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Xử lý request và bắt các exception

        Args:
            request: Request object
            call_next: Hàm xử lý request tiếp theo

        Returns:
            Response object
        """
        try:
            return await call_next(request)
        except Exception as e:
            # Ghi log exception
            logger.error(
                "Exception occurred",
                category=LogCategory.API,
                extra_fields={
                    "detail": str(e),
                    "traceback": traceback.format_exc(),
                },
                exc_info=True,
            )
            # Cho phép exception handler của FastAPI xử lý
            raise
