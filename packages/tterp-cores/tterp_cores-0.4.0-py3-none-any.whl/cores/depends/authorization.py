"""
Module cung cấp các dependency và service liên quan đến xác thực và phân quyền.

Module này chứa các class và hàm để:
- Tạo và xác thực JWT tokens
- Mã hóa và giải mã secret keys
- Kiểm tra quyền truy cập vào các routes
- Validate tokens từ người dùng và services
"""

from datetime import datetime, timedelta
from typing import Any, cast

import jwt
from cryptography.fernet import Fernet
from fastapi import Depends, Header, HTTPException, Request, Security, status
from fastapi.security import APIKeyHeader, HTTPBearer
from jose import ExpiredSignatureError, JWTError
from pydantic import ValidationError

from cores.config import service_config
from cores.repository.rpc.auth_client import AuthClient
from cores.repository.rpc.secret_key_menagement_client import (
    SecretKeyManagementClient,
)
from cores.repository.rpc.user_client import UserClient

SECURITY_ALGORITHM = "HS256"

# Security schemes
api_key_header_auth = APIKeyHeader(name="Api-key", auto_error=True)
service_id_header = APIKeyHeader(
    name="service-management-id",
    scheme_name="ServiceManagementId",
    description=f"Origin service id. Default: {service_config.BASE_SERVICE_ID}",
    auto_error=True,
)
reusable_oauth2 = HTTPBearer(
    scheme_name="Authorization", description="JWT Token from Auth Service"
)


class TokenService:
    """
    Service để tạo và xác thực JWT tokens.

    Cung cấp các phương thức để tạo token, giải mã token, và tạo cặp access/refresh tokens.
    """

    @staticmethod
    def generate_token(
        data: dict[str, Any],
        secret_key: str,
        expires_delta: timedelta | None = None,
    ) -> str:
        """
        Tạo JWT token từ dữ liệu và secret key.

        Args:
            data: Dữ liệu cần mã hóa trong token
            secret_key: Khóa bí mật để ký token
            expires_delta: Thời gian token có hiệu lực, mặc định là 15 phút

        Returns:
            JWT token đã được mã hóa
        """
        to_encode = data.copy()
        expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
        to_encode["exp"] = expire
        return jwt.encode(to_encode, secret_key, algorithm=SECURITY_ALGORITHM)

    @staticmethod
    def decode_token(
        token: str, secret_key: str, verify_exp: bool = True
    ) -> dict[str, Any]:
        """
        Giải mã JWT token.

        Args:
            token: JWT token cần giải mã
            secret_key: Khóa bí mật để xác thực token
            verify_exp: Có kiểm tra token hết hạn không

        Returns:
            Dữ liệu từ token đã giải mã

        Raises:
            HTTPException: Nếu token không hợp lệ hoặc đã hết hạn
        """
        try:
            options = {"verify_exp": False} if not verify_exp else {}
            return jwt.decode(
                token,
                secret_key,
                algorithms=[SECURITY_ALGORITHM],
                options=options,
            )
        except ExpiredSignatureError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"message": str(e), "require_refresh": True},
                headers={"WWW-Authenticate": "Bearer"},
            )
        except (JWTError, ValidationError) as e:
            raise HTTPException(
                status_code=(
                    status.HTTP_401_UNAUTHORIZED
                    if isinstance(e, JWTError)
                    else status.HTTP_403_FORBIDDEN
                ),
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def decode_without_verification(token: str) -> dict[str, Any]:
        """
        Giải mã JWT token mà không xác thực chữ ký.

        Hữu ích cho việc xem nội dung token mà không cần secret key.

        Args:
            token: JWT token cần giải mã

        Returns:
            Dữ liệu từ token đã giải mã

        Raises:
            HTTPException: Nếu token không phải là JWT hợp lệ
        """
        try:
            return jwt.decode(token, key=None, options={"verify_signature": False})
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e),
                headers={"WWW-Authenticate": "Bearer"},
            )

    @staticmethod
    def create_token_pair(
        payload: dict[str, Any], private_key: str, public_key: str
    ) -> dict[str, str]:
        """
        Tạo cặp access token và refresh token.

        Args:
            payload: Dữ liệu cần mã hóa trong tokens
            private_key: Khóa bí mật để ký refresh token
            public_key: Khóa công khai để ký access token

        Returns:
            Dictionary chứa access_token và refresh_token
        """
        access_payload = payload.copy()
        refresh_payload = payload.copy()
        access_payload["exp"] = datetime.utcnow() + timedelta(days=999999)
        refresh_payload["exp"] = datetime.utcnow() + timedelta(days=7)
        return {
            "access_token": jwt.encode(
                access_payload, public_key, algorithm=SECURITY_ALGORITHM
            ),
            "refresh_token": jwt.encode(
                refresh_payload, private_key, algorithm=SECURITY_ALGORITHM
            ),
        }


