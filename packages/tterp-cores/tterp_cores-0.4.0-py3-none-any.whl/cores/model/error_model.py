from fastapi import HTTPException


class GenericHTTPException(HTTPException):
    """
    Exception chung cho toàn bộ hệ thống, dùng cho business logic.
    Có thể mở rộng thêm các thuộc tính như code, message, ...
    """

    def __init__(self, status_code: int, code: str, message: str):
        super().__init__(status_code=status_code, detail=message)
        self.code = code
        self.message = message
