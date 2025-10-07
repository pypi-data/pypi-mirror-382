import asyncio
import io
import mimetypes
import os
from collections.abc import Callable
from datetime import datetime
from typing import Any, BinaryIO, Optional

import boto3
from botocore.config import Config
from botocore.exceptions import ClientError, NoCredentialsError

from cores.config.s3_config import s3_config
from cores.logger.logging import ApiLogger


class S3Logger:
    """
    Specialized logger cho S3 Service operations.

    Wraps ApiLogger với S3-specific methods, conditional logging,
    và performance tracking cho S3 operations.
    """

    @staticmethod
    def info(*messages: Any, **extra: Any) -> None:
        """Log S3 info messages."""
        if s3_config.should_log_operation("info"):
            # Add S3 context prefix
            prefixed_messages = [f"[S3] {msg}" for msg in messages]
            ApiLogger.s3_info(*prefixed_messages, **extra)

    @staticmethod
    def debug(*messages: Any, **extra: Any) -> None:
        """Log S3 debug messages."""
        if s3_config.should_log_operation("debug"):
            prefixed_messages = [f"[S3] {msg}" for msg in messages]
            ApiLogger.logging_s3(*prefixed_messages, **extra)

    @staticmethod
    def error(*messages: Any, **extra: Any) -> None:
        """Log S3 error messages."""
        if s3_config.should_log_operation("error"):
            prefixed_messages = [f"[S3] ERROR - {msg}" for msg in messages]
            ApiLogger.s3_error(*prefixed_messages, **extra)

    @staticmethod
    def success(*messages: Any, **extra: Any) -> None:
        """Log S3 success messages."""
        if s3_config.should_log_operation("success"):
            prefixed_messages = [f"[S3] SUCCESS - {msg}" for msg in messages]
            ApiLogger.s3_success(*prefixed_messages, **extra)

    @staticmethod
    def warning(*messages: Any, **extra: Any) -> None:
        """Log S3 warning messages."""
        if s3_config.should_log_operation("warning"):
            prefixed_messages = [f"[S3] WARNING - {msg}" for msg in messages]
            ApiLogger.warning(*prefixed_messages, **extra)

    @staticmethod
    def log_operation_start(operation: str, **context: Any) -> None:
        """
        Log bắt đầu một S3 operation.

        Args:
            operation: Tên operation (upload, download, etc.)
            **context: Context data (bucket, key, size, etc.)
        """
        if s3_config.S3_LOG_OPERATIONS:
            S3Logger.info(f"Starting {operation}", operation=operation, **context)

    @staticmethod
    def log_operation_success(
        operation: str,
        duration: Optional[float] = None,
        **context: Any
    ) -> None:
        """
        Log thành công của S3 operation với performance metrics.

        Args:
            operation: Tên operation
            duration: Thời gian thực hiện (seconds)
            **context: Context data
        """
        if s3_config.S3_LOG_OPERATIONS:
            log_data = {"operation": operation, **context}
            if duration is not None and s3_config.S3_LOG_PERFORMANCE:
                log_data["duration_seconds"] = f"{duration:.2f}"

            S3Logger.success(f"Completed {operation}", **log_data)

    @staticmethod
    def log_operation_error(operation: str, error: str, **context: Any) -> None:
        """
        Log lỗi của S3 operation.

        Args:
            operation: Tên operation
            error: Error message
            **context: Context data
        """
        S3Logger.error(
            f"Failed {operation}: {error}",
            operation=operation,
            error=error,
            **context
        )

    @staticmethod
    def log_performance_metrics(
        operation: str,
        file_size: int,
        duration: float,
        **extra: Any
    ) -> None:
        """
        Log performance metrics cho S3 operations.

        Args:
            operation: Tên operation
            file_size: Kích thước file (bytes)
            duration: Thời gian thực hiện (seconds)
            **extra: Additional metrics
        """
        if s3_config.S3_LOG_PERFORMANCE and duration > 0:
            speed_mbps = (file_size / duration / 1024 / 1024)
            S3Logger.debug(
                f"Performance metrics for {operation}",
                operation=operation,
                file_size_bytes=file_size,
                file_size_mb=f"{file_size/1024/1024:.2f}",
                duration_seconds=f"{duration:.2f}",
                speed_mbps=f"{speed_mbps:.2f}",
                **extra
            )


