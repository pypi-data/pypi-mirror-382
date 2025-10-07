from abc import abstractmethod


class ServiceBaseContract:
    @abstractmethod
    def paginate(
        self, pagination_params, conditions=None, with_trash: bool = False
    ):
        pass

    @abstractmethod
    def get_all(self):
        pass

    @abstractmethod
    async def find(self, id: str) -> dict:
        pass

    @abstractmethod
    async def create(self, data: dict) -> dict:
        pass

    @abstractmethod
    async def update(self, id: str, data: dict) -> dict:
        pass

    @abstractmethod
    async def delete(self, id: str, is_hard_delete=False) -> dict:
        pass
