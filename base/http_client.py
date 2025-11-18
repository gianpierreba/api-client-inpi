"""
Base HTTP client for API requests.

This module provides a base HTTP client with error handling,
retry logic, and common functionality.
"""

from typing import Any, Dict, Optional

import requests

from config import Config
from exceptions import ApiRequestError


class BaseHttpClient:
    """Base HTTP client with common functionality."""

    def __init__(
        self,
        base_url: str,
        timeout: int = None,
    ):
        """
        Initialize HTTP client.

        Parameters:
            base_url:
                Base URL for API requests.
            timeout:
                Request timeout in seconds. Defaults to Config.DEFAULT_TIMEOUT.
        """
        self.base_url = base_url
        self.timeout = timeout or Config.DEFAULT_TIMEOUT
        self.session = requests.Session()

    def _make_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make HTTP request with error handling.

        Parameters:
            method (str):
                HTTP method (GET, POST, etc.)
            url (str):
                Request URL
            headers:
                Request headers.
            params:
                Query parameters.
            json_data:
                JSON data for request body.
            **kwargs:
                Additional arguments for requests.

        Returns:
            requests.Response:
                Response object.

        Raises:
            ApiRequestError: If request fails
        """
        try:
            response = self.session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                timeout=self.timeout,
                **kwargs,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.Timeout as e:
            raise ApiRequestError(
                f"Request timeout after {self.timeout} seconds: {url}",
                status_code=None,
                response_text=str(e),
            ) from e
        except requests.exceptions.HTTPError as e:
            raise ApiRequestError(
                f"HTTP error occurred: {e}",
                status_code=e.response.status_code if e.response else None,
                response_text=e.response.text if e.response else None,
            ) from e
        except requests.exceptions.RequestException as e:
            raise ApiRequestError(
                f"Request failed: {e}",
                status_code=None,
                response_text=str(e),
            ) from e

    def get(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make GET request.

        Args:
            endpoint (str):
                API endpoint (will be appended to base_url).
            headers:
                Request headers.
            params:
                Query parameters.
            **kwargs:
                Additional arguments.

        Returns:
            requests.Response:
                Response object.
        """
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith("http") else endpoint
        return self._make_request(
            method="GET",
            url=url,
            headers=headers,
            params=params,
            **kwargs,
        )

    def post(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make POST request.

        Args:
            endpoint (str):
                API endpoint (will be appended to base_url).
            headers:
                Request headers.
            json_data:
                JSON data for request body.
            **kwargs:
                Additional arguments.

        Returns:
            requests.Response:
                Response object.
        """
        url = f"{self.base_url}/{endpoint}" if not endpoint.startswith("http") else endpoint
        return self._make_request(
            method="POST",
            url=url,
            headers=headers,
            json_data=json_data,
            **kwargs,
        )

    def get_json(
        self,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Make GET request and return JSON response.

        Args:
            endpoint (str):
                API endpoint.
            headers:
                Request headers.
            params:
                Query parameters.
            **kwargs:
                Additional arguments.

        Returns:
            dict:
                JSON response.

        Raises:
            ApiRequestError:
                If request fails or response is not valid JSON.
        """
        response = self.get(
            endpoint=endpoint,
            headers=headers,
            params=params,
            **kwargs,
        )
        try:
            return response.json()
        except ValueError as e:
            raise ApiRequestError(
                f"Invalid JSON response: {e}",
                status_code=response.status_code,
                response_text=response.text,
            ) from e

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):
        """Context manager exit."""
        self.close()
