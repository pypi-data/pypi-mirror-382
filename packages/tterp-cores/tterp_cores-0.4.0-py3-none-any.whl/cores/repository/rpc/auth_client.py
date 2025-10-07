from cores.config import service_config
from cores.model.base_error import UnauthorizeError
from cores.repository.rpc.client_base import ClientBase


class AuthClient(ClientBase):
    def __init__(self, jwt_token) -> None:
        self._base_url = service_config.AUTH_BASE_URL
        self._jwt_token = jwt_token

    async def validate_token(
        self,
        service_management_id: str,
        target_service_id: str,
        user_token: str,
    ) -> bool | str:
        external_headers = {
            "service-management-id": service_management_id,
            "target-service-id": target_service_id,
            "user-token": user_token,
        }

        rs = await self.curl_api(
            "POST", "validate", {}, external_headers=external_headers
        )

        if not rs:
            raise UnauthorizeError("Auth token không hợp lệ!")

        if rs.get("valid") is True:
            return True

        if user_token := rs.get("user_token"):
            return user_token

        raise UnauthorizeError(rs.get("detail", "Authorization failed"))
