from datetime import datetime
from typing import Any

import jwt
from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError
from pydantic import ValidationError

from cores.config import service_config
from cores.depends.authorization import EncryptionService
from cores.interface.index import (
    ITokenProvider,
    TokenPayload,
    TokenPayloadV2,
)

# Constants
SECURITY_ALGORITHM = "HS256"


class JwtTokenService(ITokenProvider):
    """
    Dịch vụ xử lý JWT Tokens.

    Class này cung cấp các phương thức để tạo và xác thực JWT tokens,
    hỗ trợ cả tokens từ service hiện tại và các services khác.
    """

    def __init__(self, secret_key: str, expires_in: str | int):
        """
        Khởi tạo JWT Token Service.

        Args:
            secret_key: Khóa bí mật dùng để ký JWT
            expires_in: Thời gian hết hạn của token
        """
        self.secret_key = secret_key
        self.expires_in = expires_in

    async def generate_token(self, payload: TokenPayload) -> str:
        """
        Tạo JWT token từ payload.

        Args:
            payload: Dữ liệu cần mã hóa trong token

        Returns:
            JWT token đã được mã hóa
        """
        # Thêm thời gian hết hạn vào payload nếu cần
        token_payload = dict(payload)
        if isinstance(self.expires_in, int):
            from datetime import datetime, timedelta
            token_payload["exp"] = datetime.utcnow() + timedelta(seconds=self.expires_in)

        return jwt.encode(
            token_payload,
            self.secret_key,
            algorithm=SECURITY_ALGORITHM
        )

    async def verify_token(self, token: str) -> TokenPayloadV2 | None:
        """
        Xác thực JWT token.

        Args:
            token: JWT token cần xác thực

        Returns:
            TokenPayloadV2 nếu token hợp lệ, None nếu không
        """
        try:
            payload = jwt.decode(
                token, self.secret_key, algorithms=[SECURITY_ALGORITHM]
            )

            if "exp" in payload:
                self._check_token_expiry(payload)

            return TokenPayloadV2(
                is_other_service=(
                    payload["is_other_service"]
                    if "is_other_service" in payload
                    else False
                ),
                id=payload["id"],
            )

        except Exception:
            return None

    async def verify_token_v2(
        self, user_token: str, key_service=None
    ) -> TokenPayloadV2 | None:
        """
        Giải mã JWT token để lấy thông tin người dùng và trả về payload.

        Phương thức này hỗ trợ xác thực token từ service hiện tại hoặc
        các services khác thông qua key_service.

        Args:
            user_token: JWT token cần xác thực
            key_service: Service dùng để lấy secret key cho các services khác

        Returns:
            TokenPayloadV2 chứa thông tin người dùng

        Raises:
            HTTPException: Khi token không hợp lệ hoặc hết hạn
        """
        try:
            # Đọc payload mà không cần xác thực để xác định nguồn gốc token
            unverified_payload = jwt.decode(
                user_token, options={"verify_signature": False}, key=""
            )

            # Xác định xem token có phải từ service khác không
            if "service_management_id" in unverified_payload:
                payload = await self._handle_jwt_from_other_service(
                    key_service,
                    unverified_payload["service_management_id"],
                    user_token,
                )
                return TokenPayloadV2(
                    is_other_service=True, id=1  # Default ID cho service khác
                )
            elif "id" in unverified_payload:
                payload = await self.verify_token(user_token)
                if not payload:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="User Token không hợp lệ",
                    )
                return TokenPayloadV2(
                    is_other_service=False,
                    id=payload.id,
                )
            else:
                raise HTTPException(
                    status_code=403, detail="Token verified fail"
                )

        except ExpiredSignatureError as e:
            self._handle_expired_token(e)
        except JWTError:
            self._handle_validation_error()
        except ValidationError:
            self._handle_validation_error()

        # Không bao giờ được thực thi do có raise exception ở trên
        # nhưng cần thiết cho type checker
        return None

    async def _handle_jwt_from_other_service(
        self, key_service, service_management_id: str, token: str
    ) -> dict[str, Any]:
        """
        Xử lý JWT từ service khác.

        Args:
            key_service: Service dùng để lấy secret key
            service_management_id: ID của service gửi token
            token: JWT token cần xác thực

        Returns:
            Payload của token đã giải mã

        Raises:
            HTTPException: Khi service không tồn tại hoặc token không hợp lệ
        """
        try:
            # Tìm secret key của service
            service_secret_key = (
                await key_service.find_cached_secret_key_by_service(
                    service_management_id
                )
            )

            if service_secret_key is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"Service {service_management_id} does not exist",
                )

            # Giải mã token với secret key của service
            return self._decode_token_with_service_key(
                token, service_secret_key
            )
        except ExpiredSignatureError as e:
            self._handle_expired_token(e)
        except JWTError as e:
            return await self._handle_jwt_from_other_service(
                key_service, e, token
            )  # type: ignore
        except ValidationError:
            self._handle_validation_error()

        # Không bao giờ được thực thi do có raise exception ở trên
        # nhưng cần thiết cho type checker
        return {}

    def _handle_expired_token(self, error: Exception) -> None:
        """
        Xử lý lỗi token hết hạn.

        Args:
            error: Exception gốc

        Raises:
            HTTPException: Luôn luôn được raise với thông tin về token hết hạn
        """
        res = {
            "message": str(error),
            "require_refresh": True,
        }
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=res,
            headers={"WWW-Authenticate": "Bearer"},
        )

    def _handle_validation_error(self) -> None:
        """
        Xử lý lỗi validation.

        Raises:
            HTTPException: Luôn luôn được raise với thông báo lỗi
        """
        raise HTTPException(
            status_code=403,
            detail="User token không hợp lệ",
        )

    def _check_token_expiry(self, payload: dict[str, Any]) -> None:
        """
        Kiểm tra xem token đã hết hạn chưa.

        Args:
            payload: Payload của token

        Raises:
            ExpiredSignatureError: Nếu token đã hết hạn
        """
        if payload.get("exp") < datetime.now().timestamp():
            raise ExpiredSignatureError("Token has expired")

    def _decode_token_with_service_key(
        self, token: str, service_secret_key: str
    ) -> dict[str, Any]:
        """
        Giải mã token với service-specific secret key.

        Args:
            token: JWT token cần giải mã
            service_secret_key: Secret key của service

        Returns:
            Payload của token đã giải mã

        Raises:
            HTTPException: Khi token không hợp lệ
        """
        try:
            return jwt.decode(
                token,
                EncryptionService.decrypt_secret_key(
                    service_config.ENCRYPTION_KEY, service_secret_key
                ),
                algorithms=[SECURITY_ALGORITHM],
            )
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Xác thực token từ BE Service khác gọi đến không hợp lệ",
                headers={"WWW-Authenticate": "Bearer"},
            )


# Khởi tạo JWT provider singleton
jwt_provider = JwtTokenService(
    service_config.access_token.USER_SECRET_KEY,
    service_config.access_token.EXPIRES_IN,
)
