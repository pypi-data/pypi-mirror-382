"""
Module cung cấp các interfaces và dataclasses cho toàn bộ ứng dụng.

Chứa các định nghĩa interface cho repository, command/query handlers, use cases
và các dataclasses cho token và authentication.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

from sqlalchemy import ScalarResult

from cores.model.paging import PagingDTO

# Type variables cho các generic interfaces
Entity = TypeVar("Entity")
Cond = TypeVar("Cond")
UpdateDTO = TypeVar("UpdateDTO")
CreateDTO = TypeVar("CreateDTO")
Cmd = TypeVar("Cmd")
Result = TypeVar("Result")
Query = TypeVar("Query")


class IQueryRepository(ABC, Generic[Entity, Cond]):
    """
    Interface cho repository chỉ đọc.

    Generic Parameters:
        Entity: Loại entity mà repository xử lý
        Cond: Kiểu điều kiện tìm kiếm
    """

    @abstractmethod
    async def get(
        self,
        id: str | int,
        options: list[Any] = [],
        columns: list[Any] = [],
        with_trash: bool = False,
    ) -> Entity | None:
        """
        Lấy một entity theo ID.

        Args:
            id: ID của entity cần lấy
            options: Các tùy chọn truy vấn (join, eager loading...)
            columns: Danh sách các cột cần lấy
            with_trash: Có lấy cả các bản ghi đã bị xóa mềm không

        Returns:
            Entity nếu tồn tại, None nếu không
        """

    @abstractmethod
    async def get_by_ids(
        self,
        ids: list[int],
        options: list[Any] = [],
        columns: list[Any] = [],
        with_trash: bool = False,
    ) -> ScalarResult:
        """
        Lấy nhiều entities theo danh sách ID.

        Args:
            ids: Danh sách ID của các entities cần lấy
            options: Các tùy chọn truy vấn
            columns: Danh sách các cột cần lấy
            with_trash: Có lấy cả các bản ghi đã bị xóa mềm không

        Returns:
            ScalarResult chứa các entities tìm thấy
        """

    @abstractmethod
    async def find_by_cond(
        self,
        cond: dict[str, Any] | list[Any],
        options: list[Any] = [],
        columns: list[Any] = [],
        with_trash: bool = False,
        exact: bool = False,
    ) -> Entity | None:
        """
        Tìm một entity theo điều kiện.

        Args:
            cond: Điều kiện tìm kiếm
            options: Các tùy chọn truy vấn
            columns: Danh sách các cột cần lấy
            with_trash: Có lấy cả các bản ghi đã bị xóa mềm không
            exact: Tìm kiếm chính xác hay không

        Returns:
            Entity đầu tiên thỏa mãn điều kiện, hoặc None nếu không tìm thấy
        """

    @abstractmethod
    async def get_all_by_cond(
        self,
        cond: Cond | None = None,
        options: list[Any] = [],
        columns: list[Any] = [],
        with_trash: bool = False,
    ) -> list[Entity]:
        """
        Lấy tất cả entities thỏa mãn điều kiện.

        Args:
            cond: Điều kiện tìm kiếm
            options: Các tùy chọn truy vấn
            columns: Danh sách các cột cần lấy
            with_trash: Có lấy cả các bản ghi đã bị xóa mềm không

        Returns:
            Danh sách các entities thỏa mãn điều kiện
        """

    @abstractmethod
    async def get_paging_list(
        self,
        cond: Cond,
        paging: PagingDTO,
        options: list[Any] = [],
        columns: list[Any] = [],
        with_trash: bool = False,
    ) -> list[Entity]:
        """
        Lấy danh sách entities theo trang.

        Args:
            cond: Điều kiện tìm kiếm
            paging: Thông tin phân trang
            options: Các tùy chọn truy vấn
            columns: Danh sách các cột cần lấy
            with_trash: Có lấy cả các bản ghi đã bị xóa mềm không

        Returns:
            Danh sách các entities cho trang hiện tại
        """


class ICommandRepository(ABC, Generic[Entity, CreateDTO, UpdateDTO]):
    """
    Interface cho repository thực hiện các thao tác thay đổi dữ liệu.

    Generic Parameters:
        Entity: Loại entity mà repository xử lý
        CreateDTO: Kiểu dữ liệu cho thao tác tạo mới
        UpdateDTO: Kiểu dữ liệu cho thao tác cập nhật
    """

    @abstractmethod
    async def insert(
        self,
        data: Entity | CreateDTO,
        with_commit: bool = True,
        model_validate: bool = True,
    ) -> Entity:
        """
        Thêm mới một entity.

        Args:
            data: Dữ liệu cần thêm mới
            with_commit: Tự động commit sau khi thêm
            model_validate: Có validate model trước khi thêm không

        Returns:
            Entity đã được thêm vào database
        """

    @abstractmethod
    async def update(
        self,
        id: str | int,
        data: UpdateDTO | dict[str, Any],
        with_commit: bool = True,
    ) -> bool:
        """
        Cập nhật một entity theo ID.

        Args:
            id: ID của entity cần cập nhật
            data: Dữ liệu cập nhật
            with_commit: Tự động commit sau khi cập nhật

        Returns:
            True nếu cập nhật thành công, False nếu không
        """

    @abstractmethod
    async def soft_update(
        self,
        old_entity: Entity,
        data: UpdateDTO | dict[str, Any],
        with_commit: bool = True,
    ) -> Entity:
        """
        Cập nhật một entity hiện có (không trực tiếp qua ID).

        Args:
            old_entity: Entity cần cập nhật
            data: Dữ liệu cập nhật
            with_commit: Tự động commit sau khi cập nhật

        Returns:
            Entity đã được cập nhật
        """

    @abstractmethod
    async def delete(
        self,
        id: str | int,
        is_hard: bool = False,
        with_commit: bool = True,
    ) -> bool:
        """
        Xóa một entity theo ID.

        Args:
            id: ID của entity cần xóa
            is_hard: Xóa cứng hay xóa mềm
            with_commit: Tự động commit sau khi xóa

        Returns:
            True nếu xóa thành công, False nếu không
        """

    @abstractmethod
    async def update_or_create(
        self,
        defaults: dict[str, Any] | None = None,
        with_commit: bool = True,
        **cond: Any,
    ) -> Entity:
        """
        Cập nhật nếu tồn tại, tạo mới nếu chưa tồn tại.

        Args:
            defaults: Các giá trị mặc định khi tạo mới
            with_commit: Tự động commit sau khi xử lý
            **cond: Điều kiện tìm kiếm

        Returns:
            Entity đã được cập nhật hoặc tạo mới
        """

    @abstractmethod
    def bulk_insert(self, entities: list[Entity]) -> None:
        """
        Thêm nhiều entities cùng lúc.

        Args:
            entities: Danh sách entities cần thêm
        """

    @abstractmethod
    async def bulk_update(
        self,
        ids: list[int] = [],
        data: dict[str, Any] = {},
        with_commit: bool = True,
    ) -> None:
        """
        Cập nhật nhiều entities cùng lúc.

        Args:
            ids: Danh sách ID của các entities cần cập nhật
            data: Dữ liệu cập nhật
            with_commit: Tự động commit sau khi cập nhật
        """

    @abstractmethod
    async def save_change(self) -> bool:
        """
        Lưu các thay đổi.

        Returns:
            True nếu lưu thành công, False nếu không
        """

    @abstractmethod
    async def refresh(self, entity: Entity) -> None:
        """
        Làm mới dữ liệu của một entity từ database.

        Args:
            entity: Entity cần làm mới
        """

    @abstractmethod
    async def flush(self) -> None:
        """
        Flush các thay đổi hiện tại vào database nhưng không commit.
        """

    @abstractmethod
    async def delete_by_condition(
        self,
        condition: dict[str, Any],
        is_hard: bool = False,
        with_commit: bool = True,
    ) -> bool:
        """
        Xóa các entities theo điều kiện.

        Args:
            condition: Điều kiện xóa
            is_hard: Xóa cứng hay xóa mềm
            with_commit: Tự động commit sau khi xóa

        Returns:
            True nếu xóa thành công, False nếu không
        """

    @abstractmethod
    async def update_by_condition(
        self,
        condition: dict[str, Any],
        data: dict[str, Any],
        with_commit: bool = True,
    ) -> bool:
        """
        Cập nhật các entities theo điều kiện.

        Args:
            condition: Điều kiện cập nhật
            data: Dữ liệu cập nhật
            with_commit: Tự động commit sau khi cập nhật

        Returns:
            True nếu cập nhật thành công, False nếu không
        """


class IRepository(
    IQueryRepository[Entity, Cond],
    ICommandRepository[Entity, CreateDTO, UpdateDTO],
    ABC,
):
    """
    Interface kết hợp cả repository đọc và ghi.

    Kết hợp các chức năng của IQueryRepository và ICommandRepository.
    """

    @abstractmethod
    async def list(
        self,
        cond: Cond,
        paging: PagingDTO,
        options: list[Any] = [],
        columns: list[Any] = [],
        with_trash: bool = False,
    ) -> list[Entity]:
        """
        Lấy danh sách entities theo trang.

        Args:
            cond: Điều kiện tìm kiếm
            paging: Thông tin phân trang
            options: Các tùy chọn truy vấn
            columns: Danh sách các cột cần lấy
            with_trash: Có lấy cả các bản ghi đã bị xóa mềm không

        Returns:
            Danh sách các entities cho trang hiện tại
        """


class IMysqlRepository(
    IQueryRepository[Entity, Cond],
    ICommandRepository[Entity, CreateDTO, UpdateDTO],
    ABC,
):
    """
    Interface repository dành riêng cho MySQL.

    Kế thừa các chức năng từ IQueryRepository và ICommandRepository
    và cung cấp các tính năng đặc thù cho MySQL.
    """


class ICommandHandler(ABC, Generic[Cmd, Result]):
    """
    Interface cho command handler.

    Generic Parameters:
        Cmd: Kiểu của command
        Result: Kiểu của kết quả trả về
    """

    @abstractmethod
    async def execute(self, command: Cmd) -> Result:
        """
        Thực thi một command.

        Args:
            command: Command cần thực thi

        Returns:
            Kết quả của command
        """


class IQueryHandler(ABC, Generic[Query, Result]):
    """
    Interface cho query handler.

    Generic Parameters:
        Query: Kiểu của query
        Result: Kiểu của kết quả trả về
    """

    @abstractmethod
    async def query(self, query: Query) -> Result:
        """
        Thực hiện một query.

        Args:
            query: Query cần thực hiện

        Returns:
            Kết quả của query
        """


class IUseCase(ABC, Generic[CreateDTO, UpdateDTO, Entity, Cond]):
    """
    Interface cho use case.

    Generic Parameters:
        CreateDTO: Kiểu dữ liệu cho thao tác tạo mới
        UpdateDTO: Kiểu dữ liệu cho thao tác cập nhật
        Entity: Loại entity mà use case xử lý
        Cond: Kiểu điều kiện tìm kiếm
    """

    @abstractmethod
    async def create(self, data: CreateDTO) -> Entity:
        """
        Tạo mới một entity.

        Args:
            data: Dữ liệu cần tạo mới

        Returns:
            Entity đã được tạo
        """

    @abstractmethod
    async def get_detail(self, id: str | int) -> Entity | None:
        """
        Lấy thông tin chi tiết của một entity.

        Args:
            id: ID của entity cần lấy

        Returns:
            Entity nếu tồn tại, None nếu không
        """

    @abstractmethod
    async def list(self, cond: Cond, paging: PagingDTO) -> list[Entity]:
        """
        Lấy danh sách entities theo trang.

        Args:
            cond: Điều kiện tìm kiếm
            paging: Thông tin phân trang

        Returns:
            Danh sách các entities cho trang hiện tại
        """

    @abstractmethod
    async def update(self, id: str | int, data: UpdateDTO) -> Entity:
        """
        Cập nhật một entity.

        Args:
            id: ID của entity cần cập nhật
            data: Dữ liệu cập nhật

        Returns:
            Entity sau khi cập nhật
        """

    @abstractmethod
    async def delete(self, id: str | int) -> bool:
        """
        Xóa một entity.

        Args:
            id: ID của entity cần xóa

        Returns:
            True nếu xóa thành công, False nếu không
        """


class UserRole(Enum):
    """
    Enum định nghĩa các vai trò của người dùng.
    """

    ADMIN = "admin"
    USER = "user"


@dataclass
class TokenPayload:
    """
    Dữ liệu chứa trong JWT token.

    Attributes:
        id: ID của người dùng
        role: Vai trò của người dùng
    """

    id: str | int
    role: UserRole


@dataclass
class TokenPayloadV2:
    """
    Phiên bản mở rộng của TokenPayload, hỗ trợ thêm is_other_service.

    Attributes:
        id: ID của người dùng hoặc service
        is_other_service: Có phải là token của service khác không
    """

    id: int = -1
    is_other_service: bool = False


@dataclass
class Requester(TokenPayload):
    """
    Thông tin về người gửi request.

    Kế thừa từ TokenPayload, chứa ID và vai trò của người gửi request.
    """


class ITokenProvider(ABC):
    """
    Interface cho service cung cấp JWT token.
    """

    @abstractmethod
    async def generate_token(self, payload: TokenPayload) -> str:
        """
        Tạo JWT token từ payload.

        Args:
            payload: Dữ liệu cần mã hóa trong token

        Returns:
            JWT token đã được mã hóa
        """

    @abstractmethod
    async def verify_token(self, token: str) -> TokenPayloadV2 | None:
        """
        Xác thực JWT token.

        Args:
            token: JWT token cần xác thực

        Returns:
            TokenPayloadV2 nếu token hợp lệ, None nếu không
        """


@dataclass
class UserToken:
    """
    Bộ token cho người dùng, bao gồm access token và refresh token.

    Attributes:
        access_token: Token truy cập, có thời hạn ngắn
        refresh_token: Token làm mới, có thời hạn dài hơn
    """

    access_token: str
    refresh_token: str


@dataclass
class TokenIntrospectResult:
    """
    Kết quả phân tích token.

    Attributes:
        payload: Payload của token sau khi giải mã
        is_ok: Token có hợp lệ không
        user_token: Token người dùng (tùy chọn)
        error: Thông tin lỗi nếu có
    """

    payload: TokenPayloadV2 | None = None
    is_ok: bool = False
    user_token: str | None = None
    error: Any | None = None


@dataclass
class CheckPermissionResult:
    """
    Kết quả kiểm tra quyền truy cập.

    Attributes:
        can_action: Người dùng có quyền thực hiện hành động không
        user_id: ID của người dùng được kiểm tra
    """

    can_action: bool = False
    user_id: int = -1


class ITokenIntrospect(ABC):
    """
    Interface cho service phân tích token.
    """

    @abstractmethod
    async def introspect(self, token: str) -> TokenIntrospectResult:
        """
        Phân tích token để lấy thông tin.

        Args:
            token: JWT token cần phân tích

        Returns:
            Kết quả phân tích token
        """

    @classmethod
    @abstractmethod
    async def check_access(
        cls,
        service_management_id: str,
        user_token: str,
        auth_token: str,
        method: str,
        url: str,
    ) -> TokenIntrospectResult:
        """
        Kiểm tra quyền truy cập tổng thể.

        Args:
            service_management_id: ID của service gọi API
            user_token: Token người dùng
            auth_token: Token xác thực
            method: Phương thức HTTP
            url: URL đang được truy cập

        Returns:
            Kết quả phân tích token và quyền truy cập
        """
