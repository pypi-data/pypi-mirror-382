# cores/events/interfaces.py
from abc import ABC, abstractmethod

from ..events.schemas.base_event import Event


class IEventPublisher(ABC):
    """
    Interface cho việc publish event.
    Việc triển khai cụ thể sẽ quyết định event được ghi vào Outbox DB hay gửi trực tiếp ra Message Broker.
    """
    @abstractmethod
    async def publish(self, event: Event):
        """Gửi đi một event."""
        raise NotImplementedError

    @abstractmethod
    async def publish_many(self, events: list[Event]):
        """Gửi đi nhiều event."""
        raise NotImplementedError
