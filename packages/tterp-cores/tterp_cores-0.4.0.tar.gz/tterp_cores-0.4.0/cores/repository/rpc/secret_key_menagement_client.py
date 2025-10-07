from fastapi import HTTPException
from fastapi.security import HTTPBearer

from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase

SECURITY_ALGORITHM = "HS256"

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


class SecretKeyManagementClient(ClientBase):
    def __init__(self) -> None:
        self._base_url = service_config.USER_BASE_URL

    async def get_secret_key(self) -> str:
        """
        Lấy secret key từ API secret-key-management.
        """

        self._jwt_token = self._generate_jwt_token()

        secret_key_response = await self._fetch_secret_key()
        if not self._is_valid_response(secret_key_response):
            raise HTTPException(
                422,
                detail=secret_key_response.get(
                    "detail", "Get Secret key error"
                ),
            )
        return secret_key_response

    def _generate_jwt_token(self) -> str:
        from cores.depends.authorization import TokenService

        """
        Sinh JWT token với secret key từ cấu hình.
        """
        return TokenService.generate_token(
            data={}, secret_key=service_config.SECRET_KEY_FOR_MANAGEMENT
        )

    async def _fetch_secret_key(self) -> str | dict[str, str]:
        """
        Gửi yêu cầu GET đến API để lấy secret key.
        """
        service_management_id = service_config.BASE_SERVICE_ID
        return await self.curl_api(
            "GET", f"secret-key-management/{service_management_id}"
        )

    def _is_valid_response(self, response) -> bool:
        """
        Kiểm tra xem phản hồi từ API có hợp lệ không.
        """
        if type(response) is str:
            return True
        return response.get("status_code") == 200
