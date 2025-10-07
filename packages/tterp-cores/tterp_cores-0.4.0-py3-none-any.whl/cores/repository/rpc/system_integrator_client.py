"""
RPC Client để interact với System Integrator endpoints
"""


from cores.config import service_config
from cores.model.system_integrator import (
    InvalidClientError,
    SystemIntegratorIntrospectResponse,
    SystemIntegratorPermissionResponse,
    SystemIntegratorTokenResponse,
    SystemIntegratorValidationResponse,
)
from cores.repository.rpc.client_base import ClientBase


class SystemIntegratorAuthClient(ClientBase):
    """Client để interact với Auth Service System Integrator endpoints"""

    def __init__(self):
        super().__init__()
        self._base_url = service_config.AUTH_BASE_URL

    async def authenticate_client_credentials(
        self, client_id: str, client_secret: str, scope: str | None = None
    ) -> SystemIntegratorTokenResponse:
        """Authenticate và lấy access token"""

        request_data = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grant_type": "client_credentials",
        }

        if scope:
            request_data["scope"] = scope

        try:
            response = await self.curl_api(
                "POST", "system-integrator/authenticate", request_data
            )

            return SystemIntegratorTokenResponse(**response)

        except Exception as e:
            raise InvalidClientError(f"Authentication failed: {str(e)}")

    async def validate_token(
        self, access_token: str, target_service_id: str
    ) -> SystemIntegratorValidationResponse:
        """Validate System Integrator token"""

        try:
            response = await self.curl_api(
                "POST",
                "system-integrator/validate",
                {},
                external_headers={
                    "Authorization": f"Bearer {access_token}",
                    "target-service-id": target_service_id,
                },
            )

            return SystemIntegratorValidationResponse(**response)

        except Exception as e:
            return SystemIntegratorValidationResponse(
                valid=False, error_message=str(e)
            )


class SystemIntegratorUserClient(ClientBase):
    """Client để interact với User Service System Integrator endpoints"""

    def __init__(self):
        super().__init__()
        self._base_url = service_config.USER_BASE_URL

    async def introspect_token(
        self, user_token: str
    ) -> SystemIntegratorIntrospectResponse:
        """Introspect System Integrator user token"""

        try:
            response = await self.curl_api(
                "POST",
                "system-integrator/introspect",
                {},
                external_headers={"user-token": user_token},
            )

            # Response format: {"data": {...}}
            if "data" in response:
                return SystemIntegratorIntrospectResponse(**response["data"])
            else:
                return SystemIntegratorIntrospectResponse(**response)

        except Exception as e:
            raise InvalidClientError(f"Token introspection failed: {str(e)}")

    async def check_permission(
        self,
        route: str,
        method: str,
        user_token: str,
        table_management_id: str | None = None,
    ) -> SystemIntegratorPermissionResponse:
        """Check permission cho System Integrator"""

        request_data = {"route": route, "method": method}

        if table_management_id:
            request_data["table_management_id"] = table_management_id

        try:
            response = await self.curl_api(
                "POST",
                "system-integrator/check-permission",
                request_data,
                external_headers={"user-token": user_token},
            )

            return SystemIntegratorPermissionResponse(**response)

        except Exception as e:
            return SystemIntegratorPermissionResponse(
                can_action=False,
                user_id=-1,
                client_id="unknown",
                reason=f"Permission check failed: {str(e)}",
            )


class SystemIntegratorHelperService:
    """Helper service cho external integrators"""

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token: str | None = None
        self._auth_client = SystemIntegratorAuthClient()

    async def authenticate(self) -> str:
        """Authenticate và cache access token"""

        response = await self._auth_client.authenticate_client_credentials(
            self.client_id, self.client_secret
        )

        self._access_token = response.access_token
        return self._access_token

    def get_api_headers(self) -> dict:
        """Get headers for API calls"""

        if not self._access_token:
            raise ValueError(
                "Must authenticate first. Call authenticate() method."
            )

        return {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

    async def test_api_call(self, endpoint: str, method: str = "GET") -> dict:
        """Test API call với current token"""

        if not self._access_token:
            await self.authenticate()

        headers = self.get_api_headers()

        # This would be implemented by the specific service
        # For now, just return the headers that should be used
        return {
            "endpoint": endpoint,
            "method": method,
            "headers": headers,
            "note": "Use these headers to call the API endpoint",
        }
