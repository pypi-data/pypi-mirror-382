from fastapi.security import HTTPBearer

from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase

SECURITY_ALGORITHM = "HS256"

reusable_oauth2 = HTTPBearer(scheme_name="Authorization")


class UserClient(ClientBase):
    def __init__(self, user_token=None) -> None:
        self.user_token = user_token

    async def _initialize(self) -> "UserClient":
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

        # ApiLogger.debug(self._headers, self._jwt_token)

        return self

    async def _send_request(
        self,
        method: str,
        endpoint: str,
        data: dict | None = None,
        params: dict | None = None,
    ) -> dict:
        """Helper method to send authenticated API requests."""
        return await self.curl_api_with_auth(
            self._initialize,
            method=method,
            uri=endpoint,
            body=data or {},
            params=params or {},
        )

    # User-related methods
    async def login(self, email: str, password: str) -> dict:
        """Login user with email and password"""
        data = {"email": email, "password": password}
        return await self._send_request("POST", "users/login", data)

    async def get_user_by_token(self) -> dict:
        return await self._send_request("GET", "/api/current-user")

    async def get_me(self) -> dict:
        return await self._send_request("GET", "users/users/me/")

    async def get_my_permissions(self) -> dict:
        """Lấy danh sách quyền của người dùng hiện tại"""
        return await self._send_request("GET", "users/users/me/permissions")

    async def find(self, user_id: str) -> dict:
        return await self._send_request("GET", f"users/{user_id}")

    async def get_users(
        self,
        page: int = 1,
        page_size: int = 15,
        order: str = "asc",
        exist_ids: str | None = "",
    ) -> dict:
        params = {"page": page, "page_size": page_size, "order": order}
        if exist_ids:
            params["exist_ids"] = exist_ids
        return await self._send_request("GET", "users/", params=params)

    async def create_user(self, data: dict) -> dict:
        return await self._send_request("POST", "users/register", data)

    async def dispatch_user(self, user_id: str) -> dict:
        return await self._send_request(
            "POST", f"users/es/build-by-id/{user_id}"
        )

    async def send_task(self, user_id: str, countdown: int = 1) -> dict:
        return await self._send_request(
            "GET",
            f"users/user-task/{user_id}",
            params={"countdown": countdown},
        )

    async def search(
        self,
        field: str,
        value: str,
        is_absolute: bool = False,
        is_get_first: bool = True,
    ) -> dict:
        params = {
            "field": field,
            "value": value,
            "is_absolute": is_absolute,
            "is_get_first": is_get_first,
        }
        return await self._send_request(
            "GET", "users/user/search", params=params
        )

    # User group methods
    async def find_user_group(self, user_group_id: str) -> dict:
        return await self._send_request("GET", f"user-groups/{user_group_id}")

    async def search_user_group(
        self, field: str, value: str, is_absolute: bool = False
    ) -> dict:
        params = {"field": field, "value": value, "is_absolute": is_absolute}
        return await self._send_request(
            "GET", "user-groups/user-group/search", params=params
        )

    async def get_user_groups(
        self,
        page: int = 1,
        page_size: int = 15,
        except_ids: str | None = None,
        exist_ids: str | None = None,
    ) -> dict:
        params: dict = {"page": page, "page_size": page_size}
        if except_ids:
            params["except_ids"] = except_ids
        if exist_ids:
            params["exist_ids"] = exist_ids
        return await self._send_request(
            "GET", "user-groups/admin/list", params=params
        )

    # Resource and permission methods
    async def get_user_resources(self, user_id: str) -> dict:
        return await self._send_request(
            "GET", f"user-resources/user/{user_id}"
        )

    async def check_permission(
        self, route: str, method: str, table_management_id: str | None = None
    ) -> dict:
        data = {"route": route, "method": method}
        if table_management_id is not None:
            data["table_management_id"] = table_management_id
        return await self._send_request(
            "POST", "permission_assignments/check_permission", data
        )

    # Token and secret key methods
    async def validate_token(self) -> dict:
        return await self._send_request("GET", "users/token/validation")

    async def get_secret_key(
        self, service_management_id: str = "profile"
    ) -> dict:
        return await self._send_request(
            "GET", f"users/secret-key/{service_management_id}"
        )
