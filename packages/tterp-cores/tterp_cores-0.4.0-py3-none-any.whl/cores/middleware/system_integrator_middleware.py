"""
Module cung cấp middleware hỗ trợ xác thực System Integrator.

Module này định nghĩa các thành phần để:
- Xác thực và xử lý các requests từ System Integrator
- Tích hợp với luồng xác thực hiện có
- Tự động phát hiện loại token để áp dụng xử lý phù hợp
"""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials

from cores.config import service_config
from cores.interface.index import CheckPermissionResult
from cores.logger.enhanced_logging import LogCategory, logger
from cores.middleware.auth import reusable_oauth2, service_id_header
from cores.model.system_integrator import (
    InvalidClientError,
    TokenExpiredError,
)
from cores.repository.rpc.auth_client import AuthClient
from cores.repository.rpc.system_integrator_client import (
    SystemIntegratorAuthClient,
    SystemIntegratorUserClient,
)
from cores.repository.rpc.verify_token_rpc import TokenIntrospectRPCClient
from cores.utils.system_integrator_helper import (
    SystemIntegratorTokenDetector,
)


class SystemIntegratorMiddleware:
    """
    Middleware handler cho System Integrator authentication.

    Xử lý luồng xác thực đặc biệt cho System Integrator, bao gồm:
    - Xác thực token với Auth Service
    - Kiểm tra quyền truy cập vào route cụ thể
    - Thiết lập thông tin người dùng System Integrator vào request state

    Attributes:
        auth_client: Client để giao tiếp với System Integrator Auth Service
        user_client: Client để giao tiếp với System Integrator User Service
    """

    def __init__(self) -> None:
        """
        Khởi tạo middleware với các clients cần thiết.
        """
        self.auth_client = SystemIntegratorAuthClient()
        self.user_client = SystemIntegratorUserClient()

    async def handle_system_integrator_request(
        self, req: Request, auth_token: str
    ) -> None:
        """
        Xử lý luồng xác thực cho System Integrator.

        Thực hiện các bước:
        1. Xác thực token với Auth Service
        2. Introspect user token để lấy thông tin người dùng
        3. Kiểm tra quyền truy cập vào route cụ thể
        4. Thiết lập thông tin vào request state

        Args:
            req: Đối tượng Request
            auth_token: Token xác thực từ System Integrator

        Raises:
            HTTPException: Nếu xác thực thất bại hoặc không có quyền truy cập
        """

        try:
            # 1. Validate token với Auth Service
            validation_response = await self.auth_client.validate_token(
                auth_token, service_config.BASE_SERVICE_ID
            )

            if not validation_response.valid:
                raise HTTPException(
                    status_code=401,
                    detail=validation_response.error_message
                    or "Invalid system integrator token",
                )

            system_user_token = validation_response.user_token

            # 2. Introspect user token
            user_info = await self.user_client.introspect_token(
                system_user_token
            )

            # 3. Check permission
            route = self._get_request_route(req)
            permission_response = await self.user_client.check_permission(
                route,
                req.method,
                system_user_token,
                table_management_id=self._extract_table_management_id(route),
            )

            if not permission_response.can_action:
                raise HTTPException(
                    status_code=403,
                    detail=f"System Integrator permission denied: {permission_response.reason}",
                )

            # 4. Set request state
            req.state.requester = CheckPermissionResult(
                can_action=True, user_id=permission_response.user_id
            )
            req.state.user_token = system_user_token
            req.state.is_system_integrator = True
            req.state.client_id = user_info.client_id

            logger.info(
                "System Integrator request authenticated",
                category=LogCategory.API,
                extra_fields={
                    "client_id": user_info.client_id,
                    "route": route,
                    "method": req.method,
                },
            )

        except (InvalidClientError, TokenExpiredError) as e:
            logger.warning(
                "System Integrator authentication failed",
                category=LogCategory.API,
                extra_fields={"detail": str(e)},
            )
            raise HTTPException(status_code=401, detail=str(e))
        except Exception as e:
            logger.error(
                "System Integrator middleware error",
                category=LogCategory.SYSTEM,
                extra_fields={"detail": str(e)},
                exc_info=True,
            )
            raise HTTPException(
                status_code=500,
                detail="System Integrator authentication error",
            )

    def _get_request_route(self, req: Request) -> str:
        """
        Lấy đường dẫn đầy đủ của route từ request.

        Args:
            req: Đối tượng Request

        Returns:
            Đường dẫn đầy đủ của route
        """
        root_path = req.scope.get("root_path", "")
        route_path = req.scope.get("route", {}).get("path", "")
        return root_path + route_path

    def _extract_table_management_id(self, route: str) -> str | None:
        """
        Trích xuất table management ID từ route.

        Phân tích đường dẫn route để xác định table management ID
        dựa trên các pattern đã định nghĩa.

        Args:
            route: Đường dẫn route cần phân tích

        Returns:
            Table management ID nếu tìm thấy, None nếu không
        """
        # Simple pattern matching
        if "/v1/royalty" in route:
            return "royalty"
        elif "/v1/news" in route:
            return "news"
        elif "/v1/user" in route:
            return "user"
        # Add more patterns as needed
        return None


# Enhanced middleware function
async def enhanced_check_permission_middleware(
    req: Request,
    service_id: str = Depends(service_id_header),
    user_token: str | None = Header(
        None
    ),  # Make optional for System Integrator
    auth_token: HTTPAuthorizationCredentials = Depends(reusable_oauth2),
) -> None:
    """
    Middleware nâng cao với khả năng tự động phát hiện token System Integrator.

    Middleware này tương thích ngược với luồng xác thực hiện có, đồng thời
    hỗ trợ xác thực cho System Integrator. Tự động phát hiện loại token
    để áp dụng luồng xử lý phù hợp.

    Args:
        req: Đối tượng Request
        service_id: ID của service gọi API
        user_token: Token người dùng từ header (có thể None cho System Integrator)
        auth_token: Bearer token xác thực

    Raises:
        HTTPException: Nếu xác thực thất bại hoặc không có quyền truy cập
    """

    # Detect System Integrator token
    if SystemIntegratorTokenDetector.is_system_integrator_request(
        f"Bearer {auth_token.credentials}"
    ):
        # Handle System Integrator flow
        middleware = SystemIntegratorMiddleware()
        await middleware.handle_system_integrator_request(
            req, auth_token.credentials
        )
        return

    # === EXISTING LOGIC - UNCHANGED ===
    # Regular service-to-service authentication

    # 1. Xác thực auth token từ request
    auth_client = AuthClient(auth_token.credentials)
    validated_user_token = await auth_client.validate_token(
        service_id, service_config.BASE_SERVICE_ID, user_token
    )

    # 2. Xác thực quyền
    route = req.scope["root_path"] + req.scope["route"].path
    introspector = TokenIntrospectRPCClient(validated_user_token)

    introspected_result = await introspector.check_permission(
        route, req.method
    )

    if not introspected_result.can_action:
        raise HTTPException(
            status_code=401,
            detail="Không có quyền truy cập vào tài nguyên này",
        )

    requester = introspected_result

    # 3. Set requester to res.state
    req.state.requester = requester
    req.state.user_token = validated_user_token
