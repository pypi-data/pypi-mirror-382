# cores/outbox/models.py
import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.dialects.mysql import JSON
from sqlalchemy.types import Enum as SAEnum

from cores.component.sqlalchemy import Base


class OutboxEventStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"


class OutboxEvent(Base):
    __tablename__ = "outbox_events"

    id = Column(String(36), primary_key=True, default=uuid.uuid4)
    aggregate_id = Column(
        String(255),
        nullable=False,
        index=True,
        comment="ID của đối tượng nghiệp vụ (ví dụ: notification_id)",
    )
    topic = Column(
        String(255), nullable=False, comment="Tên routing key/topic của RabbitMQ"
    )
    payload = Column(JSON, nullable=False, comment="Nội dung của event")
    status = Column(
        SAEnum(OutboxEventStatus),
        default=OutboxEventStatus.PENDING,
        nullable=False,
        index=True,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    # Retry/Backoff fields
    retry_count = Column(Integer, nullable=False, default=0)
    next_retry_at = Column(DateTime, nullable=True)
    last_error_at = Column(DateTime, nullable=True)
    last_error_type = Column(String(255), nullable=True)
    error_context = Column(JSON, nullable=True)
    dead = Column(Boolean, nullable=False, default=False)

    __table_args__ = {"mysql_engine": "InnoDB"}
