# src/cores/outbox/worker.py
import asyncio
import json
import logging
import random
from datetime import datetime, timedelta

import aio_pika
from sqlalchemy.ext.asyncio import async_sessionmaker

from ..events.event_bus import RabbitMQEventBus
from .repository import OutboxRepository

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


class OutboxRelayWorker:
    """
    Lớp worker có thể tái sử dụng để xử lý các event trong outbox.
    Chứa logic cốt lõi, độc lập với bất kỳ service cụ thể nào.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker,
        poll_interval: int = 5,
        batch_size: int = 100,
    ):
        """
        Khởi tạo worker.
        :param session_factory: Một async_sessionmaker để tạo session DB.
        :param poll_interval: Khoảng thời gian (giây) giữa các lần quét.
        :param batch_size: Số lượng event tối đa xử lý trong mỗi batch.
        """
        self.session_factory = session_factory
        self.poll_interval = poll_interval
        self.batch_size = batch_size
        self.event_bus = RabbitMQEventBus()
        # Retry policy
        self.max_retries = 12
        self.backoff_base = 5  # seconds
        self.backoff_max = 15 * 60  # seconds
        self.backoff_jitter = 3  # seconds

    def _compute_next_retry(self, retry_count: int) -> datetime:
        # Exponential backoff with jitter, capped
        delay = min(
            self.backoff_base * (2 ** max(0, retry_count - 1)) + random.uniform(0, self.backoff_jitter),
            self.backoff_max,
        )
        return datetime.utcnow() + timedelta(seconds=delay)

    def _is_retryable(self, exc: Exception) -> bool:
        # Conservative default: most broker/network errors are retryable
        retryable_types = (
            aio_pika.exceptions.AMQPError,
            ConnectionError,
            TimeoutError,
        )
        try:
            return isinstance(exc, retryable_types)
        except Exception:
            return True

    async def _process_batch(self):
        """Xử lý một batch các event."""
        await self.event_bus.connect()
        try:
            async with self.session_factory() as session:
                async with session.begin():
                    outbox_repo = OutboxRepository(session)
                    pending_events = await outbox_repo.get_pending_events(
                        limit=self.batch_size
                    )

                    if not pending_events:
                        return

                    logging.info(
                        f"Found {len(pending_events)} pending events. Publishing..."
                    )

                    for event_model in pending_events:
                        try:
                            message_body = json.dumps(
                                {
                                    "event_id": str(event_model.id),
                                    "event_name": event_model.topic,
                                    "created_at": event_model.created_at.isoformat(),
                                    "payload": event_model.payload,
                                }
                            ).encode()

                            message = aio_pika.Message(
                                body=message_body,
                                content_type="application/json",
                                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                                message_id=str(event_model.id),
                            )

                            await self.event_bus.exchange.publish(
                                message, routing_key=event_model.topic
                            )
                            await outbox_repo.mark_as_processed(event_model.id)
                            logging.info(
                                f"Published and marked event {event_model.id} as PROCESSED."
                            )

                        except Exception as e:
                            # Ghi log và cập nhật trạng thái FAILED/DEAD + lịch retry
                            logging.error(
                                f"Failed to publish event {event_model.id}: {e}",
                                exc_info=True,
                            )
                            try:
                                retryable = self._is_retryable(e)
                                error_msg = f"{type(e).__name__}: {e}"
                                error_type = type(e).__name__
                                context = {
                                    "exchange": getattr(self.event_bus, "exchange_name", None),
                                    "routing_key": event_model.topic,
                                    "created_at": event_model.created_at.isoformat() if event_model.created_at else None,
                                }

                                current_retry = getattr(event_model, "retry_count", 0) or 0
                                if retryable and current_retry < self.max_retries:
                                    next_retry_at = self._compute_next_retry(current_retry + 1)
                                    await outbox_repo.mark_as_failed_retryable(
                                        event_model.id,
                                        error_msg,
                                        error_type,
                                        next_retry_at,
                                        current_retry + 1,
                                        context,
                                    )
                                else:
                                    await outbox_repo.mark_as_dead(
                                        event_model.id,
                                        error_msg,
                                        error_type,
                                        context,
                                    )
                            except Exception as mark_err:
                                logging.error(
                                    f"Failed to update failed status for event {event_model.id}: {mark_err}",
                                    exc_info=True,
                                )
                await session.commit()
        except Exception as e:
            logging.error(
                f"An error occurred while processing outbox batch: {e}", exc_info=True
            )
        finally:
            await self.event_bus.disconnect()

    async def run(self):
        """Bắt đầu vòng lặp vô hạn của worker."""
        logging.info(
            f"Starting Outbox Relay Worker. Polling every {self.poll_interval} seconds."
        )
        while True:
            await self._process_batch()
            await asyncio.sleep(self.poll_interval)
