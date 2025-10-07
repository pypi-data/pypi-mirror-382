from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    # App basics
    SERVICE_NAME: str = "royalty-service"
    APP_ENV: str = "local"
    APP_DEBUG: bool = True
    PROJECT_ROOT: str = "."

    # Logging config
    LOG_LEVEL: str = "INFO"
    LOG_DIR: str = "logs"
    ENABLE_CONSOLE_LOG: bool = True
    ENABLE_FILE_LOG: bool = True
    ENABLE_JSON_LOG: bool = True
    LOG_MAX_FILE_SIZE: int = 50 * 1024 * 1024
    LOG_BACKUP_COUNT: int = 10
    LOG_COMPRESS: bool = True

    # Trace filtering
    LOG_PROJECT_ROOT: str | None = None  # alias for PROJECT_ROOT if not set
    LOG_TRACE_LOCAL_ONLY: bool = True
    LOG_TRACE_MAX_FRAMES: int = 0  # 0 means unlimited
    LOG_STACK_MAX_FRAMES: int = 0  # 0 means unlimited
    LOG_INCLUDE_STACK: bool = True

    # Startup healthcheck
    DISABLE_STARTUP_HEALTHCHECK: bool = False
    MYSQL_HEALTHCHECK_URL: str = "mysql://localhost:3306"
    REDIS_URL: str = "redis://localhost:6379"
    AMQP_URL: str = "amqp://localhost:5672"
    HEALTH_CHECK_CRITICAL_SERVICES: str = "mysql"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def EFFECTIVE_PROJECT_ROOT(self) -> str:
        # Prefer LOG_PROJECT_ROOT > PROJECT_ROOT
        return (self.LOG_PROJECT_ROOT or self.PROJECT_ROOT).rstrip("/")

    @property
    def CRITICAL_SERVICES_LIST(self) -> list[str]:
        raw = (self.HEALTH_CHECK_CRITICAL_SERVICES or "").strip()
        if not raw:
            return []
        return [s.strip() for s in raw.split(",") if s.strip()]


core_settings = CoreSettings()
