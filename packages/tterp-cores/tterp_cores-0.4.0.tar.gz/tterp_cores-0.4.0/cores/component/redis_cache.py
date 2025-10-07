"""redis_cache.py
Bộ nhớ đệm (cache) sử dụng Redis thay thế Memcached.

File này cung cấp:
    • `cache_handler` – singleton CacheHandler
    • `cacheable`, `list_cacheable` – decorator tiện lợi giống memcache.py

Thiết kế:
1. Lưu trữ object bằng pickle -> base64 string để tránh lỗi encoding.
2. Fallback to in-memory dict khi không kết nối được Redis (giúp test CI).
3. Ghi lại tất cả cache key vào file JSON `cache_keys.json` để hỗ trợ xoá hàng loạt.
"""

from __future__ import annotations

import base64
import json
import pickle
import traceback
from collections.abc import Callable, Coroutine
from functools import wraps
from pathlib import Path
from typing import Any

import aioredis  # type: ignore

from cores.config import database_config
from cores.logger.enhanced_logging import LogCategory, logger

# ---------------------------------------------------------------------------
# Helper decorator ghi log exception nhưng không "bóp chết" chương trình
# ---------------------------------------------------------------------------


def handle_exception(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):  # type: ignore
        try:
            return await func(*args, **kwargs)
        except Exception:  # pragma: no cover – tránh che log test
            logger.error(
                "Redis cache handler exception",
                category=LogCategory.SYSTEM,
                extra_fields={"traceback": traceback.format_exc()},
                exc_info=True,
            )
            return None

    return wrapper


# ---------------------------------------------------------------------------
# CacheHandler sử dụng Redis (async)
# ---------------------------------------------------------------------------


class CacheHandler:  # pylint: disable=too-few-public-methods
    """Wrapper quanh Redis cho nhu cầu cache đơn giản (get/set/delete)."""

    def __init__(self) -> None:
        self._address = f"redis://:{database_config.REDIS_PASSWORD}@{database_config.REDIS_HOST}:{database_config.REDIS_PORT}/{database_config.REDIS_DB}"
        self._password = database_config.REDIS_PASSWORD or None
        self._redis: aioredis.Redis | None = None  # type: ignore
        self._use_memory: bool = False  # Fallback khi Redis unavailable
        self._memory_cache: dict[str, Any] = {}

        # File lưu danh sách key để admin có thể xoá hàng loạt
        self.cache_key_file = Path("cache_keys.json")
        if not self.cache_key_file.exists():
            self.cache_key_file.write_text(json.dumps([]))

        self.keys: set[str] = set()
        self._load_keys()

        # Thống kê hit/miss
        self.hit: int = 0
        self.miss: int = 0

    # ------------------------------------------------------------------
    # Connection helpers
    # ------------------------------------------------------------------

    async def _init_redis(self) -> None:
        """Lười khởi tạo kết nối Redis."""
        if self._use_memory:
            return
        if self._redis is not None:
            # Nếu đã có connection, thử ping. Nếu ping OK -> giữ nguyên.
            try:
                await self._redis.ping()
                return
            except Exception:
                # Connection cũ hỏng -> tạo kết nối mới.
                self._redis = None
        try:
            self._redis = await aioredis.from_url(  # type: ignore
                self._address,
                password=self._password,
                encoding="utf-8",
                decode_responses=True,
            )
            # Thử ping để chắc kết nối ổn
            await self._redis.ping()
        except Exception as exc:  # pragma: no cover – fallback
            logger.error(
                "[RedisCache] Không kết nối được Redis -> fallback memory",
                category=LogCategory.SYSTEM,
                extra_fields={"error": str(exc)},
            )
            self._use_memory = True
            self._redis = None

    # ------------------------------------------------------------------
    # Public API (get / set / delete)
    # ------------------------------------------------------------------

    @handle_exception
    async def get(self, key: str) -> Any:
        if self._use_memory:
            value = self._memory_cache.get(key)
            if value is None:
                self.miss += 1
            else:
                self.hit += 1
            return value
        await self._init_redis()
        if self._redis is None:
            self.miss += 1
            return None
        data = await self._redis.get(key)
        if data is None:
            self.miss += 1
            return None
        try:
            # Giải mã base64 -> pickle -> object
            value = pickle.loads(base64.b64decode(data))
            self.hit += 1
            return value
        except Exception:  # pragma: no cover – unsupported format
            self.hit += 1
            return data  # Kiểu text thuần

    @handle_exception
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        if self._use_memory:
            self._memory_cache[key] = value
            return
        await self._init_redis()
        if self._redis is None:
            return
        # Pickle + base64 tránh lỗi decode_responses
        encoded = base64.b64encode(pickle.dumps(value)).decode("utf-8")
        await self._redis.set(key, encoded, ex=ttl)
        self._add_key_to_file(key)

    @handle_exception
    async def delete(self, key: str) -> None:
        if self._use_memory:
            self._memory_cache.pop(key, None)
            return
        await self._init_redis()
        if self._redis is None:
            return
        await self._redis.delete(key)
        self._remove_key_from_file(key)

    @handle_exception
    async def flushdb(self) -> None:
        if self._use_memory:
            self._memory_cache.clear()
            self.hit = 0
            self.miss = 0
            return
        await self._init_redis()
        if self._redis is None:
            return
        await self._redis.flushdb()
        # Reset file
        self.keys.clear()
        self._write_keys()

    async def health_check(self) -> bool:
        """Ping Redis hoặc xác nhận fallback memory đang bật."""
        if self._use_memory:
            # Fallback memory luôn "up" nhưng nên cảnh báo
            return False

        try:
            await self._init_redis()
            if self._redis is None:
                return False
            pong = await self._redis.ping()
            return bool(pong)
        except Exception as exc:
            logger.error(
                "[RedisCache] Health check lỗi",
                category=LogCategory.SYSTEM,
                extra_fields={"error": str(exc), "traceback": traceback.format_exc()},
                exc_info=True,
            )
            return False

    async def close(self) -> None:
        if self._redis and not self._redis.closed:
            await self._redis.close()

    # ------------------------------------------------------------------
    # Helper functions cho file key
    # ------------------------------------------------------------------

    def _load_keys(self) -> None:  # pragma: no cover
        try:
            with open(self.cache_key_file, encoding="utf-8") as f:
                self.keys = set(json.load(f))
        except Exception as exc:
            logger.error(
                "[RedisCache] Error load keys",
                category=LogCategory.SYSTEM,
                extra_fields={"error": str(exc)},
            )

    def _add_key_to_file(self, key: str) -> None:
        if key not in self.keys:
            self.keys.add(key)
            self._write_keys()

    def _remove_key_from_file(self, key: str) -> None:
        if key in self.keys:
            self.keys.remove(key)
            self._write_keys()

    def _write_keys(self) -> None:  # pragma: no cover
        try:
            with open(self.cache_key_file, "w", encoding="utf-8") as f:
                json.dump(list(self.keys), f, indent=4)
        except Exception as exc:
            logger.error(
                "[RedisCache] Error write keys",
                category=LogCategory.SYSTEM,
                extra_fields={"error": str(exc)},
            )

    # ------------------------------------------------------------------
    # Stats & monitoring
    # ------------------------------------------------------------------

    def stats(self) -> dict[str, Any]:
        """Trả về thống kê hit/miss và trạng thái fallback."""
        total = self.hit + self.miss
        hit_ratio = round(self.hit / total, 2) if total else None
        return {
            "hit": self.hit,
            "miss": self.miss,
            "hit_ratio": hit_ratio,
            "use_memory": self._use_memory,
        }


