"""Database configuration module
"""

import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseConfig(BaseSettings):
    """Cấu hình cơ sở dữ liệu"""

    # MySQL/MariaDB configuration
    db_host: str = ""
    db_username: str = ""
    db_password: str = ""
    db_database: str = ""
    ECHO_DB_LOG: bool = False

    # Redis configuration
    REDIS_HOST: str = "localhost"
    REDIS_PASSWORD: str = ""
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0

    # MongoDB configuration
    MONGODB_USERNAME: str = "root"
    MONGODB_PASSWORD: str = "root"
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DATABASE: str = "my_database"
    MONGODB_AUTHENTICATION_DATABASE: str = "admin"

    # Firebase configuration
    FIRE_BASE_CRED: str = ""

    model_config = SettingsConfigDict(
        env_file=(
            ".env.testing" if os.getenv("APP_ENV") == "testing" else ".env"
        ),  # Sử dụng .env.testing cho test environment
        extra="ignore",
    )

    def get_sqlalchemy_url(self) -> str:
        """Tạo URL kết nối SQLAlchemy async"""
        return (
            f"mysql+asyncmy://{self.db_username}:{self.db_password}"
            f"@{self.db_host}/{self.db_database}"
            "?charset=utf8mb4"
        )

    def get_sqlalchemy_sync_url(self) -> str:
        """Tạo URL kết nối SQLAlchemy sync cho alembic"""
        return (
            f"mysql+pymysql://{self.db_username}:{self.db_password}"
            f"@{self.db_host}/{self.db_database}"
            "?charset=utf8mb4"
        )

    def get_redis_url(self) -> str:
        """Tạo URL kết nối Redis"""
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else "@"
        return f"redis://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    def get_mongodb_uri(self) -> str:
        """Tạo URI kết nối MongoDB"""
        auth = (
            f"{self.MONGODB_USERNAME}:{self.MONGODB_PASSWORD}@"
            if self.MONGODB_USERNAME
            else ""
        )
        return f"mongodb://{auth}{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DATABASE}"


# Singleton instance
database_config = DatabaseConfig()
