"""
Module cung cấp hệ thống logging tập trung cho ứng dụng.

Module này chứa các class và hàm để:
- Định nghĩa các custom formatters và handlers cho logging
- Tạo các loggers chuyên biệt cho các loại log khác nhau
- Cung cấp API logging tập trung với context
- Tự động xoay vòng các file log theo kích thước
"""

import logging
import os
from datetime import datetime, timedelta
from logging.handlers import RotatingFileHandler
from typing import Any

from cores.logger.context import LogContext


class VietnamTimeFormatter(logging.Formatter):
    """
    Formatter tùy chỉnh với múi giờ Việt Nam (UTC+7).

    Tự động thêm 7 giờ vào timestamp của log record để hiển thị theo giờ Việt Nam.
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str | None = None) -> str:
        """
        Format thời gian của log record theo múi giờ Việt Nam.

        Args:
            record: Log record cần format thời gian
            datefmt: Format thời gian tùy chỉnh, None để sử dụng ISO format

        Returns:
            Chuỗi thời gian đã được format
        """
        dt = datetime.fromtimestamp(record.created) + timedelta(hours=7)
        if datefmt:
            return dt.strftime(datefmt)
        else:
            return dt.isoformat()


class CustomRotatingFileHandler(RotatingFileHandler):
    """
    Handler tùy chỉnh để tạo tên file sao lưu theo định dạng ngày tháng.

    Khi file log đạt đến kích thước tối đa, handler sẽ tạo file backup
    với tên bao gồm ngày tháng hiện tại.
    """

    def __init__(self, base_filename: str, *args: Any, **kwargs: Any) -> None:
        """
        Khởi tạo handler với tên file cơ sở.

        Args:
            base_filename: Tên file cơ sở (không bao gồm phần mở rộng .log)
            *args: Các tham số bổ sung cho RotatingFileHandler
            **kwargs: Các tham số từ khóa bổ sung cho RotatingFileHandler
        """
        self.base_filename = base_filename
        super().__init__(base_filename + ".log", *args, **kwargs)

    def doRollover(self) -> None:
        """
        Thực hiện xoay vòng file log.

        Đóng file hiện tại, đổi tên thành filename-DD-MM-YYYY.log,
        và tạo file mới.
        """
        self.close()
        timestamp = datetime.now().strftime("%d-%m-%Y")
        backup_filename = f"{self.base_filename}-{timestamp}.log"
        self.rename_file(self.baseFilename, backup_filename)
        super().doRollover()

    def rename_file(self, old_filename: str, new_filename: str) -> None:
        """
        Đổi tên file nếu tồn tại.

        Args:
            old_filename: Tên file cũ
            new_filename: Tên file mới
        """
        if os.path.exists(old_filename):
            os.rename(old_filename, new_filename)


# Tạo thư mục logs nếu chưa tồn tại
os.makedirs("log", exist_ok=True)

# Formatter chi tiết cho mọi loại log
error_formatter = VietnamTimeFormatter(
    "%(asctime)s [%(module)s | %(levelname)s] @ "
    "%(pathname)s : %(lineno)d : %(funcName)s\n%(message)s",
    datefmt="%d/%m/%Y %I:%M:%S%p",
)

# Tạo handlers với đường dẫn mới
info_handler = CustomRotatingFileHandler("log/info", maxBytes=10485760, backupCount=5)
info_handler.setLevel(logging.INFO)
info_handler.setFormatter(error_formatter)

error_handler = CustomRotatingFileHandler("log/error", maxBytes=10485760, backupCount=5)
error_handler.setLevel(logging.ERROR)
error_handler.setFormatter(error_formatter)

debug_handler = CustomRotatingFileHandler("log/debug", maxBytes=10485760, backupCount=5)
debug_handler.setLevel(logging.DEBUG)
debug_handler.setFormatter(error_formatter)

success_handler = CustomRotatingFileHandler(
    "log/success", maxBytes=10485760, backupCount=5
)
success_handler.setLevel(logging.DEBUG)
success_handler.setFormatter(error_formatter)

curl_handler = CustomRotatingFileHandler(
    "log/curl_log", maxBytes=10485760, backupCount=5
)
curl_handler.setLevel(logging.ERROR)
curl_handler.setFormatter(error_formatter)

email_handler = CustomRotatingFileHandler(
    "log/err_email", maxBytes=10485760, backupCount=5
)
email_handler.setLevel(logging.ERROR)
email_handler.setFormatter(error_formatter)

task_handler = CustomRotatingFileHandler("log/task", maxBytes=10485760, backupCount=5)
task_handler.setLevel(logging.ERROR)
task_handler.setFormatter(error_formatter)

s3_handler = CustomRotatingFileHandler("log/s3", maxBytes=10485760, backupCount=5)
s3_handler.setLevel(logging.DEBUG)
s3_handler.setFormatter(error_formatter)

# Tạo loggers
general_logger = logging.getLogger("general")
general_logger.setLevel(logging.ERROR)
general_logger.addHandler(error_handler)

debug_logger = logging.getLogger("debug_config")
debug_logger.setLevel(logging.DEBUG)
debug_logger.addHandler(debug_handler)

success_logger = logging.getLogger("success_config")
success_logger.setLevel(logging.DEBUG)
success_logger.addHandler(success_handler)

info_logger = logging.getLogger("info_config")
info_logger.setLevel(logging.INFO)
info_logger.addHandler(info_handler)

curl_logger = logging.getLogger("curl_log")
curl_logger.setLevel(logging.ERROR)
curl_logger.addHandler(curl_handler)

email_logger = logging.getLogger("email")
email_logger.setLevel(logging.ERROR)
email_logger.addHandler(email_handler)

task_logger = logging.getLogger("task")
task_logger.setLevel(logging.ERROR)
task_logger.addHandler(task_handler)

s3_logger = logging.getLogger("s3")
s3_logger.setLevel(logging.DEBUG)
s3_logger.addHandler(s3_handler)

logger = logging.getLogger(__name__)


class MyLogger:
    """
    Class cung cấp truy cập trực tiếp đến các logger chính.

    Attributes:
        general_logger: Logger chung cho các thông báo lỗi
        debug_logger: Logger cho thông tin debug
        info_logger: Logger cho thông tin thông thường
        s3_logger: Logger riêng cho S3 operations
    """

    general_logger = general_logger
    debug_logger = debug_logger
    info_logger = info_logger
    s3_logger = s3_logger


class ApiLogger:
    """
    Lớp ApiLogger xử lý log tập trung cho toàn bộ ứng dụng.

    Tự động thêm context từ LogContext vào mỗi log message.
    Cung cấp các phương thức tĩnh để log ở các cấp độ khác nhau.
    """

    @staticmethod
    def _get_log_context() -> dict[str, Any]:
        """
        Lấy context cho log hiện tại.

        Returns:
            Dictionary chứa context hiện tại từ LogContext
        """
        return LogContext.get_context()

    @staticmethod
    def _format_message(message: Any, extra: dict[str, Any] | None = None) -> str:
        """
        Format message với context.

        Args:
            message: Thông điệp cần log
            extra: Thông tin bổ sung để thêm vào context

        Returns:
            Thông điệp đã được format với context
        """
        context = ApiLogger._get_log_context()

        # Thêm extra vào context nếu có
        if extra:
            context.update(extra)

        context_str = ""
        if context and any(context.values()):
            context_str = f" | Context: {context}"

        return f"{message}{context_str}"

    @staticmethod
    def error(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin ở cấp độ ERROR.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            general_logger.error(formatted_message, stacklevel=2)

    @staticmethod
    def debug(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin ở cấp độ DEBUG.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            debug_logger.debug(formatted_message, stacklevel=2)

    @staticmethod
    def info(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin ở cấp độ INFO.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            info_logger.info(formatted_message, stacklevel=2)

    @staticmethod
    def warning(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin ở cấp độ WARNING.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            general_logger.warning(formatted_message, stacklevel=2)

    @staticmethod
    def success(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin thành công.

        Sử dụng cấp độ INFO nhưng ghi vào file success.log.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            success_logger.info(formatted_message, stacklevel=2)

    @staticmethod
    def logging_curl(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin HTTP requests/responses.

        Sử dụng cấp độ ERROR để ghi vào file curl_log.log.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            curl_logger.error(formatted_message, stacklevel=2)

    @staticmethod
    def logging_email(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin liên quan đến email.

        Sử dụng cấp độ ERROR để ghi vào file err_email.log.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            email_logger.error(formatted_message, stacklevel=2)

    @staticmethod
    def logging_task(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin liên quan đến background tasks.

        Sử dụng cấp độ ERROR để ghi vào file task.log.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            task_logger.error(formatted_message, stacklevel=2)

    @staticmethod
    def logging_s3(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin liên quan đến S3 operations.

        Ghi log chi tiết tất cả các thao tác với S3 như upload, download,
        generate presigned URLs, object management, v.v.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context (bucket, key, size, etc.)
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            s3_logger.debug(formatted_message, stacklevel=2)

    @staticmethod
    def s3_info(*messages: Any, **extra: Any) -> None:
        """
        Log thông tin S3 ở level INFO.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            s3_logger.info(formatted_message, stacklevel=2)

    @staticmethod
    def s3_error(*messages: Any, **extra: Any) -> None:
        """
        Log lỗi S3 operations.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            s3_logger.error(formatted_message, stacklevel=2)

    @staticmethod
    def s3_success(*messages: Any, **extra: Any) -> None:
        """
        Log thành công S3 operations.

        Args:
            *messages: Các thông điệp cần log
            **extra: Thông tin bổ sung để thêm vào context
        """
        for message in messages:
            formatted_message = ApiLogger._format_message(message, extra)
            s3_logger.info(formatted_message, stacklevel=2)

    @staticmethod
    def debug_query(*queries: Any) -> None:
        """
        Log các SQL queries ở dạng đã được compile.

        Hữu ích để debug các SQL queries được tạo bởi SQLAlchemy.

        Args:
            *queries: Các query objects từ SQLAlchemy cần log
        """
        for query in queries:
            debug_logger.debug(
                str(query.compile(compile_kwargs={"literal_binds": True})),
                stacklevel=2,
            )
