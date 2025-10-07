"""
Module cung cấp truy cập tới cache handler cho toàn bộ ứng dụng.

Module này export cache_handler từ cores.component.redis_cache để
các module khác có thể import một cách dễ dàng.
"""

from cores.component.redis_cache import cache_handler

__all__ = ["cache_handler"]
