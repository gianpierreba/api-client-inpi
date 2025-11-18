"""
Base authenticator for API clients.

This module provides base authentication functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional


class BaseAuthenticator(ABC):
    """Base class for API authenticators."""

    def __init__(self):
        """Initialize authenticator."""
        self.token: Optional[str] = None

    @abstractmethod
    def authenticate(self) -> str:
        """
        Perform authentication and return token.

        Returns:
            str:
                Authentication token.

        Raises:
            AuthenticationError:
                If authentication fails
        """

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            dict:
                Headers with authentication token.

        Raises:
            AuthenticationError:
                If not authenticated.
        """

    def is_authenticated(self) -> bool:
        """
        Check if authenticated.

        Returns:
            bool: True if authenticated, False otherwise
        """
        return self.token is not None

    def clear_authentication(self):
        """Clear authentication token."""
        self.token = None
