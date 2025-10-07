from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class ModelStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    DELETED = "deleted"


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel, populate_by_name=True, from_attributes=True
    )


class MakeOptional(BaseModel):
    @classmethod
    def __pydantic_init_subclass__(cls, **kwargs: Any) -> None:
        super().__pydantic_init_subclass__(**kwargs)

        for field in cls.model_fields.values():
            if field.is_required():
                field.default = None

        cls.model_rebuild(force=True)


T = TypeVar("T")


class ResponseSchemaBase(BaseModel):
    __abstract__ = True

    code: str = ""
    message: str = ""

    def custom_response(self, code: str, message: str):
        self.code = code
        self.message = message
        return self

    def success_response(self):
        self.code = "200"
        self.message = "Success"
        return self


class DataResponse(ResponseSchemaBase, BaseModel, Generic[T]):
    data: T | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    def custom_response(self, code: str, message: str, data: T):
        self.code = code
        self.message = message
        self.data = data
        return self

    def success_response(self, data: T):
        self.code = "200"
        self.message = "Success"
        self.data = data
        return self
