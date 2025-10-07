from fastapi import HTTPException

from cores.config import service_config
from cores.interface.index import (
    CheckPermissionResult,
    TokenIntrospectResult,
    TokenPayloadV2,
)
from cores.repository.rpc.client_base import ClientBase


class TokenIntrospectRPCClient(ClientBase):
    def __init__(self, user_token=None) -> None:
        self.user_token = user_token

    async def _initialize(self):
        from cores.depends.authorization import AuthService

        self._base_url = service_config.USER_BASE_URL
        self._jwt_token = AuthService.create_auth_token(
            service_config.AUTH_SECRET_KEY
        )

        if self.user_token is None:
            # Nếu không truyền user token thì đây là trường hợp service khác
            #  gọi đến các api của user mà không phải xác thực quyền
            self.user_token = await AuthService.create_user_token(
                service_config.BASE_SERVICE_ID
            )

        self._headers = {
            "service-management-id": service_config.BASE_SERVICE_ID,
            "target-service-id": service_config.USER_SERVICE_ID,
            "user-token": self.user_token,
        }
        return self

    async def introspect(self) -> TokenIntrospectResult:
        try:
            result = await self.curl_api_with_auth(
                self._initialize,
                "POST",
                "users/rpc/introspect",
                body={"user_token": self.user_token},
            )
            if not result or not result.get("data"):
                raise HTTPException(401, "User token không hợp lệ")
            payload = TokenPayloadV2(id=result["data"]["id"])
            return TokenIntrospectResult(payload=payload, is_ok=True)
        except Exception as e:
            return TokenIntrospectResult(payload=None, error=e, is_ok=False)

    async def check_permission(
        self, route: str, method: str, table_management_id: str | None = None
    ) -> CheckPermissionResult:
        data = {"route": route, "method": method}
        if table_management_id is not None:
            data["table_management_id"] = table_management_id

        result = await self.curl_api_with_auth(
            self._initialize,
            "POST",
            "permission_assignments/check_permission",
            data,
        )
        if not result.get("can_action"):
            return CheckPermissionResult(False, -1)
        return CheckPermissionResult(
            result["can_action"], int(result["user_id"])
        )
