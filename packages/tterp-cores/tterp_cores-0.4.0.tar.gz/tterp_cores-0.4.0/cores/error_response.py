"""
Module cung cấp các lớp phản hồi lỗi chuẩn cho ứng dụng.

Module này export các class lỗi từ cores.model.base_error để
các module khác có thể import và xử lý lỗi một cách nhất quán.
"""

from cores.model.base_error import (
    BadRequestError,
    ConflictRequestError,
    ErrorResponse,
    ForbiddenError,
    NotfoundError,
    UnauthorizeError,
)

__all__ = [
    "ErrorResponse",
    "ConflictRequestError",
    "BadRequestError",
    "NotfoundError",
    "ForbiddenError",
    "UnauthorizeError",
]
