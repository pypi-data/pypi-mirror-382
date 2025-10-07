"""
Worker logging module cho queue processing với detailed activity tracking.

Module này cung cấp logging chuyên biệt cho:
- Worker lifecycle (start, stop, error)
- Queue message processing
- Performance metrics
- Error handling và retry logic
"""

import asyncio
import time
from enum import Enum
from typing import Any

from cores.logger.enhanced_logging import LogCategory, log_performance, logger


class WorkerStatus(str, Enum):
    """Enum cho worker status"""

    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    ERROR = "error"


class MessageStatus(str, Enum):
    """Enum cho message processing status"""

    RECEIVED = "received"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


class WorkerLogger:
    """
    Specialized logger cho worker operations với detailed tracking.
    """

    def __init__(self, worker_name: str):
        self.worker_name = worker_name
        self.start_time = None
        self.message_count = 0
        self.error_count = 0
        self.success_count = 0

    def log_worker_lifecycle(
        self, status: WorkerStatus, extra_fields: dict[str, Any] | None = None
    ) -> None:
        """Log worker lifecycle events"""

        fields = {
            "worker_name": self.worker_name,
            "status": status.value,
            "timestamp": time.time(),
            **(extra_fields or {}),
        }

        if status == WorkerStatus.STARTING:
            self.start_time = time.time()
            fields["start_time"] = self.start_time
            message = f"Worker {self.worker_name} is starting"
            level = "INFO"

        elif status == WorkerStatus.RUNNING:
            message = f"Worker {self.worker_name} is now running"
            level = "INFO"

        elif status == WorkerStatus.STOPPING:
            message = f"Worker {self.worker_name} is stopping"
            level = "INFO"

        elif status == WorkerStatus.STOPPED:
            uptime = round(time.time() - self.start_time, 2) if self.start_time else 0
            fields.update(
                {
                    "uptime_seconds": uptime,
                    "total_messages": self.message_count,
                    "successful_messages": self.success_count,
                    "failed_messages": self.error_count,
                }
            )
            message = f"Worker {self.worker_name} stopped after {uptime}s (processed {self.message_count} messages)"
            level = "INFO"

        elif status == WorkerStatus.ERROR:
            message = f"Worker {self.worker_name} encountered an error"
            level = "ERROR"

        logger._create_log_record(level, message, LogCategory.WORKER, fields)

    def log_message_processing(
        self,
        message_id: str,
        status: MessageStatus,
        duration_ms: float | None = None,
        extra_fields: dict[str, Any] | None = None,
    ) -> None:
        """Log message processing events"""

        fields = {
            "worker_name": self.worker_name,
            "message_id": message_id,
            "status": status.value,
            "timestamp": time.time(),
            **(extra_fields or {}),
        }

        if duration_ms is not None:
            fields["duration_ms"] = duration_ms

        if status == MessageStatus.RECEIVED:
            message = f"Worker {self.worker_name} received message {message_id}"
            level = "DEBUG"

        elif status == MessageStatus.PROCESSING:
            message = f"Worker {self.worker_name} processing message {message_id}"
            level = "DEBUG"

        elif status == MessageStatus.COMPLETED:
            self.success_count += 1
            self.message_count += 1
            message = f"Worker {self.worker_name} completed message {message_id}"
            if duration_ms:
                message += f" in {duration_ms}ms"
            level = "INFO"

        elif status == MessageStatus.FAILED:
            self.error_count += 1
            self.message_count += 1
            message = (
                f"Worker {self.worker_name} failed to process message {message_id}"
            )
            level = "ERROR"

        elif status == MessageStatus.RETRYING:
            message = f"Worker {self.worker_name} retrying message {message_id}"
            level = "WARNING"

        elif status == MessageStatus.DEAD_LETTER:
            message = f"Worker {self.worker_name} sent message {message_id} to dead letter queue"
            level = "ERROR"

        logger._create_log_record(level, message, LogCategory.WORKER, fields)

    def log_queue_metrics(self, queue_name: str, metrics: dict[str, Any]) -> None:
        """Log queue performance metrics"""

        fields = {
            "worker_name": self.worker_name,
            "queue_name": queue_name,
            "metrics": metrics,
            "timestamp": time.time(),
        }

        message = f"Queue metrics for {queue_name}: {metrics}"
        logger._create_log_record("INFO", message, LogCategory.PERFORMANCE, fields)

    def log_worker_error(
        self, error: Exception, context: dict[str, Any] | None = None
    ) -> None:
        """Log worker errors với detailed context"""

        fields = {
            "worker_name": self.worker_name,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context or {},
            "timestamp": time.time(),
        }

        message = f"Worker {self.worker_name} error: {str(error)}"
        logger._create_log_record(
            "ERROR", message, LogCategory.WORKER, fields, exc_info=True
        )


