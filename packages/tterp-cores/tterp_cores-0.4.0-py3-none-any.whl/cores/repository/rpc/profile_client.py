from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase


class ProfileClient(ClientBase):

    async def _initialize(self):
        self._base_url = service_config.PROFILE_BASE_URL
        await self.set_jwt_token_and_headers(
            target_service_id=service_config.PROFILE_SERVICE_ID
        )

        return self

    async def get_paging_list_user_dep_pos(self, page=1, page_size=10):
        params = {
            "page": page,
            "page_size": page_size,
            "order": "asc",
        }

        return await self.curl_api_with_auth(
            self._initialize, "GET", "user-dep-pos/", params
        )

    async def get_user_dep_pos_by_user_id(
        self, user_id, with_is_primary=False, with_default=True
    ):
        param = {
            "with_is_primary": with_is_primary,
            "with_default": with_default,
        }

        return await self.curl_api_with_auth(
            self._initialize, "GET", f"user-dep-pos/user/{user_id}", param
        )

    async def find_dep(self, id):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"departments/{id}"
        )

    async def find_pos(self, id):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"positions/{id}"
        )

    async def find_expertise(self, id):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"expertise/{id}"
        )

    async def find_by_user_id(self, user_id):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"profiles/admin/user/{user_id}"
        )

    async def find_pos_man(self, id):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"position-management/{id}"
        )

    async def get_pos_man_by_identifier_and_level(self, identifier, level):
        return await self.curl_api_with_auth(
            self._initialize,
            "GET",
            f"position-management/identifier/{identifier}/level/{level}",
        )

    async def get_dep(self, dep_id):
        return await self.curl_api_with_auth(
            self._initialize,
            "GET",
            f"user-dep-pos/?dep_id={dep_id}&page_size=100&page=1",
        )

    async def get_pos_of_dep(self, pos_id, dep_id):
        return await self.curl_api_with_auth(
            self._initialize,
            "GET",
            f"user-dep-pos/?pos_man_id={pos_id}&dep_id={dep_id}",
        )

    async def update_full_name(self, id, full_name):
        return await self.curl_api_with_auth(
            self._initialize,
            "POST",
            "profiles/{id}",
            {"full_name": full_name},
        )

    async def get_paging_list_profiles(
        self,
        page=1,
        per_page=15,
        full_name: str = None,
        dep_names: str = None,
        pos_names: str = None,
        dep_ids: str = None,
        pos_man_ids: str = None,
        pos_man_identifiers: str = None,
        order="desc",
        labor_assessment: bool = None,
        absolute_search: bool = None,
    ):
        params = {"page": page, "page_size": per_page, "order": order}
        if labor_assessment:
            params["labor_assessment"] = labor_assessment
        if full_name:
            params["full_name"] = full_name
        if dep_names:
            params["dep_names"] = dep_names
        if pos_names:
            params["pos_names"] = pos_names
        if dep_ids:
            params["dep_ids"] = dep_ids
        if pos_man_ids:
            params["pos_man_ids"] = pos_man_ids
        if pos_man_identifiers:
            params["pos_man_identifiers"] = pos_man_identifiers

        if absolute_search:
            params["absolute_search"] = absolute_search

        return await self.curl_api_with_auth(
            self._initialize, "GET", "profiles/", params
        )

    async def get_user_dep_pos_by_id(self, id):
        return await self.curl_api_with_auth(
            self._initialize, "GET", f"user-dep-pos/{id}"
        )

    async def get_paging_list_departmens(
        self, page=1, per_page=15, order="desc", names: list = []
    ) -> list:
        params = {"page": page, "page_size": per_page, "order": order}
        if names:
            name_str = ",".join(names)
            params["names"] = name_str

        data = await self.curl_api_with_auth(
            self._initialize, "GET", "departments/", params
        )
        if "data" in data:
            return data["data"]
        return []

    async def get_paging_list_positions(
        self, page=1, per_page=15, order="desc", names: list = []
    ) -> list:
        params = {"page": page, "page_size": per_page, "order": order}
        if names:
            name_str = ",".join(names)
            params["names"] = name_str

        data = await self.curl_api_with_auth(
            self._initialize, "GET", "positions/", params
        )
        if "data" in data:
            return data["data"]
        return []

    async def get_pro_dep_pos(
        self,
        pro_id: int = None,
        dep_id: int = None,
        expertise_id: int = None,
        page=1,
        per_page=15,
        order="desc",
    ):
        params = {
            "page": page,
            "page_size": per_page,
            "order": order,
            "sort_by": "id",
        }
        params.update(
            {"pro_id": pro_id, "dep_id": dep_id, "expertise_id": expertise_id}
        )
        params = {
            key: value for key, value in params.items() if value is not None
        }
        return await self.curl_api_with_auth(
            self._initialize, "GET", "pro-dep-pos/", params
        )

    async def get_pro_dep_pos_by_user_id(self, user_id):

        return await self.curl_api_with_auth(
            self._initialize, "GET", f"pro-dep-pos/user/{user_id}"
        )
