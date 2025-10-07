"""
Unified config module - Cung cấp một cổng truy cập duy nhất cho tất cả cấu hình
"""

from .database_config import database_config
from .logging_config import logging_config
from .messaging_config import messaging_config
from .sentry_config import sentry_config
from .service_config import service_config


class Config:
    """Lớp cấu hình chính tích hợp tất cả các cấu hình con"""

    def __init__(self):
        self.db = database_config
        self.service = service_config
        self.messaging = messaging_config
        self.logging = logging_config
        self.sentry = sentry_config

    # Tiện ích mới
    def get_db_url(self) -> str:
        """Lấy URL kết nối database"""
        return self.db.get_sqlalchemy_url()

    def get_rabbitmq_url(self) -> str:
        """Lấy URL kết nối RabbitMQ"""
        return self.messaging.get_rabbitmq_url()

    def get_error_log_path(self) -> str:
        """Lấy đường dẫn file log lỗi"""
        return self.logging.get_log_file_path("error")

    def get_access_log_path(self) -> str:
        """Lấy đường dẫn file log truy cập"""
        return self.logging.get_log_file_path("access")


# Singleton instance
config = Config()
