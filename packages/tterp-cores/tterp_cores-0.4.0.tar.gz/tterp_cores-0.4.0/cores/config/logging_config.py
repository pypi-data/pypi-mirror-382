"""
Logging configuration module - Cấu hình cho hệ thống log
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class LoggingConfig(BaseSettings):
    """Cấu hình hệ thống logging"""

    # Log levels
    LOG_LEVEL: str = "INFO"

    # Log formats
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Log file paths
    LOG_DIR: str = "log"
    ERROR_LOG_FILE: str = "error.log"
    ACCESS_LOG_FILE: str = "access.log"

    # Logging backend (Elasticsearch, Filebeat)
    FILEBEAT_HOST: str = "filebeat"
    FILEBEAT_PORT: int = 5044

    ELASTICSEARCH_HOST: str = "elasticsearch"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_USERNAME: str = ""
    ELASTICSEARCH_PASSWORD: str = ""

    # Log configuration
    ENABLE_CONSOLE_LOG: bool = True
    ENABLE_FILE_LOG: bool = True
    ENABLE_JSON_LOG: bool = False
    ENABLE_ELK_LOGGING: bool = False  # Tắt ELK logging mặc định để tránh lỗi TCP connection

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    def get_elasticsearch_url(self) -> str:
        """Tạo URL kết nối Elasticsearch"""
        auth = ""
        if self.ELASTICSEARCH_USERNAME and self.ELASTICSEARCH_PASSWORD:
            auth = f"{self.ELASTICSEARCH_USERNAME}:{self.ELASTICSEARCH_PASSWORD}@"

        return f"http://{auth}{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"

    def get_log_file_path(self, log_type: str = "error") -> str:
        """Tạo đường dẫn tới file log"""
        os.makedirs(self.LOG_DIR, exist_ok=True)

        if log_type.lower() == "access":
            return os.path.join(self.LOG_DIR, self.ACCESS_LOG_FILE)

        return os.path.join(self.LOG_DIR, self.ERROR_LOG_FILE)


# Singleton instance
logging_config = LoggingConfig()
