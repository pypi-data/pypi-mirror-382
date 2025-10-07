"""
Base Event class - Lớp cơ sở cho tất cả các sự kiện
"""

import uuid
from datetime import datetime

from pydantic import Field

from cores.model.base_model import CamelCaseModel


class Event(CamelCaseModel):
    """
    Lớp cơ sở cho tất cả các sự kiện trong hệ thống

    Attributes:
        event_id: UUID duy nhất cho mỗi sự kiện
        event_name: Tên của sự kiện, được sử dụng làm routing key
        created_at: Thời gian tạo sự kiện
    """

    event_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    event_name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