class AuthService:
    """
    Service xử lý các chức năng xác thực.

    Cung cấp các phương thức để validate token, tạo user token và auth token.
    """

    @staticmethod
    async def get_user_token(
        auth_token: str,
        service_management_id: str,
        user_token: str,
        target_service_id: str = service_config.BASE_SERVICE_ID,
    ) -> bool | str:
        """
        Xác thực user token thông qua Auth Service.

        Args:
            auth_token: Token xác thực cho Auth Service
            service_management_id: ID của service gọi API
            user_token: Token người dùng cần xác thực
            target_service_id: ID của service đích, mặc định là BASE_SERVICE_ID

        Returns:
            Token người dùng đã xác thực hoặc False nếu không hợp lệ
        """
        auth_client = AuthClient(auth_token)
        return await auth_client.validate_token(
            service_management_id, target_service_id, user_token
        )

    @staticmethod
    async def create_user_token(
        service_management_id: str, user_secret_key: str | None = None
    ) -> str:
        """
        Tạo token người dùng cho một service.

        Args:
            service_management_id: ID của service
            user_secret_key: Khóa bí mật của người dùng, nếu None sẽ lấy từ Secret Key Management

        Returns:
            User token đã được tạo
        """
        if not user_secret_key:
            user_secret_key = await SecretKeyManagementClient().get_secret_key()

        return TokenService.generate_token(
            {"service_management_id": service_management_id}, user_secret_key
        )

    @staticmethod
    def create_auth_token(auth_secret: str) -> str:
        """
        Tạo auth token.

        Args:
            auth_secret: Khóa bí mật cho auth token

        Returns:
            Auth token đã được tạo
        """
        return TokenService.generate_token({}, auth_secret)


class EncryptionService:
    """
    Service mã hóa và giải mã dữ liệu.

    Sử dụng Fernet để mã hóa và giải mã các khóa bí mật.
    """

    @staticmethod
    def encrypt_secret_key(encryption_key: str, secret_key: str) -> str:
        """
        Mã hóa secret key.

        Args:
            encryption_key: Khóa dùng để mã hóa
            secret_key: Khóa bí mật cần mã hóa

        Returns:
            Secret key đã được mã hóa
        """
        cipher = Fernet(encryption_key)
        return cipher.encrypt(secret_key.encode()).decode()

    @staticmethod
    def decrypt_secret_key(encryption_key: str, encrypted_secret_key: str) -> str:
        """
        Giải mã secret key.

        Args:
            encryption_key: Khóa dùng để giải mã
            encrypted_secret_key: Khóa bí mật đã được mã hóa

        Returns:
            Secret key đã được giải mã
        """
        cipher = Fernet(encryption_key)
        return cipher.decrypt(encrypted_secret_key.encode()).decode()


async def get_api_key(
    api_key_header: str = Security(api_key_header_auth),
) -> str:
    """
    Dependency để lấy API key từ header.

    Args:
        api_key_header: API key từ header, được inject bởi FastAPI

    Returns:
        API key
    """
    return api_key_header


