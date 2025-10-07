from cores.config.config import config
from cores.repository.rpc.client_base import ClientBase


class StreamingClient(ClientBase):
    def __init__(self, app_key=config("USER_jwt_token", "")) -> None:
        self._base_url = config("STREAMING_base_url")
        self._jwt_token = app_key

    async def create_signaling_chanel(self, data):
        return await self.curl_api("POST", "signaling_channel/", data)

    async def get_signaling_chanel(self, role, chanel_arn, stream_arn=None):
        params = {
            "role": role,
            "chanel_arn": chanel_arn,
            "stream_arn": stream_arn,
        }
        return await self.curl_api("GET", "signaling_channel_detail/", params)

    async def get_hls_streaming_session_url(self, stream_arn=None):
        data = {"stream_arn": stream_arn}
        return await self.curl_api("POST", "hls_streaming_session_url/", data)

    async def store_clip(self, data):
        return await self.curl_api("POST", "clip/", data)
