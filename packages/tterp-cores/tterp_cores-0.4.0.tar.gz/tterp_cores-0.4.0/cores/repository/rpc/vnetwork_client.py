import hashlib
import hmac
import json
from datetime import datetime
from random import randint

import httpx

from cores.config.config import config
from cores.logging import get_curl_logger
from cores.repository.rpc.client_base import ClientBase

logger = get_curl_logger()


class VNetworkClient(ClientBase):
    def __init__(self, app_key=config("USER_jwt_token", "")) -> None:
        self._base_url = config("VNETWORK_BASE_URL")
        self._accesskey = str(config("VNETWORK_ACCESS_KEY"))
        self._secretkey = str(config("VNETWORK_SECRET_KEY"))
        now = datetime.now()
        self.request_time = now.strftime("%Y%m%dT%H%M%SZ")
        self.nonce = str(randint(10000, 99999))

    async def curl_api(
        self,
        method="GET",
        uri="",
        body: dict = {},
        params: dict = {},
        response_type="json",
    ):
        # timeout = httpx.TimeoutConfig(connect_timeout=5, read_timeout=None, write_timeout=5)
        headers = {
            "Authorization": self.get_signature(uri, method, body),
            "Content-Type": "application/json; charset=utf-8",
            "x-sfd-date": self.request_time,
            "x-sfd-nonce": self.nonce,
        }
        if self._jwt_token:
            headers["Authorization"] = "Bearer " + self._jwt_token
        # print(headers)
        client = httpx.AsyncClient(timeout=10, headers=headers, app=self._app)
        err_message = ""
        try:
            r = None
            link = self._base_url + uri

            if method in ["get", "GET"]:
                r = await client.get(link, headers=headers, params=body)

            elif method in ["post", "POST"]:
                r = await client.post(
                    link, headers=headers, json=body, params=params
                )
            elif method in ["put", "PUT"]:
                r = await client.put(
                    link, headers=headers, json=body, params=params
                )
            elif method in ["delete", "DELETE"]:
                r = await client.request(
                    "delete", link, headers=headers, json=body
                )
            try:
                if response_type == "binary":
                    from io import BytesIO

                    if r.status_code == 200:
                        response = BytesIO(r.content)
                else:
                    response = r.json()
                    print(response)
            except BaseException:
                err_message = r
                raise
            if "status_code" not in response and type(response) is dict:
                response["status_code"] = r.status_code

            return response
        except httpx.HTTPError as exc:
            logger.error(
                f"HTTP Exception - {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except httpx.NetworkError as exc:
            logger.error(
                f"NetworkError for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except httpx.TimeoutException as exc:
            logger.error(
                f"TimeoutException for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except httpx.ProtocolError as exc:
            logger.error(
                f"ProtocolError for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except httpx.DecodingError as exc:
            logger.error(
                f"DecodingError for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except httpx.TooManyRedirects as exc:
            logger.error(
                f"TooManyRedirects for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except httpx.StreamError as exc:
            logger.error(
                f"StreamError for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        except Exception as exc:
            logger.error(
                f"Err for {link}, method: {method}, param: {params}, body: {body} - {err_message} - {exc}"
            )
        finally:
            await client.aclose()

    def get_signature(self, uri, method, body_request=None):
        message = (
            method
            + "\n"
            + uri
            + "\n"
            + self.request_time
            + "\n"
            + self.nonce
            + "\n"
            + self._accesskey
            + "\n"
        )
        if body_request:
            message = message + json.dumps(body_request)
        sig = (
            "HMAC-SHA256 "
            + self._accesskey
            + ":"
            + hmac.new(
                self._secretkey.encode("UTF-8"),
                msg=message.encode(),
                digestmod=hashlib.sha256,
            ).hexdigest()
        )
        return sig

    async def add_stream(self, app_name, stream_name):
        uri = "/v4.4.3/stream"
        body = {
            "app": app_name,
            "stream": stream_name,
            "enable_record": "hls",
            # "client_ip": "",
            "input": "srt",
            "outputs": ["rtmp", "http-flv", "hls"],
            "storage": config("VNETWORK_STORAGE_PATH"),
        }
        return await self.curl_api("POST", uri, body)

    async def get_stream(self, app_name, stream_name):
        uri = f"/v4.4.3/app/{app_name}/stream/{stream_name}"
        return await self.curl_api("GET", uri)

    async def forbid_stream(self, app_name, stream_name):
        uri = f"/v4.4.3/app/{app_name}/stream/{stream_name}/forbid"
        return await self.curl_api("PUT", uri)
