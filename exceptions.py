"""
Custom exceptions for the French Companies API Client.

This module defines all custom exceptions used throughout the API client.
"""


class ApiClientError(Exception):
    """Base exception for all API client errors."""


class AuthenticationError(ApiClientError):
    """Raised when authentication fails."""


class ValidationError(ApiClientError):
    """Raised when input validation fails."""


class DataNotFoundError(ApiClientError):
    """Raised when expected data is not found in API response."""


class ApiRequestError(ApiClientError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        status_code: int = None,
        response_text: str = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_text = response_text


class InvalidSirenError(ValidationError):
    """Raised when SIREN format is invalid."""


class InvalidSiretError(ValidationError):
    """Raised when SIRET format is invalid."""