class MessageProcessor:
    """
    Context manager để track message processing với automatic logging.
    """

    def __init__(
        self,
        worker_logger: WorkerLogger,
        message_id: str,
        message_data: dict[str, Any] | None = None,
    ):
        self.worker_logger = worker_logger
        self.message_id = message_id
        self.message_data = message_data or {}
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        self.worker_logger.log_message_processing(
            self.message_id,
            MessageStatus.PROCESSING,
            extra_fields={"message_data": self.message_data},
        )
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (
            round((time.time() - self.start_time) * 1000, 2) if self.start_time else 0
        )

        if exc_type is None:
            # Success
            self.worker_logger.log_message_processing(
                self.message_id, MessageStatus.COMPLETED, duration_ms=duration_ms
            )
        else:
            # Error
            self.worker_logger.log_message_processing(
                self.message_id,
                MessageStatus.FAILED,
                duration_ms=duration_ms,
                extra_fields={
                    "error_type": exc_type.__name__,
                    "error_message": str(exc_val),
                },
            )


def log_worker_performance(worker_name: str):
    """Decorator để log performance của worker methods"""

    def decorator(func):
        return log_performance(
            f"worker.{worker_name}.{func.__name__}", LogCategory.WORKER
        )(func)

    return decorator


class WorkerMetricsCollector:
    """
    Collector để thu thập và log worker metrics định kỳ.
    """

    def __init__(self, collection_interval: float = 60.0):
        self.collection_interval = collection_interval
        self.workers: dict[str, WorkerLogger] = {}
        self.running = False

    def register_worker(self, worker_logger: WorkerLogger) -> None:
        """Register worker để collect metrics"""
        self.workers[worker_logger.worker_name] = worker_logger

    def unregister_worker(self, worker_name: str) -> None:
        """Unregister worker"""
        self.workers.pop(worker_name, None)

    async def start_collection(self) -> None:
        """Start metrics collection loop"""
        self.running = True

        logger.info(
            "Starting worker metrics collection",
            category=LogCategory.WORKER,
            extra_fields={"collection_interval": self.collection_interval},
        )

        while self.running:
            try:
                await self._collect_metrics()
                await asyncio.sleep(self.collection_interval)
            except Exception as e:
                logger.error(
                    f"Error collecting worker metrics: {str(e)}",
                    category=LogCategory.WORKER,
                    exc_info=True,
                )
                await asyncio.sleep(self.collection_interval)

    def stop_collection(self) -> None:
        """Stop metrics collection"""
        self.running = False
        logger.info("Stopped worker metrics collection", category=LogCategory.WORKER)

    async def _collect_metrics(self) -> None:
        """Collect và log metrics từ tất cả workers"""

        if not self.workers:
            return

        total_messages = sum(w.message_count for w in self.workers.values())
        total_errors = sum(w.error_count for w in self.workers.values())
        total_success = sum(w.success_count for w in self.workers.values())

        success_rate = (
            (total_success / total_messages * 100) if total_messages > 0 else 0
        )

        metrics = {
            "active_workers": len(self.workers),
            "total_messages_processed": total_messages,
            "total_successful": total_success,
            "total_errors": total_errors,
            "success_rate_percent": round(success_rate, 2),
            "worker_details": {
                name: {
                    "messages": worker.message_count,
                    "success": worker.success_count,
                    "errors": worker.error_count,
                    "uptime": round(time.time() - worker.start_time, 2)
                    if worker.start_time
                    else 0,
                }
                for name, worker in self.workers.items()
            },
        }

        logger.info(
            "Worker system metrics",
            category=LogCategory.PERFORMANCE,
            extra_fields=metrics,
        )


# Global metrics collector
metrics_collector = WorkerMetricsCollector()


# Convenience functions
def create_worker_logger(worker_name: str) -> WorkerLogger:
    """Tạo worker logger và register với metrics collector"""
    worker_logger = WorkerLogger(worker_name)
    metrics_collector.register_worker(worker_logger)
    return worker_logger


def log_worker_startup(worker_name: str, config: dict[str, Any]) -> WorkerLogger:
    """Log worker startup với configuration"""
    worker_logger = create_worker_logger(worker_name)

    logger.info(
        f"Starting worker: {worker_name}",
        category=LogCategory.WORKER,
        extra_fields={
            "worker_name": worker_name,
            "config": config,
            "action": "startup",
        },
    )

    worker_logger.log_worker_lifecycle(WorkerStatus.STARTING, {"config": config})
    return worker_logger


def log_worker_shutdown(worker_logger: WorkerLogger, reason: str = "normal") -> None:
    """Log worker shutdown"""

    logger.info(
        f"Shutting down worker: {worker_logger.worker_name}",
        category=LogCategory.WORKER,
        extra_fields={
            "worker_name": worker_logger.worker_name,
            "reason": reason,
            "action": "shutdown",
        },
    )

    worker_logger.log_worker_lifecycle(
        WorkerStatus.STOPPED, {"shutdown_reason": reason}
    )
    metrics_collector.unregister_worker(worker_logger.worker_name)


# Export public API
__all__ = [
    "WorkerLogger",
    "WorkerStatus",
    "MessageStatus",
    "MessageProcessor",
    "WorkerMetricsCollector",
    "log_worker_performance",
    "metrics_collector",
    "create_worker_logger",
    "log_worker_startup",
    "log_worker_shutdown",
]
