from cores.config.config import config
from cores.repository.rpc.client_base import ClientBase


class SMSClient(ClientBase):
    def __init__(self, app_key=config("USER_jwt_token", "")) -> None:
        self._base_url = config("SMS_BASE_URL")
        self._jwt_token = app_key

    async def send_sms(self, MOBILELIST):
        data = {
            "RQST": {
                "name": "send_sms_list",
                "REQID": "123",
                "LABELID": "181237",
                "CONTRACTTYPEID": "1",
                "CONTRACTID": "14761",
                "TEMPLATEID": "1101680",
                "PARAMS": [{"NUM": "1", "CONTENT": "95333413 "}],
                "SCHEDULETIME": "",
                "MOBILELIST": MOBILELIST,
                "ISTELCOSUB": "0",
                "AGENTID": "199",
                "APIUSER": "btt_api",
                "APIPASS": "M@tkh@u2o20123!@#",
                "USERNAME": "btt_api_sms",
                "DATACODING": "0",
                "SALEORDERID": "",
                "PACKAGEID": "",
            }
        }
        return await self.curl_api("POST", "", data)
