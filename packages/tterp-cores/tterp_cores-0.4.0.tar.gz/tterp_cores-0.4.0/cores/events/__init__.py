"""
Events module - Cung cấp các thành phần cho hệ thống sự kiện
"""

# Lớp trừu tượng cho Message Broker
from .event_bus import EventBus, InMemoryEventBus, RabbitMQEventBus

# Các lớp Publisher để service sử dụng
from .interfaces import IEventPublisher
from .publisher import OutboxEventPublisher

__all__ = [
    # Broker Abstractions
    "EventBus",
    "RabbitMQEventBus",
    "InMemoryEventBus",
    # Publisher Abstractions & Implementations
    "IEventPublisher",
    "DirectEventPublisher",
    "OutboxEventPublisher",
]
