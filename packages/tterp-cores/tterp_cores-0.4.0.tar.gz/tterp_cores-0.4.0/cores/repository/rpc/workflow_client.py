import json

from cores.helpers import helper
from cores.repository.rpc.client_base import ClientBase


class WorkflowClient(ClientBase):
    async def get_by_type(self):
        f = helper.open_file_as_root_path("workflow.json")
        # f = open('workflow.json')
        data = json.load(f)
        f.close()
        return data
        # return await self.curl_api('GET', '/api/current-user')
