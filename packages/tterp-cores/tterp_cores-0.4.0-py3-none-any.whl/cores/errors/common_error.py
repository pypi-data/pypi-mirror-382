"""
Common HTTP errors
"""

from .base_error import BaseHTTPError


class CommonHTTPError:
    """Common HTTP errors"""

    err_internal_server = BaseHTTPError(
        status_code=500,
        code="INTERNAL_SERVER_ERROR",
        message="Internal server error",
    )

    err_not_found = BaseHTTPError(
        status_code=404,
        code="NOT_FOUND",
        message="Resource not found",
    )

    err_bad_request = BaseHTTPError(
        status_code=400,
        code="BAD_REQUEST",
        message="Bad request",
    )

    err_unauthorized = BaseHTTPError(
        status_code=401,
        code="UNAUTHORIZED",
        message="Unauthorized",
    )

    err_forbidden = BaseHTTPError(
        status_code=403,
        code="FORBIDDEN",
        message="Forbidden",
    )

    err_conflict = BaseHTTPError(
        status_code=409,
        code="CONFLICT",
        message="Conflict",
    )
