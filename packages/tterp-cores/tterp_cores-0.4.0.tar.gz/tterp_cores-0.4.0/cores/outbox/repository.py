# cores/outbox/repository.py
import uuid
from datetime import datetime

from sqlalchemy import and_, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func

from .models import OutboxEvent, OutboxEventStatus


class OutboxRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_event(self, event: OutboxEvent):
        """Thêm một event vào outbox. Hàm này phải được gọi bên trong một transaction đang mở."""
        self.session.add(event)
        await self.session.flush() # Đảm bảo event được đưa vào session

    async def get_pending_events(self, limit: int = 100) -> list[OutboxEvent]:
        """Lấy các event cần xử lý: PENDING hoặc FAILED đến hạn retry, không dead."""
        now_expr = func.now()
        stmt = (
            select(OutboxEvent)
            .where(
                and_(
                    OutboxEvent.dead.is_(False),
                    OutboxEvent.status.in_([OutboxEventStatus.PENDING, OutboxEventStatus.FAILED]),
                    or_(OutboxEvent.next_retry_at.is_(None), OutboxEvent.next_retry_at <= now_expr),
                )
            )
            .order_by(OutboxEvent.created_at, OutboxEvent.retry_count)
            .limit(limit)
            .with_for_update(skip_locked=True)  # Tránh nhiều worker lấy cùng lúc
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def mark_as_processed(self, event_id: uuid.UUID):
        """Đánh dấu event đã được xử lý thành công."""
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(status=OutboxEventStatus.PROCESSED, processed_at=datetime.utcnow())
        )
        await self.session.execute(stmt)

    async def mark_as_failed(self, event_id: uuid.UUID, error_message: str):
        """Đánh dấu event bị lỗi và ghi nội dung lỗi vào cột error."""
        # Cắt bớt lỗi quá dài để tránh vượt quá giới hạn TEXT nếu cần
        truncated_error = error_message if len(error_message) <= 65535 else error_message[:65535]
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=OutboxEventStatus.FAILED,
                processed_at=datetime.utcnow(),
                error=truncated_error,
                last_error_at=datetime.utcnow(),
            )
        )
        await self.session.execute(stmt)

    async def mark_as_failed_retryable(
        self,
        event_id: uuid.UUID,
        error_message: str,
        error_type: str | None,
        next_retry_at: datetime,
        retry_count: int,
        error_context: dict | None = None,
    ):
        truncated_error = error_message if len(error_message) <= 65535 else error_message[:65535]
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=OutboxEventStatus.FAILED,
                error=truncated_error,
                last_error_at=datetime.utcnow(),
                last_error_type=error_type,
                error_context=error_context,
                retry_count=retry_count,
                next_retry_at=next_retry_at,
            )
        )
        await self.session.execute(stmt)

    async def mark_as_dead(
        self,
        event_id: uuid.UUID,
        error_message: str,
        error_type: str | None,
        error_context: dict | None = None,
    ):
        truncated_error = error_message if len(error_message) <= 65535 else error_message[:65535]
        stmt = (
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(
                status=OutboxEventStatus.FAILED,  # hoặc tạo trạng thái DEAD riêng nếu muốn
                dead=True,
                processed_at=datetime.utcnow(),
                error=truncated_error,
                last_error_at=datetime.utcnow(),
                last_error_type=error_type,
                error_context=error_context,
            )
        )
        await self.session.execute(stmt)
