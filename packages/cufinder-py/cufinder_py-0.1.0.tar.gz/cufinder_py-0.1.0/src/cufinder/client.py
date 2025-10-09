"""HTTP client for the Cufinder API."""

import time
import uuid
from typing import Any, Dict, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .exceptions import (
    AuthenticationError,
    CreditLimitError,
    CufinderError,
    NetworkError,
    RateLimitError,
    ValidationError,
)


class CufinderClient:
    """
    Main CUFinder API client class.
    
    Provides a type-safe interface for interacting with the CUFinder B2B data enrichment API.
    Follows SOLID principles:
    - Single Responsibility: Handles HTTP communication only
    - Open/Closed: Extensible through service classes
    - Liskov Substitution: Can be replaced with mock implementations
    - Interface Segregation: Provides focused interfaces
    - Dependency Inversion: Depends on abstractions, not concretions
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.cufinder.io/v2",
        timeout: int = 30,
        max_retries: int = 3,
    ):
        """
        Initialize the CUFinder client.
        
        Args:
            api_key: Your CUFinder API key
            base_url: Base URL for the API (default: https://api.cufinder.io/v2)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum number of retries for failed requests (default: 3)
        """
        if not api_key:
            raise ValidationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize session with retry strategy
        self.session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Set default headers
        self.session.headers.update({
            "x-api-key": api_key,
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": f"cufinder-py/0.1.0",
        })

    def _generate_request_id(self) -> str:
        """Generate a unique request ID."""
        return f"req_{int(time.time() * 1000)}_{uuid.uuid4().hex[:12]}"

    def _handle_response_error(self, response: requests.Response) -> CufinderError:
        """Handle HTTP response errors."""
        try:
            error_data = response.json()
            message = error_data.get("message", response.reason)
        except (ValueError, KeyError):
            message = response.reason or "Unknown error"

        status_code = response.status_code

        if status_code == 401:
            return AuthenticationError(message)
        elif status_code == 400:
            return ValidationError(message, error_data if "error_data" in locals() else None)
        elif status_code == 402:
            return CreditLimitError(message)
        elif status_code == 429:
            retry_after = response.headers.get("retry-after")
            retry_after_int = int(retry_after) if retry_after and retry_after.isdigit() else None
            return RateLimitError(message, retry_after_int)
        elif status_code in [500, 502, 503, 504]:
            return NetworkError(f"Server error: {message}", status_code)
        else:
            return CufinderError(
                message,
                "API_ERROR",
                status_code,
                error_data if "error_data" in locals() else None,
            )

    def _handle_request_error(self, error: Exception) -> CufinderError:
        """Handle request errors."""
        if isinstance(error, requests.exceptions.Timeout):
            return NetworkError("Request timeout", 408)
        elif isinstance(error, requests.exceptions.ConnectionError):
            return NetworkError("Unable to connect to API", 0)
        elif isinstance(error, requests.exceptions.RequestException):
            return NetworkError(f"Request failed: {str(error)}", 0)
        else:
            return CufinderError(
                f"Unknown request error: {str(error)}",
                "REQUEST_ERROR",
            )

    def request(
        self,
        method: str,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Make a raw HTTP request to the API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            url: Request URL (relative to base_url)
            params: Query parameters
            data: Request body data
            headers: Additional headers
            timeout: Request timeout in seconds
            
        Returns:
            Response data as dictionary
            
        Raises:
            CufinderError: If the request fails
        """
        # Build full URL
        if url.startswith("http"):
            full_url = url
        else:
            full_url = f"{self.base_url}/{url.lstrip('/')}"

        # Prepare headers
        request_headers = self.session.headers.copy()
        if headers:
            request_headers.update(headers)
        
        # Add request ID for tracking
        request_headers["X-Request-ID"] = self._generate_request_id()

        try:
            response = self.session.request(
                method=method.upper(),
                url=full_url,
                params=params,
                data=data,
                headers=request_headers,
                timeout=timeout or self.timeout,
            )

            # Handle HTTP errors
            if not response.ok:
                raise self._handle_response_error(response)

            return response.json()

        except CufinderError:
            raise
        except Exception as error:
            raise self._handle_request_error(error)

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make a GET request."""
        return self.request("GET", url, params=params, headers=headers, timeout=timeout)

    def post(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make a POST request."""
        return self.request("POST", url, data=data, headers=headers, timeout=timeout)

    def put(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make a PUT request."""
        return self.request("PUT", url, data=data, headers=headers, timeout=timeout)

    def delete(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make a DELETE request."""
        return self.request("DELETE", url, headers=headers, timeout=timeout)

    def patch(
        self,
        url: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Make a PATCH request."""
        return self.request("PATCH", url, data=data, headers=headers, timeout=timeout)

    def get_api_key(self) -> str:
        """Get the current API key (masked for security)."""
        if not self.api_key:
            return ""
        
        if len(self.api_key) > 8:
            return f"{self.api_key[:4]}...{self.api_key[-4:]}"
        return "****"

    def get_base_url(self) -> str:
        """Get the base URL."""
        return self.base_url

    def set_api_key(self, api_key: str) -> None:
        """Update the API key."""
        if not api_key:
            raise ValidationError("API key cannot be empty")
        
        self.api_key = api_key
        self.session.headers["x-api-key"] = api_key

    def set_base_url(self, base_url: str) -> None:
        """Update the base URL."""
        self.base_url = base_url.rstrip("/")

    def set_timeout(self, timeout: int) -> None:
        """Update the request timeout."""
        self.timeout = timeout
