from cores.config.config import config
from cores.repository.rpc.client_base import ClientBase


class TelegramClient(ClientBase):
    def __init__(self, app_key=config("USER_jwt_token", "")) -> None:
        self._base_url = config("TELEGRAM_base_url")
        self._jwt_token = "bot" + config("TELEGRAM_TOKEN")
        self._chat_id = config("TELEGRAM_CHAT_ID")

    async def get_info(self, page=1, size=15):
        params = {"page": page, "per_page": size}
        return await self.curl_api(
            "GET", self._jwt_token + "/getUpdates/", params
        )

    async def send_message(self, message=""):
        body = {
            "chat_id": self._chat_id,
            "text": message,
        }
        return await self.curl_api(
            "POST", self._jwt_token + "/sendMessage", body
        )
