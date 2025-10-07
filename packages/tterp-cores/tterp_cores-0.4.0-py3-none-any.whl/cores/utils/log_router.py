import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer


# Sử dụng os.getenv thay vì decouple để tránh lỗi type checking
def get_config(key: str, default: Any = None) -> Any:
    """Lấy giá trị từ environment variables"""
    return os.getenv(key, default)

# Khởi tạo router
router = APIRouter()
security = HTTPBearer()

# Danh sách các file log được phép truy cập (đường dẫn tương đối từ project root)
ALLOWED_LOG_FILES = [
    "log/curl_log.log",
    "log/debug.log",
    "log/err_email.log",
    "log/error.log",
    "log/info.log",
    "log/success.log",
    "log/task.log"
]

# Lấy password từ .env, mặc định là 'erpteam'
LOG_ACCESS_PASSWORD = get_config("LOG_ACCESS_PASSWORD", default="erpteam")

def verify_password(credentials: HTTPAuthorizationCredentials = Depends(security)) -> bool:
    """Xác thực password để truy cập log"""
    if credentials.credentials != LOG_ACCESS_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Sai mật khẩu truy cập log"
        )
    return True

def read_last_lines(file_path: str, num_lines: int) -> list[str]:
    """Đọc n dòng cuối cùng của file, tương tự tail -n"""
    try:
        with open(file_path, 'rb') as file:
            # Di chuyển con trỏ đến cuối file
            file.seek(0, 2)
            file_size = file.tell()

            if file_size == 0:
                return []

            lines: list[str] = []
            buffer = b''
            position = file_size

            # Đọc ngược từ cuối file
            while position > 0 and len(lines) < num_lines:
                # Đọc từng chunk 1024 bytes
                chunk_size = min(1024, position)
                position -= chunk_size
                file.seek(position)
                chunk = file.read(chunk_size)

                # Thêm vào buffer
                buffer = chunk + buffer

                # Tách các dòng
                while b'\n' in buffer and len(lines) < num_lines:
                    line, buffer = buffer.rsplit(b'\n', 1)
                    if line:  # Bỏ qua dòng trống
                        lines.insert(0, line.decode('utf-8', errors='ignore'))

            # Thêm dòng cuối nếu còn trong buffer
            if buffer and len(lines) < num_lines:
                lines.insert(0, buffer.decode('utf-8', errors='ignore'))

            return lines[:num_lines]

    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail=f"Không tìm thấy file log: {file_path}"
        )
    except PermissionError:
        raise HTTPException(
            status_code=403,
            detail=f"Không có quyền đọc file: {file_path}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi khi đọc file: {str(e)}"
        )

@router.get("/logs/tail")
async def get_log_tail(
    file_path: str = Query(default="log/error.log", description="Đường dẫn file log"),
    lines: int = Query(default=50, ge=1, le=1000, description="Số dòng cần đọc (1-1000)"),
    _: bool = Depends(verify_password)
) -> dict[str, Any]:
    """API đọc n dòng cuối của file log
    
    Args:
        file_path: Đường dẫn file log (mặc định: /log/error.log)
        lines: Số dòng cần đọc từ cuối file (mặc định: 50, tối đa: 1000)
        
    Headers:
        Authorization: Bearer <password> (mặc định: erpteam)
        
    Returns:
        {
            "file_path": "/log/error.log",
            "lines_requested": 50,
            "lines_returned": 45,
            "content": ["dòng log 1", "dòng log 2", ...]
        }
    """

    # Kiểm tra file có trong danh sách được phép không
    if file_path not in ALLOWED_LOG_FILES:
        raise HTTPException(
            status_code=403,
            detail=f"File không được phép truy cập. Chỉ cho phép: {', '.join(ALLOWED_LOG_FILES)}"
        )

    # Chuyển đổi đường dẫn tương đối thành tuyệt đối
    absolute_path = os.path.abspath(file_path)

    # Kiểm tra file có tồn tại không
    if not os.path.exists(absolute_path):
        raise HTTPException(
            status_code=404,
            detail=f"File không tồn tại: {file_path}"
        )

    # Đọc nội dung file
    log_lines = read_last_lines(absolute_path, lines)

    return {
        "file_path": file_path,
        "lines_requested": lines,
        "lines_returned": len(log_lines),
        "content": log_lines
    }

@router.get("/logs/files")
async def get_available_log_files(
    _: bool = Depends(verify_password)
) -> dict[str, list[str]]:
    """Lấy danh sách các file log có thể truy cập
    
    Headers:
        Authorization: Bearer <password>
        
    Returns:
        {
            "allowed_files": ["/log/error.log", "/log/debug.log", ...],
            "existing_files": ["/log/error.log", ...]
        }
    """

    existing_files = []
    for file_path in ALLOWED_LOG_FILES:
        absolute_path = os.path.abspath(file_path)
        if os.path.exists(absolute_path):
            existing_files.append(file_path)

    return {
        "allowed_files": ALLOWED_LOG_FILES,
        "existing_files": existing_files
    }
