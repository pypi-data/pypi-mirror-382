from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase


class VoteClient(ClientBase):
    async def _initialize(self):
        self._base_url = service_config.VOTE_BASE_URL
        await self.set_jwt_token_and_headers(
            target_service_id=service_config.VOTE_BASE_URL
        )
        return self

    async def create_ballot_user_by_user_id(self, user_id, data):
        return await self.curl_api_with_auth(
            self._initialize, "post", f"users/{user_id}/demo-ballot-user", data
        )

    async def list_criteria_create(self, data):
        return await self.curl_api_with_auth(
            self._initialize, "post", "list-criteria/", data
        )

    async def criteria_create(self, data):
        return await self.curl_api_with_auth(
            self._initialize, "post", "criteria/", data
        )

    async def result_create(self, data):
        return await self.curl_api_with_auth(
            self._initialize, "post", "results/", data
        )

    async def list_criteria_criteria_create(self, list_criteria_id, data):
        return await self.curl_api_with_auth(
            self._initialize,
            "post",
            f"list-criteria/{list_criteria_id}/criteria",
            data,
        )

    async def get_children_with_criteria_and_result(self, parent_id):
        return await self.curl_api_with_auth(
            self._initialize,
            "get",
            f"list-criteria/parent/{parent_id}/criteria",
        )
