from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase


class ServiceManagementClient(ClientBase):
    async def _initialize(self):
        self._base_url = service_config.AUTH_BASE_URL
        await self.set_jwt_token_and_headers(
            target_service_id=service_config.PROFILE_SERVICE_ID
        )

        return self

    async def get_tables(self):
        return await self.curl_api_with_auth(
            self._initialize, "GET", "table-managements"
        )

    async def find_table(self, id: str):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"table-managements/{id}"
        )

    async def get_services(self):
        params = {
            "page": 1,
            "page_size": 999,
        }
        return await self.curl_api_with_auth(
            self._initialize, "GET", "service-managements/", params
        )

    async def find_service(self, id: str):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"service-managements/{id}"
        )
