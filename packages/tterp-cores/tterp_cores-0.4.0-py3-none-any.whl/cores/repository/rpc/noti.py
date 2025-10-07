
from pydantic import BaseModel, Field

from cores.config import service_config
from cores.repository.rpc.client_base import ClientBase


class NotificationRequest(BaseModel):
    service_management_id: str = Field(
        ..., description="ID của quản lý dịch vụ"
    )
    table_management_id: str = Field(..., description="ID của quản lý bảng")
    to_list_user_id: list[int] = Field(
        ..., description="Danh sách ID người nhận"
    )
    subject: str = Field(..., description="Chủ đề thông báo")
    content: str = Field(..., description="Nội dung thông báo")
    mail_username: str | None = Field(
        None, description="Tên người dùng email (nếu có)"
    )
    mail_password: str | None = Field(
        None, description="Mật khẩu email (nếu có)"
    )
    event: str | None = Field(
        None, description="Sự kiện liên quan (nếu có)"
    )
    content_type: str = Field(
        default="plain", description="Loại nội dung (plain hoặc HTML)"
    )
    callback_url: str | None = Field(
        None, description="URL callback sau khi gửi thông báo (nếu có)"
    )
    from_user_id: str = Field(default="1", description="ID người gửi")
    item_id: str | None = Field(
        None, description="ID mục liên quan (nếu có)"
    )
    channels: list[str] = Field(
        default_factory=lambda: ["email"],
        description="Danh sách kênh để gửi thông báo",
    )
    save: bool = Field(default=True, description="Cờ để lưu thông báo")

    # class Config:
    #     schema_extra = {
    #         "example": {
    #             "service_management_id": "12345",
    #             "table_management_id": "67890",
    #             "to_list_user_id": [1, 2, 3],
    #             "subject": "Thông báo quan trọng",
    #             "content": "Đây là nội dung của thông báo.",
    #             "mail_username": "example@example.com",
    #             "mail_password": "securepassword",
    #             "event": "UserUpdate",
    #             "content_type": "plain",
    #             "from_user_id": "1",
    #             "item_id": "item123",
    #             "channels": ["email", "sms"],
    #             "save": True
    #         }
    #     }


class INotificationCommandRepository:
    def push_notify(self, request: NotificationRequest):
        raise NotImplementedError


class RPCNotificationRepository(INotificationCommandRepository, ClientBase):
    async def _initialize(self):
        self._base_url = service_config.NOTIFIER_BASE_URL
        await self.set_jwt_token_and_headers(
            target_service_id=service_config.NOTIFIER_SERVICE_ID
        )
        return self

    async def push_notify(self, request: NotificationRequest):
        return await self.curl_api_with_auth(
            self._initialize,
            "POST",
            "announce/",
            request.model_dump(exclude_none=True),
        )
