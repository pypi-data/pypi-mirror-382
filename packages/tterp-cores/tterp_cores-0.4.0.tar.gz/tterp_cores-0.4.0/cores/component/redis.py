"""
Module cung cấp các tiện ích để tương tác với Redis.

Module này chứa RedisHandler class để thực hiện các thao tác với Redis
và hàm get_redis để cung cấp singleton instance cho toàn bộ ứng dụng.
"""

from typing import Any

import aioredis

from cores.config import service_config


class RedisHandler:
    """
    Handler quản lý kết nối và tương tác với Redis.

    Class này cung cấp các phương thức để thao tác với Redis như set, get, delete...
    Sử dụng singleton pattern để đảm bảo chỉ có một kết nối Redis trong toàn bộ ứng dụng.

    Attributes:
        client: Redis client instance từ aioredis
    """

    def __init__(
        self,
        host: str = service_config.REDIS_HOST,
        port: int = service_config.REDIS_PORT,
        password: str = service_config.REDIS_PASSWORD,
        db: int = service_config.REDIS_DB,
    ):
        """
        Khởi tạo Redis handler.

        Args:
            host: Địa chỉ host của Redis server
            port: Port của Redis server
            password: Mật khẩu cho Redis server
            db: Database index của Redis
        """
        self._address = f"redis://{host}:{port}/{db}"
        self._password = password
        self.client = None

    async def initialize(self) -> None:
        """
        Khởi tạo kết nối Redis khi cần.

        Tạo một kết nối mới nếu chưa tồn tại hoặc kết nối cũ đã đóng.
        """
        if self.client is None or self.client.closed:
            self.client = await aioredis.create_redis_pool(
                self._address,
                password=self._password,
                encoding="utf-8",  # Decode responses thành string
            )

    async def set(
        self, key: str, value: Any, ex: int | None = None
    ) -> bool:
        """
        Lưu giá trị vào Redis với key cho trước.

        Args:
            key: Khóa của giá trị
            value: Giá trị cần lưu
            ex: Thời gian sống của key (seconds), None cho vĩnh viễn

        Returns:
            True nếu thành công, False nếu không
        """
        await self.initialize()
        return await self.client.set(key, value, expire=ex)

    async def get(self, key: str) -> str | None:
        """
        Lấy giá trị từ Redis với key cho trước.

        Args:
            key: Khóa của giá trị cần lấy

        Returns:
            Giá trị của key hoặc None nếu key không tồn tại
        """
        await self.initialize()
        return await self.client.get(key)

    async def delete(self, key: str) -> int:
        """
        Xóa một key trong Redis.

        Args:
            key: Khóa cần xóa

        Returns:
            Số lượng key đã xóa thành công
        """
        await self.initialize()
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """
        Kiểm tra key có tồn tại trong Redis không.

        Args:
            key: Khóa cần kiểm tra

        Returns:
            True nếu key tồn tại, False nếu không
        """
        await self.initialize()
        return await self.client.exists(key)

    async def ttl(self, key: str) -> int:
        """
        Lấy thời gian còn lại của key (Time-To-Live).

        Args:
            key: Khóa cần kiểm tra TTL

        Returns:
            Thời gian còn lại (giây), -1 nếu key tồn tại nhưng không có expire,
            -2 nếu key không tồn tại
        """
        await self.initialize()
        return await self.client.ttl(key)

    async def incr(self, key: str) -> int:
        """
        Tăng giá trị của key lên 1.

        Args:
            key: Khóa cần tăng giá trị

        Returns:
            Giá trị sau khi tăng
        """
        await self.initialize()
        return await self.client.incr(key)

    async def hset(self, key: str, field: str, value: Any) -> int:
        """
        Lưu giá trị vào một field trong hash.

        Args:
            key: Khóa của hash
            field: Tên field
            value: Giá trị của field

        Returns:
            1 nếu field được tạo mới, 0 nếu field đã tồn tại và được cập nhật
        """
        await self.initialize()
        return await self.client.hset(key, field, value)

    async def hget(self, key: str, field: str) -> str | None:
        """
        Lấy giá trị của một field trong hash.

        Args:
            key: Khóa của hash
            field: Tên field cần lấy giá trị

        Returns:
            Giá trị của field hoặc None nếu field không tồn tại
        """
        await self.initialize()
        return await self.client.hget(key, field)

    async def hgetall(self, key: str) -> dict[str, str]:
        """
        Lấy tất cả các field và giá trị trong hash.

        Args:
            key: Khóa của hash

        Returns:
            Dictionary chứa các cặp field-value trong hash
        """
        await self.initialize()
        return await self.client.hgetall(key)

    async def lpush(self, key: str, *values: Any) -> int:
        """
        Thêm một hoặc nhiều giá trị vào đầu list.

        Args:
            key: Khóa của list
            values: Các giá trị cần thêm vào list

        Returns:
            Độ dài của list sau khi thêm
        """
        await self.initialize()
        return await self.client.lpush(key, *values)

    async def lrange(self, key: str, start: int, stop: int) -> list[str]:
        """
        Lấy các phần tử trong list từ vị trí start đến stop.

        Args:
            key: Khóa của list
            start: Vị trí bắt đầu (0-based)
            stop: Vị trí kết thúc (bao gồm), sử dụng -1 cho phần tử cuối cùng

        Returns:
            Danh sách các phần tử trong list trong khoảng chỉ định
        """
        await self.initialize()
        return await self.client.lrange(key, start, stop)

    async def expire(self, key: str, seconds: int) -> bool:
        """
        Đặt thời gian sống cho key.

        Args:
            key: Khóa cần đặt expire
            seconds: Thời gian sống (giây)

        Returns:
            True nếu thành công, False nếu key không tồn tại
        """
        await self.initialize()
        return await self.client.expire(key, seconds)

    async def flushdb(self) -> bool:
        """
        Xóa tất cả các key trong database hiện tại.

        Returns:
            True nếu thành công
        """
        await self.initialize()
        return await self.client.flushdb()

    async def close(self) -> None:
        """
        Đóng kết nối Redis.

        Chỉ đóng nếu kết nối tồn tại và đang mở.
        """
        if self.client and not self.client.closed:
            self.client.close()
            await self.client.wait_closed()


# Singleton instance
redis_handler = RedisHandler()


async def get_redis() -> RedisHandler:
    """
    Trả về singleton instance của RedisHandler.

    Đảm bảo RedisHandler được khởi tạo trước khi sử dụng.

    Returns:
        RedisHandler instance đã được khởi tạo
    """
    await redis_handler.initialize()
    return redis_handler
