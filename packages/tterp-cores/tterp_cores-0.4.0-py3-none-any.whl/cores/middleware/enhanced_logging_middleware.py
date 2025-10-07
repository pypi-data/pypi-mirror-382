"""
Enhanced logging middleware cho FastAPI với correlation ID tracking và performance monitoring.

Middleware này tự động:
- Tạo correlation ID cho mỗi request
- Log API requests với performance metrics
- Set user context từ authentication
- Handle exceptions với structured logging
"""

import time
import uuid
from collections.abc import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from cores.logger.enhanced_logging import LogCategory, LogContext, logger


class EnhancedLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware để tự động log API requests với structured logging và correlation tracking.
    """

    def __init__(self, app, exclude_paths: list | None = None):
        super().__init__(app)
        self.exclude_paths = exclude_paths or [
            "/health",
            "/metrics",
            "/docs",
            "/openapi.json",
        ]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request với enhanced logging"""

        # Skip logging cho certain paths
        if any(request.url.path.startswith(path) for path in self.exclude_paths):
            return await call_next(request)

        # Tạo correlation ID
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())

        # Lấy user info từ request state (set bởi auth middleware)
        user_id = (
            getattr(request.state, "requester", {}).get("user_id")
            if hasattr(request.state, "requester")
            else None
        )

        # Set logging context
        with LogContext(
            correlation_id_val=correlation_id,
            user_id_val=user_id,
            request_path_val=request.url.path,
            session_id_val=request.headers.get("X-Session-ID"),
        ):
            start_time = time.time()

            # Log incoming request
            logger.info(
                f"Incoming request: {request.method} {request.url.path}",
                category=LogCategory.API,
                extra_fields={
                    "http_method": request.method,
                    "http_path": request.url.path,
                    "query_params": dict(request.query_params),
                    "user_agent": request.headers.get("user-agent"),
                    "client_ip": request.client.host if request.client else None,
                    "correlation_id": correlation_id,
                    "user_id": user_id,
                },
            )

            try:
                # Process request
                response = await call_next(request)

                # Calculate response time
                duration_ms = round((time.time() - start_time) * 1000, 2)

                # Add correlation ID to response headers
                response.headers["X-Correlation-ID"] = correlation_id

                # Log API response
                logger.log_api_request(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=duration_ms,
                    user_id=user_id,
                    extra_fields={
                        "correlation_id": correlation_id,
                        "response_size": response.headers.get("content-length", 0),
                    },
                )

                return response

            except Exception as e:
                # Calculate error response time
                duration_ms = round((time.time() - start_time) * 1000, 2)

                # Log exception
                logger.error(
                    f"Request failed: {request.method} {request.url.path} - {str(e)}",
                    category=LogCategory.API,
                    extra_fields={
                        "http_method": request.method,
                        "http_path": request.url.path,
                        "duration_ms": duration_ms,
                        "correlation_id": correlation_id,
                        "user_id": user_id,
                        "exception_type": type(e).__name__,
                    },
                    exc_info=True,
                )

                # Re-raise exception để FastAPI xử lý
                raise


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Simplified middleware chỉ để log requests mà không can thiệp vào business logic.
    """

    def __init__(self, app, log_body: bool = False, max_body_size: int = 1024):
        super().__init__(app)
        self.log_body = log_body
        self.max_body_size = max_body_size

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request details"""

        start_time = time.time()

        # Log request body nếu được enable
        request_body = None
        if self.log_body and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                if len(body) <= self.max_body_size:
                    request_body = body.decode("utf-8")[: self.max_body_size]
                else:
                    request_body = f"<body too large: {len(body)} bytes>"
            except Exception:
                request_body = "<unable to read body>"

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log với structured format
        log_data = {
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": duration_ms,
            "query_params": dict(request.query_params),
            "headers": dict(request.headers),
            "client_ip": request.client.host if request.client else None,
        }

        if request_body:
            log_data["request_body"] = request_body

        logger.info(
            f"API Request: {request.method} {request.url.path} -> {response.status_code} ({duration_ms}ms)",
            category=LogCategory.API,
            extra_fields=log_data,
        )

        return response


# Export
__all__ = ["EnhancedLoggingMiddleware", "RequestLoggingMiddleware"]
