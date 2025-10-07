import json
import os
import secrets
from datetime import datetime, timedelta


class TokenManager:
    """
    Quản lý token xác thực 24 giờ, lưu vào file
    """

    def __init__(self, token_file: str = "tokens.json"):
        self.token_file = token_file
        self._ensure_token_file()

    def _ensure_token_file(self):
        """Đảm bảo file token tồn tại"""
        if not os.path.exists(self.token_file):
            with open(self.token_file, "w") as f:
                json.dump({}, f)

    def _load_tokens(self) -> dict:
        """Load tokens từ file"""
        with open(self.token_file) as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def _save_tokens(self, tokens: dict):
        """Lưu tokens vào file"""
        with open(self.token_file, "w") as f:
            json.dump(tokens, f)

    def _clean_expired_tokens(self, tokens: dict) -> dict:
        """Xóa các token đã hết hạn"""
        now = datetime.now()
        return {
            k: v
            for k, v in tokens.items()
            if datetime.fromisoformat(v["expires_at"]) > now
        }

    def create_token(self, user_id: str, expires_in_hours: int = 24) -> str:
        """
        Tạo token mới với thời hạn

        Args:
            user_id: ID của người dùng
            expires_in_hours: Thời hạn tính bằng giờ (mặc định 24)

        Returns:
            Token được tạo
        """
        # Tạo token ngẫu nhiên
        token = secrets.token_urlsafe(32)

        # Tính thời gian hết hạn
        now = datetime.now()
        expires_at = now + timedelta(hours=expires_in_hours)

        # Load tokens hiện có và làm sạch
        tokens = self._load_tokens()
        tokens = self._clean_expired_tokens(tokens)

        # Thêm token mới
        tokens[token] = {
            "user_id": user_id,
            "created_at": now.isoformat(),
            "expires_at": expires_at.isoformat(),
        }

        # Lưu lại vào file
        self._save_tokens(tokens)

        return token

    def verify_token(self, token: str) -> tuple[bool, str | None]:
        """
        Xác thực token

        Args:
            token: Token cần xác thực

        Returns:
            Tuple (valid, user_id): (True, user_id) nếu hợp lệ,
            (False, None) nếu không
        """
        # Load tokens
        tokens = self._load_tokens()
        tokens = self._clean_expired_tokens(tokens)

        # Kiểm tra token có tồn tại không
        if token not in tokens:
            return False, None

        # Lấy thông tin
        token_data = tokens[token]
        expires_at = datetime.fromisoformat(token_data["expires_at"])

        # Kiểm tra thời hạn
        if expires_at < datetime.now():
            # Xóa token hết hạn
            del tokens[token]
            self._save_tokens(tokens)
            return False, None

        return True, token_data["user_id"]

    def revoke_token(self, token: str) -> bool:
        """
        Thu hồi token

        Args:
            token: Token cần thu hồi

        Returns:
            True nếu token được thu hồi thành công, False nếu không tìm thấy
        """
        tokens = self._load_tokens()

        if token in tokens:
            del tokens[token]
            self._save_tokens(tokens)
            return True

        return False


# Singleton instance
token_manager = TokenManager()
