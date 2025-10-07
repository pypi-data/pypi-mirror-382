"""memcache.py
Module hỗ trợ thao tác **Memcached** sử dụng thư viện *aiocache* và cung cấp
hai decorator tiện lợi:

1. ``cacheable``   – Cache kết quả của một hàm (key đơn).
2. ``list_cacheable`` – Cache danh sách object theo ``id`` hoặc thuộc tính
   khác, hỗ trợ lấy nhiều id một lượt.

Refactor này thêm docstrings tiếng Việt, type-hint đầy đủ, sắp xếp lại import
theo chuẩn PEP8, KHÔNG thay đổi bất kỳ logic nào.
"""

from __future__ import annotations

import json
import traceback
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from aiocache import Cache
from aiocache.serializers import PickleSerializer

from cores.logger.enhanced_logging import LogCategory, logger


def handle_exception(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception:
            logger.error(
                "Memcache handler exception",
                category=LogCategory.SYSTEM,
                extra_fields={"traceback": traceback.format_exc()},
                exc_info=True,
            )
            return None

    return wrapper


class CacheHandler:
    """Wrapper tiện lợi cho *aiocache* với thêm khả năng lưu key ra file."""

    def __init__(self) -> None:
        self.cache = Cache(
            Cache.MEMCACHED,  # type: ignore
            endpoint="memcache",
            port=11211,
            serializer=PickleSerializer(),
        )
        self.cache_key_file = Path("cache_keys.json")
        self.keys = set()

        if not self.cache_key_file.exists():
            self.cache_key_file.write_text(json.dumps([]))

        self._load_keys()

    @handle_exception
    async def get(self, key: str) -> Any:
        value = await self.cache.get(key)  # type: ignore
        return value

    @handle_exception
    async def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        await self.cache.set(key, value, ttl=ttl)  # type: ignore
        self._add_key_to_file(key)

    @handle_exception
    async def delete(self, key: str) -> None:
        await self.cache.delete(key)  # type: ignore
        self._remove_key_from_file(key)

    @handle_exception
    async def health_check(self) -> bool:
        try:
            await self.set("key", "value")
            value = await self.get("key")
            return value == "value"
        except Exception:
            return False

    def _load_keys(self) -> None:
        """Tải key từ file JSON vào bộ nhớ."""
        try:
            with open(self.cache_key_file) as f:
                self.keys = set(json.load(f))
        except Exception as e:
            logger.error(
                "Error loading keys from file",
                category=LogCategory.SYSTEM,
                extra_fields={"error": str(e)},
            )

    def _add_key_to_file(self, key: str) -> None:
        if key not in self.keys:
            self.keys.add(key)
            self._write_keys()

    def _remove_key_from_file(self, key: str) -> None:
        if key in self.keys:
            self.keys.remove(key)
            self._write_keys()

    def _write_keys(self) -> None:
        """Ghi danh sách key vào file JSON."""
        try:
            with open(self.cache_key_file, "w") as f:
                json.dump(list(self.keys), f, indent=4)
        except Exception as e:
            logger.error(
                "Error writing keys to file",
                category=LogCategory.SYSTEM,
                extra_fields={"error": str(e)},
            )

    async def close(self) -> None:
        """Đóng kết nối khi ứng dụng kết thúc."""
        await self.cache.close()  # type: ignore


cache_handler = CacheHandler()


def list_cacheable(
    cache_key_prefix: str,
    key_to_cache: str = "id",
    ttl: int = 3600,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator kiểm tra cache trước khi gọi hàm gốc.
    Nếu cache có, trả về giá trị từ cache.
    Nếu không, gọi hàm gốc và lưu kết quả vào cache.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            # Nếu key ko phải là dạng list[int] thì return []
            if len(args) < 1 or not isinstance(args[1], list):
                return []

            # args[1] là ids
            results = []  # Danh sách chứa cache value

            # Tạo một danh sách tạm để lưu lại các id chưa có trong cache
            remaining_ids: list[Any] = []

            for item_id in args[1]:
                cache_key = f"{cache_key_prefix}:{item_id}"
                # Kiểm tra cache
                cached_value = await cache_handler.get(cache_key)

                if cached_value is not None:
                    results.append(cached_value)  # Lưu giá trị đã cache
                else:
                    remaining_ids.append(item_id)  # Lưu lại ID chưa cache

            # Gọi hàm gốc để lấy data nếu chưa có cache.
            if remaining_ids:
                origin_results = await func(args[0], remaining_ids)
                if origin_results is not None:
                    mapping: dict[Any, Any] = {}
                    for item in origin_results:
                        mapping[getattr(item, key_to_cache)] = item
                        cache_key = (
                            f"{cache_key_prefix}:{getattr(item, key_to_cache)}"
                        )
                        await cache_handler.set(cache_key, item, ttl)
                        results.append(item)
            await cache_handler.close()
            return results

        return wrapper

    return decorator


def cacheable(
    cache_key_prefix: str,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator cache cho hàm trả về **single object**.

    Key cache được xây theo ``{cache_key_prefix}_{first_arg}`` nếu hàm có
    positional arg; ngược lại chỉ dùng ``cache_key_prefix``.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any):
            cache_key = (
                f"{cache_key_prefix}_{args[0]}" if args else cache_key_prefix
            )
            data = await cache_handler.get(cache_key)
            if data is not None:
                return data

            data = await func(*args, **kwargs)
            await cache_handler.set(cache_key, data)
            await cache_handler.close()
            return data

        return wrapper

    return decorator
