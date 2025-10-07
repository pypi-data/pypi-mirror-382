"""
Logging middleware - Ghi log các request và response
"""

import time
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from cores.logger.enhanced_logging import LogCategory, logger


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware để ghi log các request và response

    Ghi log thời gian xử lý, method, path, status code và thời gian phản hồi
    """

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """
        Xử lý request và ghi log

        Args:
            request: Request object
            call_next: Hàm xử lý request tiếp theo

        Returns:
            Response object
        """
        start_time = time.time()

        # Log request
        logger.info(
            "Request received",
            category=LogCategory.API,
            extra_fields={
                "method": request.method,
                "path": request.url.path,
            },
        )

        # Xử lý request
        response = await call_next(request)

        # Tính thời gian xử lý
        process_time = time.time() - start_time

        # Log response
        logger.info(
            "Response sent",
            category=LogCategory.API,
            extra_fields={
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
                "process_time": round(process_time, 4),
            },
        )

        return response