# Singleton instance
cache_handler = CacheHandler()

# ---------------------------------------------------------------------------
# Decorators
# ---------------------------------------------------------------------------


def list_cacheable(
    cache_key_prefix: str,
    key_to_cache: str = "id",
    ttl: int = 3600,
) -> Callable[[Callable[..., Coroutine[Any, Any, Any]]], Callable[..., Any]]:
    """Decorator cache cho danh sách object (nhiều id).

    Hàm gốc phải có tham số thứ hai (positional) là list ids.
    """

    def decorator(func):  # type: ignore
        @wraps(func)
        async def wrapper(*args, **kwargs):  # type: ignore
            if len(args) < 2 or not isinstance(args[1], list):
                return await func(*args, **kwargs)

            ids: list[Any] = args[1]
            results: list[Any] = []
            missing_ids: list[Any] = []

            # Kiểm tra cache từng id
            for _id in ids:
                ckey = f"{cache_key_prefix}:{_id}"
                cached = await cache_handler.get(ckey)
                if cached is not None:
                    results.append(cached)
                else:
                    missing_ids.append(_id)

            # Lấy những id chưa cache
            if missing_ids:
                # type: ignore
                origin_results = await func(
                    args[0], missing_ids, *args[2:], **kwargs
                )
                for item in origin_results or []:
                    item_key = getattr(item, key_to_cache)
                    ckey = f"{cache_key_prefix}:{item_key}"
                    await cache_handler.set(ckey, item, ttl)
                    results.append(item)
            return results

        return wrapper

    return decorator


def cacheable(cache_key_prefix: str, ttl: int = 3600):
    """Decorator cache cho hàm trả về **single object**."""

    def decorator(func):  # type: ignore
        @wraps(func)
        async def wrapper(*args, **kwargs):  # type: ignore
            key = f"{cache_key_prefix}_{args[1] if len(args) > 1 else ''}"
            cached = await cache_handler.get(key)
            if cached is not None:
                return cached
            data = await func(*args, **kwargs)
            await cache_handler.set(key, data, ttl)
            return data

        return wrapper

    return decorator
