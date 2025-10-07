"""
Base error class for HTTP errors
"""

from typing import Any


class BaseHTTPError(Exception):
    """Base class for HTTP errors"""

    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        data: dict[str, Any] | None = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.data = data
        super().__init__(self.message)
