from datetime import datetime

from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase


class NotifierClient(ClientBase):
    async def _initialize(self) -> "NotifierClient":
        self._base_url = service_config.NOTIFIER_BASE_URL
        await self.set_jwt_token_and_headers(
            target_service_id=service_config.NOTIFIER_SERVICE_ID
        )
        return self

    async def _send_request(
        self, method: str, endpoint: str, data: dict | None = None
    ) -> dict:
        """Helper method to send authenticated API requests."""
        return await self.curl_api_with_auth(
            self._initialize, method=method, uri=endpoint, body=data or {}
        )

    async def push_notify(
        self,
        service_management_id: str,
        table_management_id: str,
        to_list_user_id: list[int],
        subject: str,
        content: str,
        mail_username: str | None = None,
        mail_password: str | None = None,
        event: str | None = None,
        content_type: str = "plain",
        callback_url: str | None = None,
        from_user_id: str = "1",
        item_id: str | None = None,
        channels: list[str] = ["email"],
        save: bool = True,
    ) -> dict:
        data = {
            "service_management_id": service_management_id,
            "table_management_id": table_management_id,
            "to_list_user_id": to_list_user_id,
            "subject": subject,
            "content": content,
            "channels": channels,
            "from_user_id": from_user_id,
            "content_type": content_type,
            "save": save,
            "mail_username": mail_username,
            "mail_password": mail_password,
            "event": event,
            "item_id": item_id,
        }
        if callback_url:
            data["callback_url"] = callback_url

        return await self._send_request("POST", "announce/", data)

    async def send_to_app(
        self, user_ids: list[str], title: str, body: str
    ) -> dict:
        data = {"user_ids": user_ids, "title": title, "body": body}
        return await self._send_request(
            "POST", "announce/send-app-notifications/", data
        )

    async def send_to_email(
        self,
        emails: str,
        subject: str,
        content: str,
        content_type: str = "plain",
    ) -> dict:
        data = {
            "emails": emails,
            "subject": subject,
            "content": content,
            "content_type": content_type,
        }
        return await self._send_request("POST", "announce/email", data)

    async def send_error_message(
        self,
        env: str,
        service_management_id: str,
        error_message: str,
        error_code: str = "500",
        sentry_link: str | None = None,
    ) -> dict:
        data = {
            "env": env,
            "service_management_id": service_management_id,
            "error_message": error_message,
            "error_code": error_code,
            "error_time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        }
        if sentry_link:
            data["sentry_link"] = sentry_link

        return await self._send_request(
            "POST", "announce/send-err-message", data
        )

    async def send_authorization_code(self, data: dict) -> dict:
        return await self._send_request("POST", "announce/code", data)

    async def authorize(self, data: dict) -> dict:
        return await self._send_request("POST", "announce/auth", data)

    async def get_me(self) -> dict:
        return await self._send_request("GET", "announce/me")

    async def get_contacts(self) -> dict:
        return await self._send_request("GET", "announce/contacts")
