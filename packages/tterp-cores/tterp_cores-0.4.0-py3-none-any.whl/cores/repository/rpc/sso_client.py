from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase


class SSOClient(ClientBase):
    async def _initialize(self):
        from cores.authorization.authorization_helper_v2 import (
            create_auth_token_for_be,
        )

        self._base_url = service_config.SSO_BASE_URL
        self._jwt_token = await create_auth_token_for_be(
            service_config.SERVICE_MANAGEMENT_ID,
            service_config.AUTH_SECRET_KEY,
            service_config.BASE_URL,
            self._base_url,
        )
        return self

    async def check_is_login(self):
        return await self.curl_api("GET", "is-login")

    async def get_info(self):
        return await self.curl_api("GET", "info")

    async def refresh_token(self):
        return await self.curl_api("GET", "refresh-token")
