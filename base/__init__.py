"""
Base classes for API clients.
"""

from .authenticator import BaseAuthenticator
from .http_client import BaseHttpClient

__all__ = ["BaseHttpClient", "BaseAuthenticator"]
