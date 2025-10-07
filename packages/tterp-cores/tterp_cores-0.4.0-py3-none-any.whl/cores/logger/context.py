"""
Module cung cấp context cho hệ thống logging.

Module này sử dụng contextvars để lưu trữ và truy xuất thông tin context
cho mỗi request, giúp tự động đính kèm thông tin như request_id và user_id
vào các log messages mà không cần truyền thủ công.
"""

import contextvars
import uuid
from contextvars import ContextVar, Token
from typing import Any

# Context variables để lưu trữ thông tin request và user
request_id: ContextVar[str | None] = contextvars.ContextVar(
    "request_id", default=None
)
user_id: ContextVar[int | None] = contextvars.ContextVar(
    "user_id", default=None
)
request_data: ContextVar[dict[str, Any]] = contextvars.ContextVar(
    "request_data", default={}
)


class LogContext:
    """
    Context manager để quản lý thông tin log theo request.

    Tự động thiết lập và dọn dẹp các context variables cho logging.
    Cho phép truyền thông tin như request_id, user_id và dữ liệu bổ sung
    vào tất cả các log messages trong phạm vi của context.

    Sử dụng:
    ```python
    async def some_api_handler(request):
        with LogContext(request_id=str(uuid.uuid4(), user_id=user.id):
            # Tất cả log trong context này sẽ có request_id và user_id
            result = await some_business_logic()
            return result
    ```

    Attributes:
        request_id: ID duy nhất cho request
        user_id: ID của người dùng thực hiện request
        extra_data: Dữ liệu bổ sung cần lưu trong context
    """

    def __init__(
        self,
        request_id: str | None = None,
        user_id: int | None = None,
        **extra_data: Any,
    ) -> None:
        """
        Khởi tạo LogContext với các thông tin context.

        Args:
            request_id: ID duy nhất cho request, tự động tạo UUID nếu không cung cấp
            user_id: ID của người dùng thực hiện request
            **extra_data: Dữ liệu bổ sung cần lưu trong context
        """
        self.request_id_token: Token | None = None
        self.user_id_token: Token | None = None
        self.request_data_token: Token | None = None

        self.request_id = request_id or str(uuid.uuid4())
        self.user_id = user_id
        self.extra_data = extra_data

    def __enter__(self) -> "LogContext":
        """
        Thiết lập context khi bắt đầu block with.

        Lưu các giá trị vào context variables và lưu lại tokens
        để có thể reset khi kết thúc block.

        Returns:
            LogContext instance hiện tại
        """
        self.request_id_token = request_id.set(self.request_id)
        self.user_id_token = user_id.set(self.user_id)
        self.request_data_token = request_data.set(self.extra_data)
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """
        Dọn dẹp context khi kết thúc block with.

        Reset các context variables về giá trị trước đó.

        Args:
            exc_type: Loại exception nếu có
            exc_val: Giá trị exception nếu có
            exc_tb: Traceback nếu có
        """
        if self.request_id_token:
            request_id.reset(self.request_id_token)
        if self.user_id_token:
            user_id.reset(self.user_id_token)
        if self.request_data_token:
            request_data.reset(self.request_data_token)

    @classmethod
    def get_context(cls) -> dict[str, Any]:
        """
        Lấy toàn bộ thông tin context hiện tại.

        Kết hợp các giá trị từ các context variables và trả về
        dưới dạng dictionary.

        Returns:
            Dictionary chứa tất cả thông tin context hiện tại
        """
        ctx = {
            "request_id": request_id.get(),
            "user_id": user_id.get(),
        }

        # Thêm các thông tin bổ sung từ request_data
        extra = request_data.get()
        if extra and isinstance(extra, dict):
            ctx.update(extra)

        return ctx
