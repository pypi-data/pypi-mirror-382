"""
Enhanced logging system package với backward compatibility.

Exports:
- EnhancedLogger (new system)
- ApiLogger (backward compatibility alias)
- Health check utilities
- Worker logging utilities
- Middleware components
"""

# Import enhanced logging system
from .enhanced_logging import (
    ApiLogger,  # Backward compatibility alias
    EnhancedLogger,
    LogCategory,
    LogContext,
    LogLevel,
    log_business_action,
    log_performance,
    logger,
)

# Import health check utilities
from .health_check import (
    HealthCheckService,
    health_check_service,
    startup_health_checks,
)

# Keep old imports for backward compatibility
from .logging import ApiLogger as LegacyApiLogger
from .logging_setup import ELKLogger

# Import worker logging utilities
from .worker_logging import (
    MessageProcessor,
    MessageStatus,
    WorkerLogger,
    WorkerMetricsCollector,
    WorkerStatus,
    create_worker_logger,
    log_worker_performance,
    log_worker_shutdown,
    log_worker_startup,
    metrics_collector,
)

# Export everything
__all__ = [
    # Enhanced logging system
    "EnhancedLogger",
    "LogLevel",
    "LogCategory",
    "LogContext",
    "log_performance",
    "log_business_action",
    "logger",
    "ApiLogger",
    # Health check
    "HealthCheckService",
    "health_check_service",
    "startup_health_checks",
    # Worker logging
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
    # Legacy compatibility
    "LegacyApiLogger",
    "ELKLogger",
]