class S3Exception(Exception):
    """Custom exception cho S3 operations."""

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        original_error: Exception | None = None,
    ):
        self.message = message
        self.error_code = error_code
        self.original_error = original_error
        super().__init__(self.message)


class S3Object:
    """Đại diện cho một S3 object với metadata."""

    def __init__(
        self,
        key: str,
        bucket: str,
        size: int = 0,
        last_modified: datetime | None = None,
        etag: str | None = None,
        content_type: str | None = None,
        metadata: dict[str, Any] | None = None,
    ):
        self.key = key
        self.bucket = bucket
        self.size = size
        self.last_modified = last_modified
        self.etag = etag
        self.content_type = content_type
        self.metadata = metadata or {}

    def __repr__(self) -> str:
        return f"S3Object(key='{self.key}', bucket='{self.bucket}', size={self.size})"


class S3Service:
    """
    Service class cung cấp tất cả operations với S3-compatible storage.

    Hỗ trợ AWS S3, MinIO, Wasabi và các S3-compatible services khác.
    """

    _instances: dict[str, 'S3Service'] = {}

    def __init__(
        self,
        endpoint_url: str | None = None,
        region: str = 'us-east-1',
        access_key_id: str | None = None,
        secret_access_key: str | None = None,
        session_token: str | None = None,
        use_ssl: bool = True,
        verify_ssl: bool = True,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        """
        Khởi tạo S3 service.

        Args:
            endpoint_url: URL endpoint (None cho AWS S3 mặc định)
            region: AWS region
            access_key_id: Access key ID
            secret_access_key: Secret access key
            session_token: Session token (cho temporary credentials)
            use_ssl: Sử dụng HTTPS
            verify_ssl: Verify SSL certificates
            max_retries: Số lần retry khi có lỗi
            timeout: Timeout cho mỗi request (giây)
        """
        self.endpoint_url = endpoint_url
        self.region = region
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.session_token = session_token
        self.use_ssl = use_ssl
        self.verify_ssl = verify_ssl
        self.max_retries = max_retries
        self.timeout = timeout

        # Configuration cho boto3
        config = Config(
            retries={'max_attempts': max_retries, 'mode': 'adaptive'},
            connect_timeout=timeout,
            read_timeout=timeout,
            signature_version="s3v4"
        )

        try:
            # Khởi tạo S3 client
            self.client = boto3.client(
                's3',
                endpoint_url=endpoint_url,
                aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,
                aws_session_token=session_token,
                region_name=region,
                config=config,
                use_ssl=use_ssl,
                verify=verify_ssl,
            )

            S3Logger.info(
                "S3Service initialized successfully",
                endpoint=endpoint_url,
                region=region,
                ssl=use_ssl,
            )

        except NoCredentialsError as e:
            S3Logger.error("S3 credentials not found", error=str(e))
            raise S3Exception(
                "S3 credentials not configured", "NO_CREDENTIALS"
            ) from e
        except Exception as e:
            S3Logger.error("Failed to initialize S3 client", error=str(e))
            raise S3Exception(
                f"Failed to initialize S3 client: {str(e)}", "INIT_ERROR"
            ) from e

    @classmethod
    def get_instance(
        cls,
        instance_name: str = "default",
        **kwargs
    ) -> 'S3Service':
        """
        Singleton pattern - lấy hoặc tạo instance.

        Args:
            instance_name: Tên instance (cho multi-config)
            **kwargs: Tham số khởi tạo

        Returns:
            S3Service instance
        """
        if instance_name not in cls._instances:
            cls._instances[instance_name] = cls(**kwargs)
            S3Logger.debug(f"Created new S3Service instance: {instance_name}")

        return cls._instances[instance_name]

    async def health_check(self) -> bool:
        """
        Kiểm tra kết nối S3.

        Returns:
            bool: True nếu kết nối thành công
        """
        try:
            # Gọi list_buckets để test kết nối
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, self.client.list_buckets)

            S3Logger.success("S3 health check passed")
            return True

        except Exception as e:
            S3Logger.error(f"S3 health check failed: {str(e)}")
            return False

    def _get_content_type(self, file_path: str, content_type: str | None = None) -> str:
        """
        Xác định content type cho file.

        Args:
            file_path: Đường dẫn file
            content_type: Content type được chỉ định

        Returns:
            str: Content type
        """
        if content_type:
            return content_type

        content_type, _ = mimetypes.guess_type(file_path)
        return content_type or 'application/octet-stream'

    async def upload_file(
        self,
        file_path: str,
        bucket: str,
        key: str,
        content_type: Optional[str] = None,
        metadata: Optional[dict[str, str]] = None,
        acl: str = 'private',
        storage_class: str = 'STANDARD',
        server_side_encryption: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ) -> S3Object:
        """
        Upload file từ đường dẫn local.

        Args:
            file_path: Đường dẫn file local
            bucket: Tên bucket
            key: Key (path) trên S3
            content_type: Content type
            metadata: Metadata bổ sung
            acl: Access Control List
            storage_class: Storage class (STANDARD, REDUCED_REDUNDANCY, etc.)
            server_side_encryption: Server-side encryption (AES256, aws:kms)
            progress_callback: Callback function cho progress

        Returns:
            S3Object: Object đã upload

        Raises:
            S3Exception: Khi có lỗi upload
        """
        start_time = datetime.now()
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        S3Logger.log_operation_start(
            "upload_file",
            file_path=file_path,
            bucket=bucket,
            key=key,
            storage_class=storage_class,
            file_size_bytes=file_size
        )

        try:
            if not os.path.exists(file_path):
                raise S3Exception(f"File not found: {file_path}", "FILE_NOT_FOUND")

            file_size = os.path.getsize(file_path)
            content_type = self._get_content_type(file_path, content_type)

            # Chuẩn bị extra args
            extra_args = {
                'ContentType': content_type,
                'ACL': acl,
                'StorageClass': storage_class,
            }

            if metadata:
                extra_args['Metadata'] = metadata

            if server_side_encryption:
                extra_args['ServerSideEncryption'] = server_side_encryption

            # Upload file
            loop = asyncio.get_event_loop()

            if file_size > 100 * 1024 * 1024:  # > 100MB, sử dụng multipart upload
                S3Logger.debug(f"Using multipart upload for large file: {file_size} bytes")
                await loop.run_in_executor(
                    None,
                    lambda: self.client.upload_file(
                        file_path, bucket, key,
                        ExtraArgs=extra_args,
                        Callback=progress_callback,
                    )
                )
            else:
                await loop.run_in_executor(
                    None,
                    lambda: self.client.upload_file(
                        file_path, bucket, key,
                        ExtraArgs=extra_args,
                    )
                )

            # Lấy thông tin object đã upload
            obj_info = await self.get_object_info(bucket, key)

            duration = (datetime.now() - start_time).total_seconds()

            S3Logger.log_operation_success(
                "upload_file",
                duration=duration,
                bucket=bucket,
                key=key,
                file_size_bytes=file_size
            )

            # Log performance metrics
            S3Logger.log_performance_metrics(
                "upload_file",
                file_size,
                duration,
                bucket=bucket,
                key=key
            )

            return obj_info

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(
                f"S3 client error during upload: {error_code}",
                bucket=bucket,
                key=key,
                error=str(e),
            )
            raise S3Exception(f"Upload failed: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(
                "Unexpected error during upload",
                bucket=bucket,
                key=key,
                error=str(e),
            )
            raise S3Exception(f"Upload failed: {str(e)}", "UPLOAD_ERROR", e) from e

    async def upload_fileobj(
        self,
        fileobj: BinaryIO,
        bucket: str,
        key: str,
        content_type: str | None = None,
        metadata: dict[str, str | None] = None,
        acl: str = 'private',
        storage_class: str = 'STANDARD',
        server_side_encryption: str | None = None,
    ) -> S3Object:
        """
        Upload file từ file object.

        Args:
            fileobj: File object hoặc BytesIO
            bucket: Tên bucket
            key: Key trên S3
            content_type: Content type
            metadata: Metadata bổ sung
            acl: Access Control List
            storage_class: Storage class
            server_side_encryption: Server-side encryption

        Returns:
            S3Object: Object đã upload
        """
        start_time = datetime.now()
        S3Logger.info(
            "Starting file object upload",
            bucket=bucket,
            key=key,
            storage_class=storage_class,
        )

        try:
            # Đọc size nếu có thể
            file_size = 0
            if hasattr(fileobj, 'seek') and hasattr(fileobj, 'tell'):
                current_pos = fileobj.tell()
                fileobj.seek(0, 2)  # Seek to end
                file_size = fileobj.tell()
                fileobj.seek(current_pos)  # Seek back to original position

            content_type = content_type or self._get_content_type(key)

            # Chuẩn bị extra args
            extra_args = {
                'ContentType': content_type,
                'ACL': acl,
                'StorageClass': storage_class,
            }

            if metadata:
                extra_args['Metadata'] = metadata

            if server_side_encryption:
                extra_args['ServerSideEncryption'] = server_side_encryption

            # Upload file object
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.upload_fileobj(
                    fileobj, bucket, key,
                    ExtraArgs=extra_args,
                )
            )

            # Lấy thông tin object
            obj_info = await self.get_object_info(bucket, key)

            duration = (datetime.now() - start_time).total_seconds()
            S3Logger.success(
                "File object uploaded successfully",
                bucket=bucket,
                key=key,
                size=file_size,
                duration=f"{duration:.2f}s",
            )

            return obj_info

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during file object upload: {error_code}")
            raise S3Exception(f"Upload failed: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during file object upload: {str(e)}")
            raise S3Exception(f"Upload failed: {str(e)}", "UPLOAD_ERROR", e) from e

    async def download_file(
        self,
        bucket: str,
        key: str,
        file_path: str,
        progress_callback: Callable | None = None,
    ) -> str:
        """
        Download file từ S3 về local.

        Args:
            bucket: Tên bucket
            key: Key trên S3
            file_path: Đường dẫn lưu file local
            progress_callback: Callback function cho progress

        Returns:
            str: Đường dẫn file đã download
        """
        start_time = datetime.now()
        S3Logger.info(
            "Starting file download",
            bucket=bucket,
            key=key,
            file_path=file_path,
        )

        try:
            # Tạo thư mục nếu cần
            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            # Download file
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.download_file(
                    bucket, key, file_path,
                    Callback=progress_callback,
                )
            )

            file_size = os.path.getsize(file_path)
            duration = (datetime.now() - start_time).total_seconds()

            S3Logger.success(
                "File downloaded successfully",
                bucket=bucket,
                key=key,
                file_path=file_path,
                size=file_size,
                duration=f"{duration:.2f}s",
                speed=f"{file_size/duration/1024/1024:.2f} MB/s" if duration > 0 else "N/A",
            )

            return file_path

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during download: {error_code}")
            raise S3Exception(f"Download failed: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during download: {str(e)}")
            raise S3Exception(f"Download failed: {str(e)}", "DOWNLOAD_ERROR", e) from e

    async def download_fileobj(
        self,
        bucket: str,
        key: str,
        fileobj: BinaryIO,
    ) -> int:
        """
        Download file từ S3 vào file object.

        Args:
            bucket: Tên bucket
            key: Key trên S3
            fileobj: File object để ghi dữ liệu

        Returns:
            int: Số bytes đã download
        """
        start_time = datetime.now()
        S3Logger.info("Starting file object download", bucket=bucket, key=key)

        try:
            # Download vào file object
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.download_fileobj(bucket, key, fileobj)
            )

            # Tính size nếu có thể
            downloaded_size = 0
            if hasattr(fileobj, 'tell'):
                downloaded_size = fileobj.tell()

            duration = (datetime.now() - start_time).total_seconds()
            S3Logger.success(
                "File object downloaded successfully",
                bucket=bucket,
                key=key,
                size=downloaded_size,
                duration=f"{duration:.2f}s",
            )

            return downloaded_size

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during file object download: {error_code}")
            raise S3Exception(f"Download failed: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during file object download: {str(e)}")
            raise S3Exception(f"Download failed: {str(e)}", "DOWNLOAD_ERROR", e) from e

    async def get_object_content(
        self,
        bucket: str,
        key: str,
        encoding: str = 'utf-8',
    ) -> str | bytes:
        """
        Lấy nội dung file dưới dạng string hoặc bytes.

        Args:
            bucket: Tên bucket
            key: Key trên S3
            encoding: Encoding cho text file (None cho binary)

        Returns:
            (str, bytes]: Nội dung file
        """
        S3Logger.info("Getting object content", bucket=bucket, key=key)

        try:
            # Sử dụng BytesIO để download
            buffer = io.BytesIO()
            await self.download_fileobj(bucket, key, buffer)

            content = buffer.getvalue()

            if encoding:
                content = content.decode(encoding)
                S3Logger.debug(f"Decoded content as {encoding}")

            S3Logger.success("Object content retrieved", bucket=bucket, key=key, size=len(content))
            return content

        except Exception as e:
            S3Logger.error(f"Failed to get object content: {str(e)}")
            raise S3Exception(f"Failed to get content: {str(e)}", "GET_CONTENT_ERROR", e) from e

    async def generate_presigned_url(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        http_method: str = 'GET',
        params: dict[str, Any | None] = None,
    ) -> str:
        """
        Tạo presigned URL cho object.

        Args:
            bucket: Tên bucket
            key: Key trên S3
            expiration: Thời gian hết hạn (giây)
            http_method: HTTP method (GET, PUT, POST, DELETE)
            params: Parameters bổ sung

        Returns:
            str: Presigned URL
        """
        S3Logger.info(
            "Generating presigned URL",
            bucket=bucket,
            key=key,
            method=http_method,
            expiration=expiration,
        )

        try:
            # Chuẩn bị parameters
            url_params = {
                'Bucket': bucket,
                'Key': key,
            }

            if params:
                url_params.update(params)

            # Tạo presigned URL
            loop = asyncio.get_event_loop()

            if http_method.upper() == 'GET':
                operation = 'get_object'
            elif http_method.upper() == 'PUT':
                operation = 'put_object'
            elif http_method.upper() == 'DELETE':
                operation = 'delete_object'
            else:
                raise S3Exception(f"Unsupported HTTP method: {http_method}", "INVALID_METHOD")

            presigned_url = await loop.run_in_executor(
                None,
                lambda: self.client.generate_presigned_url(
                    operation,
                    Params=url_params,
                    ExpiresIn=expiration,
                    HttpMethod=http_method.upper()
                )
            )

            S3Logger.success(
                "Presigned URL generated",
                bucket=bucket,
                key=key,
                method=http_method,
                expires_in=f"{expiration}s",
            )

            return presigned_url

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during presigned URL generation: {error_code}")
            raise S3Exception(f"Failed to generate presigned URL: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during presigned URL generation: {str(e)}")
            raise S3Exception(f"Failed to generate presigned URL: {str(e)}", "PRESIGN_ERROR", e) from e

    async def generate_presigned_post(
        self,
        bucket: str,
        key: str,
        expiration: int = 3600,
        conditions: list[Any | None] = None,
        fields: dict[str, str | None] = None,
    ) -> dict[str, Any]:
        """
        Tạo presigned POST data để upload trực tiếp từ frontend.

        Args:
            bucket: Tên bucket
            key: Key trên S3
            expiration: Thời gian hết hạn (giây)
            conditions: Điều kiện cho upload
            fields: Fields bổ sung

        Returns:
            Dict: Presigned POST data với url và fields
        """
        S3Logger.info(
            "Generating presigned POST",
            bucket=bucket,
            key=key,
            expiration=expiration,
        )

        try:
            # Chuẩn bị fields và conditions
            post_fields = fields or {}
            post_conditions = conditions or []

            # Tạo presigned POST
            loop = asyncio.get_event_loop()
            presigned_post = await loop.run_in_executor(
                None,
                lambda: self.client.generate_presigned_post(
                    Bucket=bucket,
                    Key=key,
                    Fields=post_fields,
                    Conditions=post_conditions,
                    ExpiresIn=expiration,
                )
            )

            S3Logger.success(
                "Presigned POST generated",
                bucket=bucket,
                key=key,
                expires_in=f"{expiration}s",
            )

            return presigned_post

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during presigned POST generation: {error_code}")
            raise S3Exception(f"Failed to generate presigned POST: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during presigned POST generation: {str(e)}")
            raise S3Exception(f"Failed to generate presigned POST: {str(e)}", "PRESIGN_POST_ERROR", e) from e

    async def get_object_info(
        self,
        bucket: str,
        key: str,
    ) -> S3Object:
        """
        Lấy thông tin metadata của object.

        Args:
            bucket: Tên bucket
            key: Key trên S3

        Returns:
            S3Object: Thông tin object
        """
        S3Logger.debug("Getting object info", bucket=bucket, key=key)

        try:
            # Lấy object metadata
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.head_object(Bucket=bucket, Key=key)
            )

            # Tạo S3Object từ response
            obj = S3Object(
                key=key,
                bucket=bucket,
                size=response.get('ContentLength', 0),
                last_modified=response.get('LastModified'),
                etag=response.get('ETag', '').strip('"'),
                content_type=response.get('ContentType'),
                metadata=response.get('Metadata', {}),
            )

            S3Logger.debug("Object info retrieved", bucket=bucket, key=key, size=obj.size)
            return obj

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == '404':
                raise S3Exception(f"Object not found: {key}", "OBJECT_NOT_FOUND", e) from e
            S3Logger.error(f"S3 client error getting object info: {error_code}")
            raise S3Exception(f"Failed to get object info: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error getting object info: {str(e)}")
            raise S3Exception(f"Failed to get object info: {str(e)}", "GET_INFO_ERROR", e) from e

    async def object_exists(
        self,
        bucket: str,
        key: str,
    ) -> bool:
        """
        Kiểm tra object có tồn tại không.

        Args:
            bucket: Tên bucket
            key: Key trên S3

        Returns:
            bool: True nếu object tồn tại
        """
        try:
            await self.get_object_info(bucket, key)
            return True
        except S3Exception as e:
            if e.error_code == "OBJECT_NOT_FOUND":
                return False
            raise

    async def delete_object(
        self,
        bucket: str,
        key: str,
    ) -> bool:
        """
        Xóa object.

        Args:
            bucket: Tên bucket
            key: Key trên S3

        Returns:
            bool: True nếu xóa thành công
        """
        S3Logger.info("Deleting object", bucket=bucket, key=key)

        try:
            # Xóa object
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.delete_object(Bucket=bucket, Key=key)
            )

            S3Logger.success("Object deleted successfully", bucket=bucket, key=key)
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during delete: {error_code}")
            raise S3Exception(f"Failed to delete object: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during delete: {str(e)}")
            raise S3Exception(f"Failed to delete object: {str(e)}", "DELETE_ERROR", e) from e

    async def delete_objects(
        self,
        bucket: str,
        keys: list[str],
    ) -> dict[str, list[str]]:
        """
        Xóa nhiều objects cùng lúc.

        Args:
            bucket: Tên bucket
            keys: List các keys cần xóa

        Returns:
            Dict: Kết quả với 'deleted' và 'errors'
        """
        S3Logger.info(f"Deleting {len(keys)} objects", bucket=bucket)

        try:
            # Chuẩn bị delete request
            delete_objects = [{'Key': key} for key in keys]

            # Xóa objects
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.delete_objects(
                    Bucket=bucket,
                    Delete={'Objects': delete_objects}
                )
            )

            deleted = [obj['Key'] for obj in response.get('Deleted', [])]
            errors = [
                f"{obj['Key']}: {obj['Code']} - {obj['Message']}"
                for obj in response.get('Errors', [])
            ]

            S3Logger.success(
                "Bulk delete completed",
                bucket=bucket,
                deleted_count=len(deleted),
                error_count=len(errors),
            )

            if errors:
                S3Logger.warning("Some objects failed to delete", errors=errors)

            return {'deleted': deleted, 'errors': errors}

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during bulk delete: {error_code}")
            raise S3Exception(f"Failed to delete objects: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during bulk delete: {str(e)}")
            raise S3Exception(f"Failed to delete objects: {str(e)}", "BULK_DELETE_ERROR", e) from e

    async def copy_object(
        self,
        source_bucket: str,
        source_key: str,
        dest_bucket: str,
        dest_key: str,
        metadata: dict[str, str | None] = None,
        storage_class: str = 'STANDARD',
    ) -> S3Object:
        """
        Copy object từ vị trí này sang vị trí khác.

        Args:
            source_bucket: Bucket nguồn
            source_key: Key nguồn
            dest_bucket: Bucket đích
            dest_key: Key đích
            metadata: Metadata mới
            storage_class: Storage class

        Returns:
            S3Object: Object đã copy
        """
        S3Logger.info(
            "Copying object",
            source=f"{source_bucket}/{source_key}",
            dest=f"{dest_bucket}/{dest_key}",
        )

        try:
            # Chuẩn bị copy source
            copy_source = {'Bucket': source_bucket, 'Key': source_key}

            # Chuẩn bị extra args
            extra_args = {'StorageClass': storage_class}
            if metadata:
                extra_args['Metadata'] = metadata
                extra_args['MetadataDirective'] = 'REPLACE'

            # Copy object
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.copy_object(
                    CopySource=copy_source,
                    Bucket=dest_bucket,
                    Key=dest_key,
                    **extra_args,
                )
            )

            # Lấy thông tin object đã copy
            obj_info = await self.get_object_info(dest_bucket, dest_key)

            S3Logger.success(
                "Object copied successfully",
                source=f"{source_bucket}/{source_key}",
                dest=f"{dest_bucket}/{dest_key}",
                size=obj_info.size,
            )

            return obj_info

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during copy: {error_code}")
            raise S3Exception(f"Failed to copy object: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during copy: {str(e)}")
            raise S3Exception(f"Failed to copy object: {str(e)}", "COPY_ERROR", e) from e

    async def list_objects(
        self,
        bucket: str,
        prefix: str = '',
        delimiter: str = '',
        max_keys: int = 1000,
        continuation_token: str | None = None,
    ) -> dict[str, Any]:
        """
        List objects trong bucket.

        Args:
            bucket: Tên bucket
            prefix: Prefix filter
            delimiter: Delimiter (thường là '/' để list như folder)
            max_keys: Số lượng tối đa trả về
            continuation_token: Token để phân trang

        Returns:
            Dict: Danh sách objects và thông tin phân trang
        """
        S3Logger.debug(
            "Listing objects",
            bucket=bucket,
            prefix=prefix,
            max_keys=max_keys,
        )

        try:
            # Chuẩn bị parameters
            params = {
                'Bucket': bucket,
                'MaxKeys': max_keys,
            }

            if prefix:
                params['Prefix'] = prefix
            if delimiter:
                params['Delimiter'] = delimiter
            if continuation_token:
                params['ContinuationToken'] = continuation_token

            # List objects
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.list_objects_v2(**params)
            )

            # Xử lý kết quả
            objects = []
            for obj in response.get('Contents', []):
                s3_obj = S3Object(
                    key=obj['Key'],
                    bucket=bucket,
                    size=obj['Size'],
                    last_modified=obj['LastModified'],
                    etag=obj.get('ETag', '').strip('"'),
                )
                objects.append(s3_obj)

            result = {
                'objects': objects,
                'common_prefixes': response.get('CommonPrefixes', []),
                'is_truncated': response.get('IsTruncated', False),
                'next_continuation_token': response.get('NextContinuationToken'),
                'key_count': response.get('KeyCount', 0),
            }

            S3Logger.success(
                "Objects listed successfully",
                bucket=bucket,
                count=len(objects),
                truncated=result['is_truncated'],
            )

            return result

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during list: {error_code}")
            raise S3Exception(f"Failed to list objects: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during list: {str(e)}")
            raise S3Exception(f"Failed to list objects: {str(e)}", "LIST_ERROR", e) from e

    async def create_bucket(
        self,
        bucket: str,
        region: str | None = None,
        acl: str = 'private',
    ) -> bool:
        """
        Tạo bucket mới.

        Args:
            bucket: Tên bucket
            region: Region (None để sử dụng region mặc định)
            acl: Access Control List

        Returns:
            bool: True nếu tạo thành công
        """
        S3Logger.info("Creating bucket", bucket=bucket, region=region or self.region)

        try:
            # Chuẩn bị create bucket configuration
            create_args = {'Bucket': bucket, 'ACL': acl}

            # Nếu region khác us-east-1, cần LocationConstraint
            target_region = region or self.region
            if target_region != 'us-east-1':
                create_args['CreateBucketConfiguration'] = {
                    'LocationConstraint': target_region
                }

            # Tạo bucket
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.create_bucket(**create_args)
            )

            S3Logger.success("Bucket created successfully", bucket=bucket, region=target_region)
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyOwnedByYou':
                S3Logger.info("Bucket already exists and owned by you", bucket=bucket)
                return True
            elif error_code == 'BucketAlreadyExists':
                S3Logger.error("Bucket name already taken", bucket=bucket)
                raise S3Exception(f"Bucket name '{bucket}' already exists", error_code, e) from e
            else:
                S3Logger.error(f"S3 client error during bucket creation: {error_code}")
                raise S3Exception(f"Failed to create bucket: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during bucket creation: {str(e)}")
            raise S3Exception(f"Failed to create bucket: {str(e)}", "CREATE_BUCKET_ERROR", e) from e

    async def delete_bucket(
        self,
        bucket: str,
        force: bool = False,
    ) -> bool:
        """
        Xóa bucket.

        Args:
            bucket: Tên bucket
            force: Xóa tất cả objects trước khi xóa bucket

        Returns:
            bool: True nếu xóa thành công
        """
        S3Logger.info("Deleting bucket", bucket=bucket, force=force)

        try:
            if force:
                # Xóa tất cả objects trước
                S3Logger.info("Force delete: removing all objects first", bucket=bucket)

                # List và xóa tất cả objects
                continuation_token = None
                total_deleted = 0

                while True:
                    list_result = await self.list_objects(
                        bucket=bucket,
                        max_keys=1000,
                        continuation_token=continuation_token,
                    )

                    if list_result['objects']:
                        keys = [obj.key for obj in list_result['objects']]
                        delete_result = await self.delete_objects(bucket, keys)
                        total_deleted += len(delete_result['deleted'])

                    if not list_result['is_truncated']:
                        break

                    continuation_token = list_result['next_continuation_token']

                S3Logger.info(f"Deleted {total_deleted} objects before bucket deletion", bucket=bucket)

            # Xóa bucket
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                None,
                lambda: self.client.delete_bucket(Bucket=bucket)
            )

            S3Logger.success("Bucket deleted successfully", bucket=bucket)
            return True

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during bucket deletion: {error_code}")
            raise S3Exception(f"Failed to delete bucket: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during bucket deletion: {str(e)}")
            raise S3Exception(f"Failed to delete bucket: {str(e)}", "DELETE_BUCKET_ERROR", e) from e

    async def list_buckets(self) -> list[dict[str, Any]]:
        """
        List tất cả buckets.

        Returns:
            list[Dict]: Danh sách buckets với name và creation_date
        """
        S3Logger.debug("Listing all buckets")

        try:
            # List buckets
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.list_buckets()
            )

            buckets = []
            for bucket in response.get('Buckets', []):
                buckets.append({
                    'name': bucket['Name'],
                    'creation_date': bucket['CreationDate'],
                })

            S3Logger.success(f"Listed {len(buckets)} buckets")
            return buckets

        except ClientError as e:
            error_code = e.response['Error']['Code']
            S3Logger.error(f"S3 client error during bucket listing: {error_code}")
            raise S3Exception(f"Failed to list buckets: {str(e)}", error_code, e) from e
        except Exception as e:
            S3Logger.error(f"Unexpected error during bucket listing: {str(e)}")
            raise S3Exception(f"Failed to list buckets: {str(e)}", "LIST_BUCKETS_ERROR", e) from e


# Backward compatibility - Wasabi service
class S3WasabiService(S3Service):
    """
    Wasabi-specific S3 service - backward compatibility wrapper.

    Deprecated: Sử dụng S3Service với endpoint_url thay thế.
    """

    instance = None

    def __init__(self, url: str, region: str, access_key_id: str, secret_access_key: str):
        """
        Initialize Wasabi service.

        Args:
            url: Wasabi endpoint URL
            region: Region
            access_key_id: Access key ID
            secret_access_key: Secret access key
        """
        S3Logger.warning("S3WasabiService is deprecated. Use S3Service instead.")

        super().__init__(
            endpoint_url=url,
            region=region,
            access_key_id=access_key_id,
            secret_access_key=secret_access_key,
        )

        S3WasabiService.instance = self

    def init(self, url: str, region: str, access_key_id: str, secret_access_key: str):
        """Backward compatibility method."""
        self.__init__(url, region, access_key_id, secret_access_key)
