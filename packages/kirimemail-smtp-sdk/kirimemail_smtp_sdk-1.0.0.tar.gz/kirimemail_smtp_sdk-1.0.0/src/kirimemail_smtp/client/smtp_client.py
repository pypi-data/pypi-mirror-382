"""
HTTP client for the Kirim.Email SMTP API.
"""

import asyncio
import base64
from collections.abc import AsyncGenerator
from typing import Any, Optional

import httpx

from ..exceptions import (
    ApiException,
    AuthenticationException,
    NotFoundException,
    ServerException,
    ValidationException,
)


class SmtpClient:
    """
    HTTP client for the Kirim.Email SMTP API.

    Provides methods for making HTTP requests with authentication,
    error handling, and support for multipart file uploads and streaming.
    """

    def __init__(
        self,
        username: Optional[str] = None,
        token: Optional[str] = None,
        base_url: str = "https://smtp-app.kirim.email",
        timeout: float = 30.0,
        retries: int = 3,
    ) -> None:
        """
        Initialize the SMTP client.

        Args:
            username: Username for basic authentication
            token: Token for basic authentication
            base_url: Base URL for the API
            timeout: Request timeout in seconds
            retries: Number of retry attempts for failed requests
        """
        self.username = username
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries

        # Initialize HTTP client
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=httpx.Timeout(timeout),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10),
        )

    async def __aenter__(self) -> "SmtpClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client."""
        await self._client.aclose()

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers."""
        headers: dict[str, str] = {
            "User-Agent": "kirimemail-smtp-sdk/1.0.0",
            "Accept": "application/json",
        }

        if self.username and self.token:
            auth_string = f"{self.username}:{self.token}"
            auth_header = base64.b64encode(auth_string.encode()).decode()
            headers["Authorization"] = f"Basic {auth_header}"

        return headers

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any
    ) -> dict[str, Any]:
        """
        Make an HTTP request with authentication and error handling.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional arguments for httpx request

        Returns:
            Response data as dictionary

        Raises:
            ApiException: For API errors
            AuthenticationException: For authentication errors
            ValidationException: For validation errors
            NotFoundException: For not found errors
            ServerException: For server errors
        """
        # Add authentication headers
        headers = kwargs.pop("headers", {})
        headers.update(self._get_auth_headers())
        kwargs["headers"] = headers

        # Set default content type for JSON requests
        if method in ["POST", "PUT", "PATCH"] and "json" in kwargs:
            headers.setdefault("Content-Type", "application/json")

        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        # Make request with retries
        last_exception = None
        for attempt in range(self.retries + 1):
            try:
                response = await self._client.request(method, url, **kwargs)
                return await self._handle_response(response)

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_exception = e
                if attempt < self.retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** attempt)
                    continue
                break

            except (ApiException, AuthenticationException, ValidationException,
                   NotFoundException, ServerException):
                # Don't retry on client errors
                raise

        # If we get here, all retries failed
        if last_exception:
            raise ApiException(f"Request failed after {self.retries + 1} attempts: {last_exception}")
        raise ApiException(f"Request failed after {self.retries + 1} attempts")

    async def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Handle HTTP response and raise appropriate exceptions.

        Args:
            response: HTTP response object

        Returns:
            Response data as dictionary

        Raises:
            ApiException: For API errors
            AuthenticationException: For authentication errors
            ValidationException: For validation errors
            NotFoundException: For not found errors
            ServerException: For server errors
        """
        try:
            data = await response.json() if response.content else {}
        except Exception:
            data = {}

        if response.is_success:
            return data

        # Handle error responses
        status_code = response.status_code
        message = data.get("message", data.get("error", "Unknown API error"))
        errors = data.get("errors", {})

        if status_code in [400, 422]:
            raise ValidationException(message, status_code, errors, data)
        elif status_code in [401, 403]:
            raise AuthenticationException(message, status_code, errors, data)
        elif status_code == 404:
            raise NotFoundException(message, status_code, errors, data)
        elif status_code >= 500:
            raise ServerException(message, status_code, errors, data)
        else:
            raise ApiException(message, status_code, errors, data)

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a GET request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
        )

    async def post(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a POST request with JSON data.

        Args:
            endpoint: API endpoint
            data: Request data
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "POST",
            endpoint,
            json=data,
            headers=headers,
        )

    async def post_multipart(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        files: Optional[list[dict[str, Any]]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a POST request with multipart form data.

        Args:
            endpoint: API endpoint
            data: Form data
            files: List of files to upload
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        # Prepare multipart data
        multipart_data: dict[str, Any] = {}
        files_data: dict[str, Any] = {}

        # Add form fields
        if data:
            for key, value in data.items():
                if isinstance(value, list):
                    for i, item in enumerate(value):
                        multipart_data[f"{key}[{i}]"] = str(item)
                else:
                    multipart_data[key] = str(value)

        # Add files
        if files:
            for file_info in files:
                field = file_info["field"]
                filename = file_info["filename"]
                content = file_info["content"]
                content_type = file_info.get("content_type", "application/octet-stream")

                if isinstance(content, str):
                    content = content.encode()

                files_data[field] = (filename, content, content_type)

        return await self._make_request(
            "POST",
            endpoint,
            data=multipart_data,
            files=files_data,
            headers=headers,
        )

    async def put(
        self,
        endpoint: str,
        data: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a PUT request.

        Args:
            endpoint: API endpoint
            data: Request data
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "PUT",
            endpoint,
            json=data,
            headers=headers,
        )

    async def delete(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> dict[str, Any]:
        """
        Make a DELETE request.

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Returns:
            Response data as dictionary
        """
        return await self._make_request(
            "DELETE",
            endpoint,
            params=params,
            headers=headers,
        )

    async def stream(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        headers: Optional[dict[str, str]] = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """
        Stream response data (for log streaming).

        Args:
            endpoint: API endpoint
            params: Query parameters
            headers: Additional headers

        Yields:
            Parsed JSON objects from the stream
        """
        request_headers = self._get_auth_headers()
        if headers:
            request_headers.update(headers)

        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        try:
            async with self._client.stream(
                "GET",
                url,
                params=params,
                headers=request_headers,
                timeout=httpx.Timeout(60.0),  # Longer timeout for streaming
            ) as response:
                if not response.is_success:
                    await self._handle_response(response)

                buffer = ""
                async for chunk in response.aiter_text():
                    buffer += chunk
                    lines = buffer.split("\n")
                    buffer = lines.pop() or ""  # Keep incomplete line in buffer

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        # Handle Server-Sent Events format
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            if data == "[DONE]":
                                return
                            try:
                                import json
                                yield json.loads(data)
                            except json.JSONDecodeError:
                                continue
                        else:
                            # Try to parse as JSON directly
                            try:
                                import json
                                yield json.loads(line)
                            except json.JSONDecodeError:
                                continue

        except (httpx.TimeoutException, httpx.NetworkError) as e:
            raise ApiException(f"Streaming failed: {e}") from e

    def set_base_url(self, base_url: str) -> None:
        """
        Update the base URL for the API.

        Args:
            base_url: New base URL
        """
        self.base_url = base_url.rstrip("/")
        self._client.base_url = base_url.rstrip("/")

    def get_base_url(self) -> str:
        """
        Get the current base URL.

        Returns:
            Current base URL
        """
        return self.base_url

    def set_auth(self, username: str, token: str) -> None:
        """
        Update authentication credentials.

        Args:
            username: Username for basic authentication
            token: Token for basic authentication
        """
        self.username = username
        self.token = token

    def has_auth(self) -> bool:
        """
        Check if authentication is configured.

        Returns:
            True if authentication is configured
        """
        return bool(self.username and self.token)
