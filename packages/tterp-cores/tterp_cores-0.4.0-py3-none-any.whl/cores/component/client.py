"""client.py
Module cung cấp lớp `ClientBase` hỗ trợ giao tiếp HTTP nội bộ giữa các
micro-service.

Các chức năng chính:
1. Tạo và gắn **JWT token** vào header để xác thực service-to-service.
2. Cung cấp phương thức `curl_api` tiện lợi cho mọi HTTP method phổ biến.
3. Hỗ trợ ghi log chi tiết bằng `ApiLogger` khi có lỗi hoặc khi response
   trả về status code không mong muốn.
4. Hỗ trợ upload multipart file thông qua phương thức `multipart_request`.

Việc refactor chỉ thêm tài liệu và type hints, **không thay đổi logic** nhằm
đảm bảo toàn bộ test hiện tại vẫn pass.
"""

from __future__ import annotations

import traceback
from io import BytesIO
from typing import Any

import httpx
from fastapi import HTTPException, status

from cores.config import service_config
from cores.logger.enhanced_logging import LogCategory, logger


class ClientBase:
    _app = None
    _base_url: str = ""
    _jwt_token: str = ""
    _headers: dict = {}

    async def set_jwt_token_and_headers(self, target_service_id: str) -> None:
        """Khởi tạo JWT token & headers phục vụ cho các request nội bộ.

        Args:
            target_service_id: ID của service đích (service sẽ nhận request).
        """

        # Import động để tránh circular import khi module được load sớm
        from cores.depends.authorization import (
            AuthService,  # pylint: disable=import-error
        )

        # JWT token dành cho **service** (không phải user)
        self._jwt_token = AuthService.create_auth_token(
            service_config.AUTH_SECRET_KEY
        )

        # Các header chung cho mọi request nội bộ
        self._headers = {
            "service-management-id": service_config.BASE_SERVICE_ID,
            "target-service-id": target_service_id,
            "user-token": await AuthService.create_user_token(
                service_config.BASE_SERVICE_ID
            ),
        }

    async def curl_api(
        self,
        method: str = "GET",
        uri: str = "",
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        response_type: str = "json",
        external_headers: dict[str, str] | None = None,
    ) -> Any:
        """Thực hiện HTTP request và trả về dữ liệu theo *response_type*.

        Args:
            method: HTTP method (GET/POST/PUT/PATCH/DELETE).
            uri: Đường dẫn URI (được nối với `_base_url`).
            body: Payload JSON cho request (nếu có).
            params: Query params cho request (nếu có).
            response_type: Loại response mong muốn – `"json"` hoặc `"binary"`.
            external_headers: Header bổ sung sẽ ghi đè header mặc định.

        Returns:
            Dữ liệu JSON (dict) hoặc `BytesIO` tùy theo `response_type`.
        """

        body = body or {}
        params = params or {}
        headers = self._prepare_headers(external_headers)
        link = self._base_url + uri
        client = httpx.AsyncClient(timeout=10, headers=headers, app=self._app)
        try:
            response = await self._make_request(
                client, method, link, body, params, headers
            )
            return await self._handle_response(
                response, response_type, link, method, params
            )
        except httpx.RequestError as exc:
            await self._log_error(exc, link, method, params, "RequestError")
        except Exception as exc:
            await self._log_error(exc, link, method, params, "Exception")
        finally:
            await self._close_client(client)

    def _prepare_headers(
        self, external_headers: dict[str, str] | None
    ) -> dict[str, str]:
        """Chuẩn bị header cho request.

        Thứ tự ưu tiên: `Authorization` + header nội bộ (`_headers`) +
        `external_headers` – các key trùng sẽ bị *external_headers* ghi đè.
        """
        headers: dict[str, str] = {"X-Requested-With": "XMLHttpRequest"}

        if self._jwt_token:
            headers["Authorization"] = f"Bearer {self._jwt_token}"

        if self._headers:
            headers.update(self._headers)

        if external_headers:
            headers.update(external_headers)

        return headers

    async def _make_request(
        self,
        client: httpx.AsyncClient,
        method: str,
        link: str,
        body: dict[str, Any],
        params: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:

        method = method.upper()

        if method == "GET":
            return await client.get(link, headers=headers, params=body)
        elif method == "POST":
            return await client.post(
                link, headers=headers, json=body, params=params
            )
        elif method == "PUT":
            return await client.put(
                link, headers=headers, json=body, params=params
            )
        elif method == "PATCH":
            return await client.patch(
                link, headers=headers, json=body, params=params
            )
        elif method == "DELETE":
            return await client.request(
                "delete", link, headers=headers, json=body
            )
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    async def _handle_response(
        self,
        response: httpx.Response,
        response_type: str,
        link: str,
        method: str,
        params: dict[str, Any],
    ) -> Any:
        if 500 > response.status_code > 202:
            logger.error(
                f"{link}, method: {method} failed with status {response.status_code}. {response.text}",
                category=LogCategory.SYSTEM,
            )

        if response_type == "binary":
            if response.status_code == 200:
                return BytesIO(response.content)
        else:
            return self._process_json_response(response)

    def _process_json_response(self, response: httpx.Response) -> Any:
        try:
            result = response.json()
            if isinstance(result, dict) and "status_code" not in result:
                result["status_code"] = response.status_code
            return result
        except httpx.DecodingError:
            logger.error(
                f"DecodingError for response: {response.text}",
                category=LogCategory.SYSTEM,
            )
            raise

    async def _log_error(
        self,
        exc: Exception,
        link: str,
        method: str,
        params: dict[str, Any],
        error_type: str,
    ) -> None:
        error_message = f"{error_type} for {link}, method: {method}, params: {params} - {exc}"
        logger.error(error_message, category=LogCategory.SYSTEM)

    async def _close_client(self, client: httpx.AsyncClient) -> None:
        try:
            await client.aclose()
        except Exception:
            logger.error(
                f"Error closing client: {traceback.format_exc()}",
                category=LogCategory.SYSTEM,
            )

    async def multipart_request(
        self,
        uri: str = "",
        data: list[tuple[str, Any]] | None = None,
        files: Any | None = None,
    ) -> Any:
        """Upload file sử dụng multipart/form-data."""
        if data is None:
            data = []
        headers = {
            "Authorization": "Bearer " + self._jwt_token,
            "X-Requested-With": "XMLHttpRequest",
        }
        client = httpx.AsyncClient(timeout=10, headers=headers, app=self._app)
        try:
            r = None
            link = self._base_url + uri
            r = await client.post(
                link, headers=headers, data=data, files=files
            )
            if r and r.status_code != 502:
                response = r.json()
                response["status_code"] = r.status_code
                return response
            else:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Service is unavailable.",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except httpx.NetworkError as exc:
            logger.error(
                f"NetworkError for {exc.request.url} - {exc}",
                category=LogCategory.SYSTEM,
            )
        except httpx.TimeoutException as exc:
            logger.error(
                f"TimeoutException for {exc.request.url} - {exc}",
                category=LogCategory.SYSTEM,
            )
        except httpx.ProtocolError as exc:
            logger.error(
                f"ProtocolError for {exc.request.url} - {exc}",
                category=LogCategory.SYSTEM,
            )
        except httpx.DecodingError as exc:
            logger.error(
                f"DecodingError for {exc.request.url} - {exc}",
                category=LogCategory.SYSTEM,
            )
        except httpx.TooManyRedirects as exc:
            logger.error(
                f"TooManyRedirects for {exc.request.url} - {exc}",
                category=LogCategory.SYSTEM,
            )
        except httpx.StreamError as exc:
            logger.error(
                f"StreamError for {link} - {exc}",
                category=LogCategory.SYSTEM,
            )
        except httpx.HTTPError as exc:
            logger.error(
                f"HTTP Exception - {link} {exc}",
                category=LogCategory.SYSTEM,
            )
        finally:
            await client.aclose()

    async def curl_api_with_auth(
        self,
        _auth_init,
        method: str = "GET",
        uri: str = "",
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        response_type: str = "json",
        external_headers: dict[str, str] | None = None,
    ) -> Any:
        """Thực hiện HTTP request với xác thực và trả về dữ liệu theo *response_type*.

        Args:
            _auth_init: Hàm khởi tạo để thực hiện xác thực (thường là `set_jwt_token_and_headers`).
            method: HTTP method (GET/POST/PUT/PATCH/DELETE).
            uri: Đường dẫn URI (được nối với `_base_url`).
            body: Payload JSON cho request (nếu có).
            params: Query params cho request (nếu có).
            response_type: Loại response mong muốn – `"json"` hoặc `"binary"`.
            external_headers: Header bổ sung sẽ ghi đè header mặc định.

        Returns:
            Dữ liệu JSON (dict) hoặc `BytesIO` tùy theo `response_type`.
        """
        await _auth_init()
        return await self.curl_api(
            method=method,
            uri=uri,
            body=body,
            params=params,
            response_type=response_type,
            external_headers=external_headers,
        )
