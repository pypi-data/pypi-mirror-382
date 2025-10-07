#!/usr/bin/env python3
"""Base client for AIP SDK.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

import logging
import os
from typing import Any, NoReturn, Union

import httpx
from dotenv import load_dotenv

import glaip_sdk
from glaip_sdk._version import __version__ as SDK_VERSION
from glaip_sdk.config.constants import SDK_NAME
from glaip_sdk.exceptions import (
    AuthenticationError,
    ConflictError,
    ForbiddenError,
    NotFoundError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
)

# Set up logging without basicConfig (library best practice)
logger = logging.getLogger("glaip_sdk")
logger.addHandler(logging.NullHandler())

client_log = logging.getLogger("glaip_sdk.client")
client_log.addHandler(logging.NullHandler())


class BaseClient:
    """Base client with HTTP operations and authentication."""

    def __init__(
        self,
        api_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 30.0,
        *,
        parent_client: Union["BaseClient", None] = None,
        load_env: bool = True,
    ):
        """Initialize the base client.

        Args:
            api_url: API base URL
            api_key: API authentication key
            timeout: Request timeout in seconds
            parent_client: Parent client to adopt session/config from
            load_env: Whether to load environment variables
        """
        self._parent_client = parent_client
        self._session_scoped = False  # Mark as not session-scoped by default

        if parent_client is not None:
            # Adopt parent's session/config; DO NOT call super().__init__
            client_log.debug("Adopting parent client configuration")
            self.api_url = parent_client.api_url
            self.api_key = parent_client.api_key
            self._timeout = parent_client._timeout
            self.http_client = parent_client.http_client
        else:
            # Initialize as standalone client
            if load_env and not (api_url and api_key):
                # Only load .env file if explicit credentials not provided
                package_dir = os.path.dirname(glaip_sdk.__file__)
                env_file = os.path.join(package_dir, ".env")
                load_dotenv(env_file)

            self.api_url = api_url or os.getenv("AIP_API_URL")
            self.api_key = api_key or os.getenv("AIP_API_KEY")
            self._timeout = timeout

            if not self.api_url:
                client_log.error("AIP_API_URL not found in environment or parameters")
                raise ValueError("AIP_API_URL not found")
            if not self.api_key:
                client_log.error("AIP_API_KEY not found in environment or parameters")
                raise ValueError("AIP_API_KEY not found")

            client_log.info(f"Initializing client with API URL: {self.api_url}")
            self.http_client = self._build_client(timeout)

    def _build_client(self, timeout: float) -> httpx.Client:
        """Build HTTP client with configuration."""
        # For streaming operations, we need more generous read timeouts
        # while keeping reasonable connect timeouts
        timeout_config = httpx.Timeout(
            timeout=timeout,  # Total timeout
            connect=min(30.0, timeout),  # Connect timeout (max 30s)
            read=timeout,  # Read timeout (same as total for streaming)
            write=min(30.0, timeout),  # Write timeout (max 30s)
            pool=timeout,  # Pool timeout (same as total)
        )

        return httpx.Client(
            base_url=self.api_url,
            headers={
                "X-API-Key": self.api_key,
                "User-Agent": f"{SDK_NAME}/{SDK_VERSION}",
            },
            timeout=timeout_config,
            follow_redirects=True,
            http2=False,
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=100),
        )

    def _build_async_client(self, timeout: float) -> dict[str, Any]:
        """Build async client configuration (returns dict of kwargs for httpx.AsyncClient).

        Args:
            timeout: Request timeout in seconds

        Returns:
            Dictionary of kwargs for httpx.AsyncClient
        """
        # For streaming operations, we need more generous read timeouts
        # while keeping reasonable connect timeouts
        timeout_config = httpx.Timeout(
            timeout=timeout,  # Total timeout
            connect=min(30.0, timeout),  # Connect timeout (max 30s)
            read=timeout,  # Read timeout (same as total for streaming)
            write=min(30.0, timeout),  # Write timeout (max 30s)
            pool=timeout,  # Pool timeout (same as total)
        )

        return {
            "base_url": self.api_url,
            "headers": {
                "X-API-Key": self.api_key,
                "User-Agent": f"{SDK_NAME}/{SDK_VERSION}",
            },
            "timeout": timeout_config,
            "follow_redirects": True,
            "http2": False,
            "limits": httpx.Limits(max_keepalive_connections=10, max_connections=100),
        }

    @property
    def timeout(self) -> float:
        """Get current timeout value."""
        return self._timeout

    @timeout.setter
    def timeout(self, value: float) -> None:
        """Set timeout and rebuild client."""
        self._timeout = value
        if (
            hasattr(self, "http_client")
            and self.http_client
            and not self._session_scoped
            and not self._parent_client
        ):
            self.http_client.close()
            self.http_client = self._build_client(value)

    def _post_then_fetch(
        self,
        id_key: str,
        post_endpoint: str,
        get_endpoint_fmt: str,
        *,
        json: Any | None = None,
        data: Any | None = None,
        files: Any | None = None,
        **kwargs: Any,
    ) -> Any:
        """Helper for POST-then-GET pattern used in create methods.

        Args:
            id_key: Key in POST response containing the ID
            post_endpoint: Endpoint for POST request
            get_endpoint_fmt: Format string for GET endpoint (e.g., "/items/{id}")
            json: JSON data for POST
            data: Form data for POST
            files: Files for POST
            **kwargs: Additional kwargs for POST

        Returns:
            Full resource data from GET request
        """
        # Create the resource
        post_kwargs = {}
        if json is not None:
            post_kwargs["json"] = json
        if data is not None:
            post_kwargs["data"] = data
        if files is not None:
            post_kwargs["files"] = files
        post_kwargs.update(kwargs)

        response_data = self._request("POST", post_endpoint, **post_kwargs)

        # Extract the ID
        if isinstance(response_data, dict):
            resource_id = response_data.get(id_key)
        else:
            # Fallback: assume response_data is the ID directly
            resource_id = str(response_data)

        if not resource_id:
            raise ValueError(f"Backend did not return {id_key}")

        # Fetch the full resource details
        get_endpoint = get_endpoint_fmt.format(id=resource_id)
        return self._request("GET", get_endpoint)

    def _ensure_client_alive(self) -> None:
        """Ensure HTTP client is alive, recreate if needed."""
        if not hasattr(self, "http_client") or self.http_client is None:
            if not self._parent_client:
                self.http_client = self._build_client(self._timeout)
            return

        # Check if client is closed by attempting a simple operation
        try:
            # Try to access a property that would fail if closed
            _ = self.http_client.headers
        except (RuntimeError, AttributeError) as e:
            if "closed" in str(e).lower() or "NoneType" in str(e):
                client_log.debug("HTTP client was closed, recreating")
                if not self._parent_client:
                    self.http_client = self._build_client(self._timeout)
            else:
                raise

    def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make HTTP request with error handling."""
        # Ensure client is alive before making request
        self._ensure_client_alive()

        client_log.debug(f"Making {method} request to {endpoint}")
        try:
            response = self.http_client.request(method, endpoint, **kwargs)
            client_log.debug(f"Response status: {response.status_code}")
            return self._handle_response(response)
        except httpx.ConnectError as e:
            client_log.warning(
                f"Connection error on {method} {endpoint}, retrying once: {e}"
            )
            try:
                response = self.http_client.request(method, endpoint, **kwargs)
                client_log.debug(
                    f"Retry successful, response status: {response.status_code}"
                )
                return self._handle_response(response)
            except httpx.ConnectError:
                client_log.error(f"Retry failed for {method} {endpoint}: {e}")
                raise e

    def _parse_response_content(self, response: httpx.Response) -> Any | None:
        """Parse response content based on content type."""
        if response.status_code == 204:
            return None

        content_type = response.headers.get("content-type", "").lower()
        if "json" in content_type:
            try:
                return response.json()
            except ValueError:
                pass

        if 200 <= response.status_code < 300:
            return response.text
        else:
            return None  # Let _handle_response deal with error status codes

    def _handle_success_response(self, parsed: Any) -> Any:
        """Handle successful response with success flag."""
        if isinstance(parsed, dict) and "success" in parsed:
            if parsed.get("success"):
                return parsed.get("data", parsed)
            else:
                error_type = parsed.get("error", "UnknownError")
                message = parsed.get("message", "Unknown error")
                self._raise_api_error(
                    400,
                    message,
                    error_type,
                    payload=parsed,  # Using 400 as status since original response had error
                )

        return parsed

    def _get_error_message(self, response: httpx.Response) -> str:
        """Extract error message from response, preferring parsed content."""
        # Try to get error message from parsed content if available
        error_message = response.text
        try:
            parsed = response.json()
            if isinstance(parsed, dict) and "message" in parsed:
                error_message = parsed["message"]
            elif isinstance(parsed, str):
                error_message = parsed
        except (ValueError, TypeError):
            pass  # Use response.text as fallback
        return error_message

    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle HTTP response with proper error handling."""
        # Handle no-content success before general error handling
        if response.status_code == 204:
            return None

        # Handle error status codes
        if not (200 <= response.status_code < 300):
            error_message = self._get_error_message(response)
            self._raise_api_error(response.status_code, error_message)
            return None  # Won't be reached but helps with type checking

        parsed = self._parse_response_content(response)
        if parsed is None:
            return None

        return self._handle_success_response(parsed)

    def _raise_api_error(
        self,
        status: int,
        message: str,
        error_type: str | None = None,
        *,
        payload: Any | None = None,
    ) -> NoReturn:
        """Raise appropriate exception with rich context."""
        request_id = None
        try:
            request_id = self.http_client.headers.get("X-Request-Id")
        except Exception:
            pass

        mapping = {
            400: ValidationError,
            401: AuthenticationError,
            403: ForbiddenError,
            404: NotFoundError,
            408: TimeoutError,
            409: ConflictError,
            429: RateLimitError,
            500: ServerError,
            503: ServerError,
            504: TimeoutError,
        }

        exception_class = mapping.get(status, ValidationError)
        error_msg = f"HTTP {status}: {message}"
        if request_id:
            error_msg += f" (Request ID: {request_id})"

        raise exception_class(
            error_msg,
            status_code=status,
            error_type=error_type,
            payload=payload,
            request_id=request_id,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        if (
            hasattr(self, "http_client")
            and self.http_client
            and not self._session_scoped
            and not self._parent_client
        ):
            self.http_client.close()

    def __enter__(self) -> "BaseClient":
        """Context manager entry."""
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_val: BaseException | None,
        _exc_tb: Any,
    ) -> None:
        """Context manager exit."""
        # Only close if this is not session-scoped
        if not self._session_scoped:
            self.close()