async def check_access(
    request: Request,
    service_management_id: str = Depends(service_id_header),
    user_token: str = Header(...),
    auth_token=Depends(reusable_oauth2),
) -> None:
    """
    Kiểm tra quyền truy cập vào một route.

    Xác thực token người dùng và kiểm tra quyền truy cập vào route hiện tại.
    Lưu user_id và user_token vào request.state nếu có quyền.

    Args:
        request: Request object
        service_management_id: ID của service gọi API
        user_token: Token người dùng từ header
        auth_token: Token xác thực từ Authorization header

    Raises:
        HTTPException: Nếu người dùng không có quyền truy cập
    """
    validated_user_token = await AuthService.get_user_token(
        auth_token.credentials, service_management_id, user_token
    )

    if isinstance(validated_user_token, bool) and not validated_user_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    checked_result = await UserClient(cast(str, validated_user_token)).check_permission(
        request.scope["root_path"] + request.scope["route"].path,
        request.method,
    )

    if checked_result.get("can_action", False):
        request.state.current_user_id = checked_result["user_id"]
        request.state.user_token = validated_user_token
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bạn không có quyền truy cập route này",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def validate_auth(
    request: Request,
    service_management_id: str = Depends(service_id_header),
    user_token: str = Header(...),
    auth_token=Depends(reusable_oauth2),
) -> bool:
    """
    Xác thực token người dùng và lưu vào request.state.

    Không kiểm tra quyền truy cập cụ thể, chỉ xác thực token.

    Args:
        request: Request object
        service_management_id: ID của service gọi API
        user_token: Token người dùng từ header
        auth_token: Token xác thực từ Authorization header

    Returns:
        True nếu xác thực thành công

    Raises:
        HTTPException: Nếu token không hợp lệ
    """
    validated_token = await AuthService.get_user_token(
        auth_token.credentials, service_management_id, user_token
    )

    if isinstance(validated_token, bool) and not validated_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ",
            headers={"WWW-Authenticate": "Bearer"},
        )

    request.state.user_token = validated_token
    return True


async def validate_token(request: Request, credentials=Depends(reusable_oauth2)) -> int:
    """
    Xác thực token và trả về user ID.

    Args:
        request: Request object
        credentials: Credentials từ Authorization header

    Returns:
        User ID từ token

    Raises:
        HTTPException: Nếu token không hợp lệ
    """
    result = await UserClient(credentials.credentials).validate_token()
    request.state.http_authorization_credentials = credentials
    if result and "id" in result:
        return int(result["id"])
    raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")


async def get_user_info(
    request: Request | None = None, credentials=Depends(reusable_oauth2)
) -> int | dict[str, Any]:
    """
    Lấy thông tin người dùng từ token.

    Args:
        request: Request object (tùy chọn)
        credentials: Credentials từ Authorization header

    Returns:
        Thông tin người dùng hoặc user ID

    Raises:
        HTTPException: Nếu token không hợp lệ
    """
    result = await UserClient(credentials.credentials).get_me()
    if request:
        request.state.user_me = result
    return result


def check_access_token(access_token: str, secret_key: str) -> bool:
    """
    Kiểm tra access token có hợp lệ và chưa hết hạn.

    Args:
        access_token: Access token cần kiểm tra
        secret_key: Khóa bí mật để xác thực token

    Returns:
        True nếu token hợp lệ và chưa hết hạn, False nếu không
    """
    try:
        payload = TokenService.decode_token(access_token, secret_key)
        return payload["exp"] > datetime.utcnow().timestamp()
    except HTTPException:
        return False


async def validate_service_token(
    request: Request, credentials=Depends(reusable_oauth2)
) -> dict[str, Any]:
    """
    Dependency function để xác thực service token cho API của service thứ 3.

    Args:
        request: Request object
        credentials: Credentials từ Authorization header
    Returns:
        Payload của service token đã được xác thực

    Raises:
        HTTPException: Nếu token không hợp lệ hoặc service không có quyền
    """

    try:
        # Sử dụng HOOK_API_KEY để xác thực
        payload = TokenService.decode_token(
            credentials.credentials, service_config.HOOK_API_KEY
        )

        # Lưu thông tin service vào request state
        request.state.service_info = payload
        request.state.service_id = payload.get("service_id")

        # Kiểm tra xem service_id có trong danh sách ALLOWED_SERVICES không
        if request.state.service_id not in service_config.ALLOWED_SERVICES:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Service không có quyền truy cập API này",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload

    except HTTPException:
        # Re-raise HTTPException từ validate_service_token
        # (giữ nguyên status code như 403 Forbidden)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Service authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from e
