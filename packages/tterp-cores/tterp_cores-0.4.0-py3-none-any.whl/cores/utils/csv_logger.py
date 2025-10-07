# cores/utils/csv_logger.py

import csv
import json
import uuid
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from pathlib import Path

from fastapi import Request

LOG_DIR = Path("log/csv")
LOG_DIR.mkdir(parents=True, exist_ok=True)

# Sử dụng ContextVar để lưu trữ context an toàn trong môi trường async
_request_context: ContextVar[dict] = ContextVar("request_context", default={})

def set_request_context(request: Request):
    requester = getattr(request.state, 'requester', None)
    context = {
        "requester_id": requester.user_id if requester else None,
        "ip": request.client.host if request.client else "unknown",
        "request_id": request.headers.get("X-Request-ID", str(uuid.uuid4())),
    }
    _request_context.set(context)

def get_request_context() -> dict:
    return _request_context.get()

def clear_request_context():
    _request_context.set({})

def log_to_csv(
    module: str,
    action: str,
    requester_id: int = None,
    params=None,
    status="success",
    error_message=None,
    ip: str = None,
    request_id: str = None,
):
    """Ghi log vào file CSV, chỉ lưu các thông tin cần thiết để truy vết"""
    log_file = LOG_DIR / f"{module}_log.csv"

    # Lấy thông tin từ context nếu không có
    context = get_request_context()
    if context:
        if requester_id is None:
            requester_id = context.get("requester_id")
        if ip is None:
            ip = context.get("ip")
        if request_id is None:
            request_id = context.get("request_id")

    # Xử lý params để tránh lỗi serialization
    params_str = ""
    if params:
        try:
            if isinstance(params, dict):
                # Lọc các đối tượng phức tạp không serialize được
                filtered_params = {
                    k: (
                        str(v)
                        if hasattr(v, "__dict__")
                        and not isinstance(
                            v, (str, int, float, bool, list, dict)
                        )
                        else v
                    )
                    for k, v in params.items()
                }
                params_str = json.dumps(
                    filtered_params, ensure_ascii=False, default=str
                )
            else:
                params_str = str(params)
        except Exception:
            params_str = str(params)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "module": module,
        "action": action,
        "requester_id": requester_id,
        "params": params_str,
        "status": status,
        "error_message": error_message or "",
        "ip": ip or "",
        "request_id": request_id or "",
    }

    write_header = not log_file.exists()
    with open(log_file, "a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=log_entry.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(log_entry)


def auto_log(module: str, action: str = None):
    """
    Decorator để tự động log mọi hàm public của usecase/service.
    Log cả exception, log thêm IP/request_id nếu có trong context.
    """

    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Lọc bỏ các tham số không serialize được từ kwargs
            filtered_params = {}
            for k, v in kwargs.items():
                if k not in ["request", "req"]:  # Không log request object
                    if hasattr(v, "__dict__") and not isinstance(
                        v, (str, int, float, bool, list, dict)
                    ):
                        # Chỉ lưu class name hoặc các thuộc tính cơ bản
                        if hasattr(v, "id"):
                            filtered_params[k] = (
                                f"{v.__class__.__name__}(id={v.id})"
                            )
                        else:
                            filtered_params[k] = f"{v.__class__.__name__}"
                    else:
                        filtered_params[k] = v

            # Lấy requester_id từ context
            context = get_request_context()
            requester_id = context.get("requester_id")

            try:
                result = await func(*args, **kwargs)
                log_to_csv(
                    module=module,
                    action=action or func.__name__,
                    requester_id=requester_id,
                    params=filtered_params,
                    status="success",
                )
                return result
            except Exception as e:
                log_to_csv(
                    module=module,
                    action=action or func.__name__,
                    requester_id=requester_id,
                    params=filtered_params,
                    status="fail",
                    error_message=str(e),
                )
                raise

        return async_wrapper

    return decorator
