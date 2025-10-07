from typing import Any

from starlette.exceptions import HTTPException as StarletteHTTPException

from cores.utils.reason_phrases import ReasonPhrase
from cores.utils.status_codes import StatusCode

# Define status codes as constants
# class StatusCode:
#     FORBIDDEN = 403
#     CONFLICT = 409

# # Define reason messages as constants
# class ReasonStatusCode:
#     FORBIDDEN = 'Bad request error'
#     CONFLICT = 'Conflict error'

# Custom exception classes


class ErrorResponse(StarletteHTTPException):
    """
    Lớp cơ sở cho các lỗi HTTP response.

    Class này kế thừa từ StarletteHTTPException và cung cấp
    cấu trúc chuẩn cho các lỗi HTTP.

    Attributes:
        message: Thông báo lỗi
        status: Mã trạng thái HTTP
        headers: Headers bổ sung cho response
    """

    def __init__(
        self,
        message: Any = None,
        status: int = 500,
        headers: dict[str, Any] | None = None,
    ):
        super().__init__(status_code=status, detail=message, headers=headers)


class ConflictRequestError(ErrorResponse):
    """
    Lỗi xung đột (HTTP 409).

    Được sử dụng khi request xung đột với trạng thái hiện tại của server.
    Ví dụ: Tạo tài nguyên đã tồn tại.
    """

    def __init__(
        self, message=ReasonPhrase.CONFLICT, status=StatusCode.CONFLICT
    ):
        super().__init__(message, status)


class BadRequestError(ErrorResponse):
    """
    Lỗi yêu cầu không hợp lệ (HTTP 400).

    Được sử dụng khi request không đúng định dạng hoặc thiếu thông tin.
    """

    def __init__(
        self, message=ReasonPhrase.BAD_REQUEST, status=StatusCode.BAD_REQUEST
    ):
        super().__init__(message, status)


class NotfoundError(ErrorResponse):
    """
    Lỗi không tìm thấy tài nguyên (HTTP 404).

    Được sử dụng khi tài nguyên được yêu cầu không tồn tại.
    """

    def __init__(
        self, message=ReasonPhrase.NOT_FOUND, status=StatusCode.NOT_FOUND
    ):
        super().__init__(message, status)


class ForbiddenError(ErrorResponse):
    """
    Lỗi truy cập bị cấm (HTTP 403).

    Được sử dụng khi người dùng không có quyền truy cập vào tài nguyên.
    """

    def __init__(
        self, message=ReasonPhrase.FORBIDDEN, status=StatusCode.FORBIDDEN
    ):
        super().__init__(message, status)


class UnauthorizeError(ErrorResponse):
    """
    Lỗi chưa xác thực (HTTP 401).

    Được sử dụng khi người dùng chưa đăng nhập hoặc token không hợp lệ.
    """

    def __init__(
        self, message=ReasonPhrase.UNAUTHORIZED, status=StatusCode.UNAUTHORIZED
    ):
        super().__init__(message, status)
