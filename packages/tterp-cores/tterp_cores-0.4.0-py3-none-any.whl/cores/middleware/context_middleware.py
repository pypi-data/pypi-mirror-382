# cores/middleware/context_middleware.py

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from cores.utils.csv_logger import clear_request_context, set_request_context


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Thiết lập context trước khi request được xử lý bởi endpoint
        set_request_context(request)

        try:
            # Chuyển request đến middleware tiếp theo hoặc endpoint
            response = await call_next(request)
        finally:
            # Dọn dẹp context sau khi request đã hoàn thành (rất quan trọng!)
            clear_request_context()

        return response
