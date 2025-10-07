from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field


class PagingDTO(BaseModel):
    page: int = Field(1, ge=1, description="Page number, must be at least 1")
    page_size: int = Field(
        10,
        ge=1,
        le=1000000,
        description="Limit per page, must be between 1 and 100",
    )
    total: int | None = Field(
        None, ge=0, description="Total number of items, optional"
    )
    sort_by: str = "id"
    order: str = "desc"

    model_config = {
        "json_schema_extra": {
            "example": {
                "page": 1,
                "limit": 10,
            }
        }
    }


T = TypeVar("T")
C = TypeVar("C")


class MetadataSchema(BaseModel):
    current_page: int
    page_size: int
    total_items: int | None


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


class BasePage(ResponseSchemaBase, BaseModel, Generic[T], ABC):
    data: Sequence[T]

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )

    @classmethod
    @abstractmethod
    def create(
        cls: type[C],
        data: Sequence[T],
        paging: PagingDTO,
        code: str,
        message: str,
    ) -> C:
        pass  # pragma: no cover


class Page(BasePage[T], Generic[T]):
    metadata: MetadataSchema

    @classmethod
    def create(
        cls,
        data: Sequence[T],
        paging: PagingDTO,
        code: str = "200",
        message: str = "Success",
    ) -> "Page[T]":
        return cls(
            code=code,
            message=message,
            data=data,  # type: ignore
            metadata=MetadataSchema(  # type: ignore
                current_page=paging.page,
                page_size=paging.page_size,
                total_items=paging.total,
            ),
        )
