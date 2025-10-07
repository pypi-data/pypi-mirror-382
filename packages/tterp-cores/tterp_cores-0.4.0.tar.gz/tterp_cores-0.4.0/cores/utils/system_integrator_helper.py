"""
Shared utilities cho System Integrator Authentication
"""

import hashlib
import re
import secrets
from datetime import datetime, timedelta
from typing import Any

import jwt

from cores.model.system_integrator import (
    InvalidClientError,
    SystemIntegratorJWTPayload,
    SystemIntegratorType,
    SystemUserTokenPayload,
    TokenExpiredError,
    TokenType,
)


class SystemIntegratorJWTService:
    """Service để handle JWT operations cho System Integrator"""

    ALGORITHM = "HS256"
    DEFAULT_EXPIRY_HOURS = 24
    SYSTEM_USER_TOKEN_SECRET = "system-integrator-user-token-secret-2024"

    @classmethod
    def generate_access_token(
        cls,
        client_id: str,
        service_management_id: str,
        scopes: list[str],
        jwt_secret: str,
        client_type: SystemIntegratorType = SystemIntegratorType.API_CLIENT,
        expiry_hours: int = DEFAULT_EXPIRY_HOURS,
    ) -> str:
        """Tạo JWT access token cho System Integrator"""

        now = datetime.utcnow()
        payload = SystemIntegratorJWTPayload(
            client_id=client_id,
            client_type=client_type,
            service_management_id=service_management_id,
            scopes=scopes,
            exp=now + timedelta(hours=expiry_hours),
            iat=now,
            jti=cls.generate_jti(),
        )

        # Convert datetime objects to timestamps for JWT
        payload_dict = payload.model_dump()
        payload_dict["exp"] = int(payload_dict["exp"].timestamp())
        payload_dict["iat"] = int(payload_dict["iat"].timestamp())
        payload_dict["client_type"] = payload_dict["client_type"].value
        payload_dict["token_type"] = payload_dict["token_type"].value

        return jwt.encode(payload_dict, jwt_secret, algorithm=cls.ALGORITHM)

    @classmethod
    def generate_system_user_token(
        cls, client_id: str, expiry_hours: int = DEFAULT_EXPIRY_HOURS
    ) -> str:
        """Tạo system user token cho headers"""

        now = datetime.utcnow()
        payload = SystemUserTokenPayload(
            client_id=client_id,
            exp=now + timedelta(hours=expiry_hours),
            iat=now,
        )

        # Convert datetime objects to timestamps for JWT
        payload_dict = payload.model_dump()
        payload_dict["exp"] = int(payload_dict["exp"].timestamp())
        if payload_dict["iat"]:
            payload_dict["iat"] = int(payload_dict["iat"].timestamp())
        payload_dict["token_type"] = payload_dict["token_type"].value

        return jwt.encode(
            payload_dict, cls.SYSTEM_USER_TOKEN_SECRET, algorithm=cls.ALGORITHM
        )

    @classmethod
    def validate_access_token(
        cls, token: str, jwt_secret: str
    ) -> SystemIntegratorJWTPayload:
        """Validate và decode access token"""

        try:
            payload = jwt.decode(token, jwt_secret, algorithms=[cls.ALGORITHM])

            # Convert timestamps back to datetime objects
            payload["exp"] = datetime.fromtimestamp(payload["exp"])
            payload["iat"] = datetime.fromtimestamp(payload["iat"])
            payload["client_type"] = SystemIntegratorType(
                payload["client_type"]
            )
            payload["token_type"] = TokenType(payload["token_type"])

            return SystemIntegratorJWTPayload(**payload)

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("Access token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidClientError(f"Invalid access token: {str(e)}")

    @classmethod
    def validate_system_user_token(cls, token: str) -> SystemUserTokenPayload:
        """Validate và decode system user token"""

        try:
            payload = jwt.decode(
                token, cls.SYSTEM_USER_TOKEN_SECRET, algorithms=[cls.ALGORITHM]
            )

            # Convert timestamps back to datetime objects
            payload["exp"] = datetime.fromtimestamp(payload["exp"])
            if payload.get("iat"):
                payload["iat"] = datetime.fromtimestamp(payload["iat"])
            payload["token_type"] = TokenType(payload["token_type"])

            return SystemUserTokenPayload(**payload)

        except jwt.ExpiredSignatureError:
            raise TokenExpiredError("System user token has expired")
        except jwt.InvalidTokenError as e:
            raise InvalidClientError(f"Invalid system user token: {str(e)}")

    @classmethod
    def decode_without_verification(cls, token: str) -> dict[str, Any]:
        """Decode token without verification để check type"""
        try:
            return jwt.decode(token, options={"verify_signature": False})
        except jwt.DecodeError:
            return {}

    @classmethod
    def is_system_integrator_token(cls, token: str) -> bool:
        """Check xem token có phải là System Integrator token không"""
        payload = cls.decode_without_verification(token)
        return payload.get("token_type") == TokenType.SYSTEM_INTEGRATOR.value

    @staticmethod
    def generate_jti() -> str:
        """Generate unique JWT ID"""
        return secrets.token_hex(16)


class SystemIntegratorSecurityService:
    """Service để handle security operations"""

    @staticmethod
    def hash_client_secret(client_secret: str) -> str:
        """Hash client secret using bcrypt-like approach"""
        try:
            import bcrypt

            return bcrypt.hashpw(
                client_secret.encode("utf-8"), bcrypt.gensalt()
            ).decode("utf-8")
        except ImportError:
            # Fallback to hashlib if bcrypt not available
            salt = secrets.token_hex(16)
            return (
                hashlib.pbkdf2_hmac(
                    "sha256",
                    client_secret.encode("utf-8"),
                    salt.encode("utf-8"),
                    100000,
                ).hex()
                + ":"
                + salt
            )

    @staticmethod
    def verify_client_secret(client_secret: str, hashed_secret: str) -> bool:
        """Verify client secret"""
        try:
            import bcrypt

            return bcrypt.checkpw(
                client_secret.encode("utf-8"), hashed_secret.encode("utf-8")
            )
        except ImportError:
            # Fallback to hashlib verification
            if ":" in hashed_secret:
                stored_hash, salt = hashed_secret.split(":", 1)
                computed_hash = hashlib.pbkdf2_hmac(
                    "sha256",
                    client_secret.encode("utf-8"),
                    salt.encode("utf-8"),
                    100000,
                ).hex()
                return stored_hash == computed_hash
            return False

    @staticmethod
    def generate_client_id(prefix: str = "client") -> str:
        """Generate unique client ID"""
        timestamp = int(datetime.utcnow().timestamp())
        random_part = secrets.token_hex(8)
        return f"{prefix}-{timestamp}-{random_part}"

    @staticmethod
    def generate_client_secret(length: int = 32) -> str:
        """Generate secure client secret"""
        return secrets.token_urlsafe(length)

    @staticmethod
    def generate_jwt_secret(length: int = 32) -> str:
        """Generate JWT secret key"""
        return secrets.token_urlsafe(length)


class SystemIntegratorPermissionService:
    """Service để handle permission checking"""

    # Default permissions cho System Integrator
    DEFAULT_PERMISSIONS = {
        "royalty-integrator-001": {
            "royalty": [
                "GET:/v1/royalty.*",
                "POST:/v1/royalty.*",
                "PUT:/v1/royalty.*",
            ],
            "news": ["GET:/v1/news.*"],
            "user": ["GET:/v1/user.*"],
        }
    }

    @classmethod
    def check_permission(
        cls,
        client_id: str,
        route: str,
        method: str,
        table_management_id: str | None = None,
    ) -> bool:
        """Check permission cho System Integrator"""

        # Get permissions cho client
        client_permissions = cls.DEFAULT_PERMISSIONS.get(client_id, {})

        # Nếu có table_management_id, check specific table
        if table_management_id:
            table_permissions = client_permissions.get(table_management_id, [])
        else:
            # Check tất cả permissions
            table_permissions = []
            for perms in client_permissions.values():
                table_permissions.extend(perms)

        # Check từng permission
        for permission in table_permissions:
            if cls._matches_permission(permission, method, route):
                return True

        return False

    @staticmethod
    def _matches_permission(permission: str, method: str, route: str) -> bool:
        """Check xem route/method có match với permission pattern không"""
        try:
            perm_method, perm_route = permission.split(":", 1)

            # Check method
            if perm_method.upper() != method.upper():
                return False

            # Check route với regex pattern
            # Convert perm_route to regex (support .* wildcard)
            regex_pattern = perm_route.replace(".*", ".*")
            return bool(re.match(f"^{regex_pattern}$", route))

        except ValueError:
            return False

    @classmethod
    def get_available_scopes(cls, client_id: str) -> list[str]:
        """Get available scopes cho client"""
        client_permissions = cls.DEFAULT_PERMISSIONS.get(client_id, {})
        scopes = []

        for table, permissions in client_permissions.items():
            for perm in permissions:
                method, _ = perm.split(":", 1)
                scope = f"{table}:{method.lower()}"
                if scope not in scopes:
                    scopes.append(scope)

        return scopes


class SystemIntegratorTokenDetector:
    """Helper để detect System Integrator token trong middleware"""

    @staticmethod
    def extract_token_from_header(authorization_header: str) -> str | None:
        """Extract token từ Authorization header"""
        if not authorization_header:
            return None

        if authorization_header.startswith("Bearer "):
            return authorization_header[7:]  # Remove "Bearer "

        return None

    @staticmethod
    def is_system_integrator_request(authorization_header: str) -> bool:
        """Check xem request có phải từ System Integrator không"""
        token = SystemIntegratorTokenDetector.extract_token_from_header(
            authorization_header
        )
        if not token:
            return False

        return SystemIntegratorJWTService.is_system_integrator_token(token)
