from datetime import datetime
from typing import Generic, TypeVar

from cores.model.base_model import CamelCaseModel

# Định nghĩa generic type cho Payload
Payload = TypeVar("Payload")


class DTOProps(CamelCaseModel):
    id: str | None = None
    occurred_at: datetime | None = None
    sender_id: str | None = None


class AppEvent(CamelCaseModel, Generic[Payload]):
    event_name: str
    payload: Payload
    dto_props: DTOProps | None = None
