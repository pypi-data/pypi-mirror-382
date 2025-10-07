"""
Module cung cấp các middleware cơ bản cho ứng dụng.

Module này định nghĩa các middleware cho:
- Logging thông tin request
- Logging thời gian xử lý request
- Xử lý exceptions
- Giới hạn tần suất truy cập (rate limiting)
- Tích hợp Sentry
"""

import json
import time
import traceback
import uuid
from collections import defaultdict
from collections.abc import Callable

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from cores.config import sentry_config, service_config
from cores.logger.logging import ApiLogger
from cores.logger.logging_setup import ELKLogger


async def log_info(request: Request) -> Request:
    """
    Ghi log thông tin request và gán request_id.

    Đọc body của request và gán một UUID duy nhất làm request_id.

    Args:
        request: Đối tượng Request cần log thông tin

    Returns:
        Request: Đối tượng Request đã được gán request_id
    """
    try:
        body = await request.json()
    except json.JSONDecodeError:
        body = await request.body()
        body = body.decode("utf-8")  # Chuyển đổi sang chuỗi

    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    # # Log thông tin request
    # method = request.method
    # path = request.url.path
    # query_params = dict(request.query_params)
    # ApiLogger.info(
    #     f"Request ID: {request_id} | Method: {method} | Path: {path} | "
    #     f"Query Params: {json.dumps(query_params)} | Body: {body}"
    # )
    # ELKLogger.log(
    #     f"Request ID: {request_id} | Method: {method} | Path: {path} | "
    #     f"Query Params: {json.dumps(query_params)} | Body: {body}",
    #     log_type='info'
    # )

    return request


async def log_request_processing_time(request_id: str, start_time: float) -> None:
    """
    Ghi log thời gian xử lý request.

    Args:
        request_id: ID của request
        start_time: Thời điểm bắt đầu xử lý request
    """
    end_time = time.time()  # Ghi nhận thời gian kết thúc xử lý
    processing_time = end_time - start_time  # Tính toán thời gian xử lý

    # Log thời gian xử lý
    ApiLogger.info(
        f"Request ID: {request_id} | Processing Time: {processing_time:.4f} seconds"
    )


async def catch_exceptions_middleware(
    request: Request, call_next: Callable
) -> Response:
    """
    Middleware bắt và xử lý tất cả các exceptions.

    Bắt tất cả các exceptions xảy ra trong quá trình xử lý request,
    ghi log và trả về response lỗi phù hợp.

    Args:
        request: Đối tượng Request
        call_next: Hàm để gọi middleware tiếp theo hoặc endpoint

    Returns:
        Response: Kết quả xử lý request hoặc response lỗi
    """
    request_id = (
        request.state.request_id if hasattr(request.state, "request_id") else None
    )
    try:
        response = await call_next(request)
        if request_id:
            response.headers["X-Request-ID"] = request_id
        return response

    except HTTPException as e:
        # Re-raise HTTPException để FastAPI xử lý
        raise e
    except Exception as e:
        # Ghi lại lỗi vào log
        ApiLogger.error(f"\nRequest ID: {request_id} {traceback.format_exc()} ")
        # ELKLogger.log(
        #     message=f"Request ID: {request_id}. Error: {str(e)} ",
        #     log_type="error",
        # )

        # Nếu môi trường là local, trả về chi tiết lỗi
        if service_config.APP_ENV != "production":
            formatted_traceback = traceback.format_exc().splitlines()
            err_detail = {
                "request_id": request_id,
                "detail": str(e),
                "traceback": formatted_traceback,
            }
            return JSONResponse(err_detail, status_code=500)

        # Nếu không, trả về thông báo lỗi chung chung
        return JSONResponse({"detail": "Internal server error"}, status_code=500)


# Hàm middleware để log thời gian xử lý
async def log_processing_time(request: Request, call_next: Callable) -> Response:
    """
    Middleware ghi log thời gian xử lý request.

    Tính toán và ghi log thời gian xử lý của mỗi request.
    Nếu thời gian xử lý vượt quá ngưỡng (0.5 giây), sẽ ghi log chi tiết.

    Args:
        request: Đối tượng Request
        call_next: Hàm để gọi middleware tiếp theo hoặc endpoint

    Returns:
        Response: Kết quả xử lý request
    """
    start_time = time.time()  # Ghi nhận thời gian bắt đầu xử lý

    response = await call_next(request)

    processing_time = time.time() - start_time  # Tính toán thời gian xử lý

    # Log thời gian xử lý
    request_id = (
        request.state.request_id if hasattr(request.state, "request_id") else None
    )
    # ApiLogger.info(f"Request ID: {request_id} | Path: {request.url.path} | Processing Time: {processing_time:.4f} seconds")
    if processing_time >= 0.5:
        ELKLogger.log_processing_time(
            f"Request ID: {request_id} | Path: {request.url.path} | Processing Time: {processing_time:.4f} seconds",
            processing_time=processing_time,
        )
    return response


def integrate_sentry() -> None:
    """
    Tích hợp Sentry để theo dõi lỗi và hiệu suất.

    Khởi tạo Sentry SDK nếu được bật trong cấu hình.
    """
    # sentry
    if sentry_config.SENTRY_ENABLE:
        import sentry_sdk

        sentry_sdk.init(
            dsn=sentry_config.SENTRY_DNS,
            # Set traces_sample_rate to 1.0 to capture 100%
            # of transactions for performance monitoring.
            traces_sample_rate=1.0,
            # Set profiles_sample_rate to 1.0 to profile 100%
            # of sampled transactions.
            # We recommend adjusting this value in production.
            profiles_sample_rate=1.0,
        )


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware giới hạn tần suất truy cập (rate limiting).

    Giới hạn số lượng requests từ một địa chỉ IP đến một route cụ thể
    trong một khoảng thời gian.

    Attributes:
        limit: Số lượng requests tối đa cho phép trong khoảng thời gian
        period: Khoảng thời gian (giây) để áp dụng giới hạn
        visits: Dictionary lưu trữ thời gian các lần truy cập
    """

    def __init__(self, app: FastAPI, limit: int, period: int) -> None:
        """
        Khởi tạo middleware rate limiting.

        Args:
            app: Ứng dụng FastAPI
            limit: Số lượng requests tối đa cho phép trong khoảng thời gian
            period: Khoảng thời gian (giây) để áp dụng giới hạn
        """
        super().__init__(app)
        self.limit = limit
        self.period = period
        self.visits: defaultdict[str, defaultdict[str, list[float]]] = defaultdict(
            lambda: defaultdict(list)
        )  # Khởi tạo nested defaultdict

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Xử lý request và kiểm tra giới hạn tần suất.

        Args:
            request: Đối tượng Request
            call_next: Hàm để gọi middleware tiếp theo hoặc endpoint

        Returns:
            Response: Kết quả xử lý request

        Raises:
            HTTPException: Nếu vượt quá giới hạn tần suất
        """
        client_ip = request.client.host
        route_path = request.url.path
        now = time.time()

        # Xóa timestamps bên ngoài thời gian giới hạn
        self.visits[client_ip][route_path] = [
            ts for ts in self.visits[client_ip][route_path] if ts > now - self.period
        ]

        # Kiểm tra số lần truy cập
        if len(self.visits[client_ip][route_path]) >= self.limit:
            raise HTTPException(
                status_code=429,
                detail="Quá nhiều yêu cầu, vui lòng thử lại sau",
            )

        # Thêm timestamp mới
        self.visits[client_ip][route_path].append(now)

        response = await call_next(request)
        return response
