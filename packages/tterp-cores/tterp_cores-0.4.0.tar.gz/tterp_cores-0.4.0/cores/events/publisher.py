# cores/events/publisher.py
from __future__ import annotations

from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ..outbox.models import OutboxEvent
from ..outbox.repository import OutboxRepository
from .interfaces import IEventPublisher
from .schemas.base_event import Event


class OutboxEventPublisher(IEventPublisher):
    """
    Triển khai IEventPublisher để ghi event vào bảng Outbox.
    Tự quản lý session riêng để đảm bảo event được commit sau khi transaction nghiệp vụ thành công.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory
        self._session: AsyncSession | None = None
        self._scope_depth: int = 0  # hỗ trợ re-entrant session scopes

    @asynccontextmanager
    async def session_scope(self):
        """Cung cấp một scope session cho publisher."""
        created_here = False
        if self._session is None:
            # Chỉ tạo session mới nếu chưa có session hiện hữu
            self._session = self._session_factory()
            created_here = True
        self._scope_depth += 1
        try:
            yield self._session
        except Exception:
            # Rollback khi có lỗi
            if self._session is not None:
                await self._session.rollback()
            raise
        finally:
            self._scope_depth -= 1
            # Chỉ đóng session nếu scope hiện tại là nơi đã tạo session
            if created_here and self._session is not None:
                await self._session.close()
                self._session = None

    async def publish(self, event: Event):
        """Ghi một event vào bảng outbox."""
        if self._session is None:
            raise RuntimeError(
                "Publisher session is not active. Use 'async with publisher.session_scope()'."
            )

        outbox_repo = OutboxRepository(self._session)
        payload_dict = event.model_dump(mode="json").get("payload", {})

        outbox_event = OutboxEvent(
            aggregate_id=str(payload_dict.get("item_id") or event.event_id),
            topic=event.event_name,
            payload=payload_dict,
        )
        await outbox_repo.add_event(outbox_event)

    async def publish_many(self, events: list[Event]):
        """Ghi nhiều event vào bảng outbox."""
        for event in events:
            await self.publish(event)
