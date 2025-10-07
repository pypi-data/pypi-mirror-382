"""
Module cung cấp các middleware xác thực và phân quyền.

Module này chứa các middleware để:
- Xác thực user token
- Xác thực auth token
- Kiểm tra quyền truy cập vào các routes
- Gắn thông tin người dùng vào request state
"""

import os
from collections.abc import Callable
from typing import Any

from fastapi import Depends, HTTPException, Request
from fastapi.security import (
    APIKeyHeader,
    HTTPAuthorizationCredentials,
    HTTPBearer,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from cores.config import config, service_config
from cores.interface.index import CheckPermissionResult
from cores.logger.enhanced_logging import LogCategory, logger
from cores.logger.logging import ApiLogger
from cores.repository.rpc.auth_client import AuthClient
from cores.repository.rpc.verify_token_rpc import TokenIntrospectRPCClient

# Định nghĩa header cho service management ID
service_id_header = APIKeyHeader(
    name="service-management-id",
    scheme_name="ServiceManagementId",
    description=f"""Origin service id để truy cập endpoints.
      Mặc định: {service_config.BASE_SERVICE_ID}""",
    auto_error=True,
)

# Định nghĩa OAuth bearer token
reusable_oauth2 = HTTPBearer(
    scheme_name="Authorization", description="JWT Token từ Auth Service."
)

# Định nghĩa user token như một API Key header để hiện trong OpenAPI securitySchemes
user_token_header = APIKeyHeader(
    name="user-token",
    scheme_name="UserToken",
    description="JWT của người dùng (header: user-token)",
    auto_error=True,
)


async def user_token_middleware(
    req: Request,
    user_token: str = Depends(user_token_header),
) -> None:
    """
    Middleware kiểm tra user token và gắn thông tin requester vào request state.

    Xác thực user token bằng cách gọi introspect API và gắn thông tin
    người dùng vào request state nếu token hợp lệ.

    Args:
        req: Đối tượng Request
        user_token: Token người dùng từ header

    Raises:
        HTTPException: Nếu token không hợp lệ hoặc hết hạn
    """
    # 1. Xác thực token
    introspector = TokenIntrospectRPCClient(user_token)
    introspected_result = await introspector.introspect()
    if not introspected_result.is_ok:
        raise HTTPException(
            status_code=401,
            detail=(
                introspected_result.error.detail
                if introspected_result.error.detail
                else "Unauthorized"
            ),
        )

    # 2. Gán requester vào req.state
    req.state.requester = introspected_result.payload


async def auth_middleware(
    req: Request,
    service_id: str = Depends(service_id_header),
    user_token: str = Depends(user_token_header),
    auth_token: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> None:
    """
    Middleware xác thực toàn diện, kiểm tra cả auth token và user token.

    Hỗ trợ 2 luồng:
    1. FE call: user token từ cookie sau khi login (có field "id")
    2. BE call: user token từ KeyManagementService (có field "service_management_id")

    Args:
        req: Đối tượng Request
        service_id: ID của service gọi API
        user_token: Token người dùng từ header
        auth_token: Bearer token xác thực

    Raises:
        HTTPException: Nếu bất kỳ token nào không hợp lệ hoặc hết hạn
    """
    from cores.depends.authorization import TokenService
    from cores.interface.index import CheckPermissionResult

    # 1. Xác thực auth token từ request
    auth_client = AuthClient(auth_token.credentials)
    validated_user_token = await auth_client.validate_token(
        service_id, service_config.BASE_SERVICE_ID, user_token
    )

    # 2. Kiểm tra loại token để xử lý khác nhau
    try:
        # Decode token để xem payload
        payload = TokenService.decode_without_verification(validated_user_token)

        if "service_management_id" in payload:
            # Đây là token từ BE (KeyManagementService)
            # Không cần gọi introspect API để tránh vòng lặp
            # Sử dụng user_id mặc định cho BE-to-BE call
            req.state.requester = CheckPermissionResult(
                can_action=True,
                user_id=1,  # Default user_id cho BE calls
            )
            req.state.user_token = validated_user_token

        elif "id" in payload:
            # Đây là token từ FE (user token thông thường)
            # Xác thực user token như bình thường
            introspector = TokenIntrospectRPCClient(validated_user_token)
            introspected_result = await introspector.introspect()
            if not introspected_result.is_ok:
                raise HTTPException(
                    status_code=401,
                    detail=(
                        introspected_result.error.detail
                        if introspected_result.error.detail
                        else "Unauthorized"
                    ),
                )

            req.state.requester = introspected_result.payload
            req.state.user_token = validated_user_token

        else:
            raise HTTPException(status_code=401, detail="User token không hợp lệ")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Token processing failed: {str(e)}", category=LogCategory.SYSTEM)
        raise HTTPException(status_code=401, detail="User token không hợp lệ")


async def check_permission_middleware(
    req: Request,
    service_id: str = Depends(service_id_header),
    user_token: str = Depends(user_token_header),
    auth_token: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> None:
    ApiLogger.debug(req.url)
    """
    Middleware kiểm tra quyền truy cập vào một route cụ thể.

    Thực hiện ba bước kiểm tra:
    1. Xác thực auth token để đảm bảo request đến từ service hợp lệ
    2. Xác thực user token để đảm bảo người dùng đã đăng nhập
    3. Kiểm tra quyền truy cập vào route cụ thể với phương thức HTTP

    Args:
        req: Đối tượng Request
        service_id: ID của service gọi API
        user_token: Token người dùng từ header
        auth_token: Bearer token xác thực

    Raises:
        HTTPException: Nếu token không hợp lệ hoặc không có quyền truy cập
    """
    # 1. Xác thực auth token từ request
    auth_client = AuthClient(auth_token.credentials)
    validated_user_token = await auth_client.validate_token(
        service_id, service_config.BASE_SERVICE_ID, user_token
    )

    # 2. Xác thực quyền truy cập vào route
    route = req.scope["root_path"] + req.scope["route"].path
    introspector = TokenIntrospectRPCClient(validated_user_token)

    introspected_result = await introspector.check_permission(route, req.method)

    if not introspected_result.can_action:
        raise HTTPException(
            status_code=401,
            detail="Không có quyền truy cập vào tài nguyên này",
        )

    # 3. Gán requester và user token vào req.state
    req.state.requester = introspected_result
    req.state.user_token = validated_user_token


# Giá trị mặc định cho user ID khi override check access
_override_user_id: int = 1


async def _override_check_access(req: Request) -> CheckPermissionResult:
    from utils.test_util import UserIdEnum, UserToken

    """
    Override kiểm tra truy cập, sử dụng cho môi trường phát triển.
    Kiểm tra user_token để mô phỏng quyền.
    """
    user_token_header = req.headers.get("user-token")

    # Default to allowing access with a generic user ID
    can_action = True
    requester = CheckPermissionResult(can_action=True, user_id=_override_user_id)

    # If the user token is specifically for a no-permission user, set can_action to False
    if user_token_header == UserToken.USER_NO_PERMISSION.value:
        can_action = False
        requester = CheckPermissionResult(
            can_action=False, user_id=UserIdEnum.USER_NO_PERMISSION.value
        )

    req.state.requester = requester

    # Nếu không có quyền, raise HTTPException
    if not can_action:
        raise HTTPException(status_code=403, detail="Forbidden")

    return requester


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware xác thực và phân quyền cho FastAPI.

    Sử dụng Starlette BaseHTTPMiddleware để triển khai xác thực.
    Trong môi trường test, sử dụng _override_check_access.
    Trong môi trường sản phẩm, sử dụng check_permission_middleware.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """
        Xử lý request và thực hiện xác thực.

        Args:
            request: Request hiện tại
            call_next: Handler tiếp theo trong chuỗi middleware

        Returns:
            Response: Kết quả từ handler tiếp theo hoặc lỗi xác thực
        """
        # Bỏ qua xác thực cho một số endpoint đặc biệt
        excluded_paths = ["/docs", "/redoc", "/openapi.json", "/metrics"]
        for path in excluded_paths:
            if request.url.path.startswith(path):
                return await call_next(request)

        try:
            if os.environ.get("ENVIRONMENT") == "test" or getattr(
                config, "DISABLE_AUTH", False
            ):
                # Sử dụng override trong môi trường test hoặc khi cấu hình tắt
                # xác thực
                await _override_check_access(request)
            else:
                # Thực hiện xác thực đầy đủ trong môi trường sản phẩm
                # Lưu ý: Ở đây chúng ta không thể sử dụng check_permission_middleware trực tiếp
                # vì nó cần Depends, nên triển khai lại logic tương tự

                # Giả lập UserID=1 trong quá trình refactoring
                # TODO: Triển khai xác thực đầy đủ khi hoàn thành refactoring
                requester = CheckPermissionResult(
                    can_action=True, user_id=_override_user_id
                )
                request.state.requester = requester

            return await call_next(request)
        except HTTPException as e:
            return JSONResponse(
                status_code=e.status_code,
                content={
                    "code": "UNAUTHORIZED",
                    "message": str(e.detail),
                    "data": None,
                },
            )
        except Exception:
            logger.error(
                "Authentication error: {str(e)}",
                category=LogCategory.SYSTEM,
                exc_info=True,
            )
            return JSONResponse(
                status_code=500,
                content={
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                    "data": None,
                },
            )
