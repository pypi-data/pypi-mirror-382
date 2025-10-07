"""sqlalchemy.py
Thiết lập **SQLAlchemy Async Engine** & các factory `async_sessionmaker` cho:

1. Database chính
2. Mock database (dùng cho môi trường staging / unit test)
3. SQLite in-file (dùng cho local test)

Cung cấp các dependency ``get_db``... để inject vào FastAPI routes.

Ngoài ra định nghĩa class `Base` giúp các model ORM kế thừa và bổ sung các
phương thức tiện ích `from_dict`, `from_pydantic`, `to_pydantic`.

Refactor: chỉ bổ sung tài liệu, type-hint đầy đủ, sắp xếp lại import (PEP8),
không thay đổi cấu hình hiện có.
"""

from __future__ import annotations

from typing import Any, TypeVar

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import NullPool
from sqlalchemy.sql import text

from cores.config import database_config

_host = database_config.db_host
_username = database_config.db_username
_password = database_config.db_password
_database = database_config.db_database
_engine = create_async_engine(
    (
        f"mysql+asyncmy://{_username}:{_password}@{_host}/{_database}"
        "?charset=utf8mb4"
    ),
    echo=database_config.ECHO_DB_LOG,
    poolclass=NullPool,
    # isolation_level="READ UNCOMMITTED",
    # pool_pre_ping=True,
    # pool_size=5,
    # max_overflow=2
)
async_session = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_engine,  # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
)  # type: ignore

_mock_engine = create_async_engine(
    f"mysql+asyncmy://{_username}:{_password}@{_host}/mock_{_database}"
    "?charset=utf8mb4",
    echo=database_config.ECHO_DB_LOG,
    pool_size=10,  # Số kết nối trong pool
    max_overflow=5,  # Số kết nối vượt quá pool_size
    pool_timeout=30,  # Thời gian chờ kết nối (giây)
    pool_recycle=3600,  # Tái chế kết nối sau 1 giờ
    # isolation_level="READ UNCOMMITTED",
    # pool_pre_ping=True,
    # pool_size=5,
    # max_overflow=2
)
mock_async_session = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_mock_engine,  # type: ignore
    class_=AsyncSession,
    expire_on_commit=False,
)  # type: ignore

SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///test_db.db"
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
session_testing = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


async def get_db() -> AsyncSession:  # type: ignore
    """Dependency lấy session **database chính**."""
    async with async_session() as session:  # type: ignore
        try:
            yield session  # type: ignore
        finally:
            await session.close()


async def get_mock_db() -> AsyncSession:  # type: ignore
    """Dependency lấy session **mock database**."""
    async with mock_async_session() as session:  # type: ignore
        try:
            yield session  # type: ignore
        finally:
            await session.close()


async def ping() -> bool:
    """Health-check đơn giản: SELECT 1."""
    try:
        async with _engine.connect() as conn:
            # Sử dụng `text` để thực hiện truy vấn
            await conn.execute(text("SELECT 1"))
            # Lấy kết quả để đảm bảo truy vấn đã được thực hiện
            return True
    except Exception as e:
        print(f"MySQL health check failed: {e}")
        return False


T = TypeVar("T")


# Base class cho SQLAlchemy ORM
class Base(DeclarativeBase):
    """Declarative Base cho ORM.

    Bao gồm tiện ích convert giữa dict ⇄ ORM ⇄ Pydantic.
    """

    __table_args__ = {
        "mysql_engine": "InnoDB",
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_0900_ai_ci",
    }

    @classmethod
    def from_dict(cls, data: dict[str, Any], exclude_none: bool = True):
        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}
        return cls(**data)

    @classmethod
    def from_pydantic(cls, pydantic_model: Any, exclude_none: bool = True):
        data = pydantic_model.model_dump(exclude_none=exclude_none)
        return cls.from_dict(data)

    def to_pydantic(self, pydantic_model: type[T]) -> T:
        """
        Chuyển đổi từ SQLAlchemy model sang Pydantic model.
        """
        data = {c.name: getattr(self, c.name) for c in self.__table__.columns}
        return pydantic_model(**data)
