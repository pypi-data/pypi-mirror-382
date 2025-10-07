
from pydantic import BaseModel

from cores.component.redis_cache import list_cacheable
from cores.config import service_config
from cores.enum.cache import CacheKeyEnum
from cores.model.profile import Profile
from cores.repository.rpc.client_base import ClientBase


class ProfileRPCSearchParams(BaseModel):
    full_name: str | None = None
    dep_names: list[str] | None = None
    pos_names: list[str] | None = None
    expertise_names: list[str] | None = None
    dep_ids: list[int] | None = None
    pos_ids: list[int] | None = None
    expertise_ids: list[int] | None = None
    labor_assessment: bool | None = None
    limit: int = 100


class GetUidsDTO(BaseModel):
    labor_assessment: bool | None = None
    work_object_id: int | None = None


# Base interfaces for repositories


class IProfileQueryRepository:
    def get(self, id: str) -> Profile | None:
        raise NotImplementedError

    def get_by_uids(self, ids: list[int]) -> list[Profile]:
        raise NotImplementedError

    def search_data(self, conditions: ProfileRPCSearchParams) -> list[Profile]:
        raise NotImplementedError

    async def get_uids(self, conddto: GetUidsDTO) -> list[int]:
        raise NotImplementedError


class RPCProfileRepository(IProfileQueryRepository, ClientBase):
    async def _initialize(self):
        self._base_url = service_config.PROFILE_BASE_URL
        await self.set_jwt_token_and_headers(
            target_service_id=service_config.PROFILE_SERVICE_ID
        )
        return self

    async def get(self, id: str) -> Profile | None:
        data = await self.curl_api_with_auth(
            self._initialize, "GET", f"profiles/{id}"
        )
        return Profile(**data)

    async def get_by_uids(self, ids: list[int]) -> list[Profile]:
        data = await self.curl_api_with_auth(
            self._initialize, "POST", "rpc/profiles/by-uids", body=ids
        )
        if not data or data["status_code"] != 200:
            return []
        return [Profile(**item) for item in data["data"]]

    async def search_data(
        self, conditions: ProfileRPCSearchParams
    ) -> list[Profile]:
        data = await self.curl_api_with_auth(
            self._initialize,
            "POST",
            "rpc/profiles/search",
            body=conditions.model_dump(exclude_none=True),
        )
        if not data or data["status_code"] != 200:
            return []
        return [Profile(**item) for item in data["data"]]

    async def get_uids(self, conddto: GetUidsDTO) -> list[int]:
        data = await self.curl_api_with_auth(
            self._initialize,
            "POST",
            "rpc/profiles/get-uids",
            body=conddto.model_dump(exclude_none=True),
        )
        if not data or data["status_code"] != 200:
            return []
        return data["data"]


class ProxyProfileRepository(IProfileQueryRepository):
    def __init__(self, origin):
        self.origin: IProfileQueryRepository = origin
        self.cached: dict[int, Profile] = {}

    # @cacheable(key=CacheKeyEnum.PROFILE, ttl=600)  # Cache kết quả trong 10 phút
    async def get(self, id: str) -> Profile | None:
        try:
            # Gọi đến repository gốc để lấy dữ liệu
            return await self.origin.get(id)
        except Exception as error:
            print(f"Error in proxy repository: {error}")
            return None

    @list_cacheable(
        cache_key_prefix=CacheKeyEnum.USER_PROFILE.value,
        key_to_cache="user_id",
        ttl=99999,
    )
    async def get_by_uids(self, uids: list[int]) -> list[Profile]:
        profiles = await self.origin.get_by_uids(uids)
        return profiles

    async def search_data(
        self, conditions: ProfileRPCSearchParams
    ) -> list[Profile]:
        profiles = await self.origin.search_data(conditions)
        return profiles

    async def get_uids(self, conddto: GetUidsDTO) -> list[int]:
        profiles = await self.origin.get_uids(conddto)
        return profiles

        # try:
        #     if id in self.cached:
        #         return self.cached[id]

        #     brand = self.origin.get(id)
        #     if brand:
        #         self.cached[id] = brand

        #     return brand
        # except Exception as error:
        #     print(f"Error in proxy repository: {error}")
        #     return None
