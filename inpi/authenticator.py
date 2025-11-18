"""
INPI API authenticator.

This module handles authentication for the INPI API.
"""

from typing import Dict

import requests

from base.authenticator import BaseAuthenticator
from config import Config
from exceptions import AuthenticationError


class InpiAuthenticator(BaseAuthenticator):
    """Authenticator for INPI API."""

    def __init__(
        self,
        username: str,
        password: str,
    ):
        """
        Initialize INPI authenticator.

        Parameters:
            username (str):
                INPI account username.
            password (str):
                INPI account password.
        """
        super().__init__()
        self.username = username
        self.password = password
        self.base_url = Config.INPI_BASE_URL
        self.session = requests.Session()

    def authenticate(self) -> str:
        """
        Perform authentication with INPI API.

        Returns:
            str:
                Authentication token.

        Raises:
            AuthenticationError:
                If authentication fails.
        """

        auth_url = f"{self.base_url}/sso/login"
        credentials = {
            "username": self.username,
            "password": self.password,
        }

        try:
            response = self.session.post(
                url=auth_url,
                json=credentials,
                timeout=Config.DEFAULT_TIMEOUT,
            )
            response.raise_for_status()

            data = response.json()
            token = data.get("token")

            if not token:
                raise AuthenticationError(
                    "No token found in the authentication response.",
                )

            self.token = token
            return token

        except requests.exceptions.HTTPError as e:
            error_msg = f"Authentication failed with HTTP error: {e}"
            if e.response is not None:
                error_msg += f"\nResponse: {e.response.text}"
            raise AuthenticationError(error_msg) from e

        except requests.exceptions.RequestException as e:
            raise AuthenticationError(
                f"Authentication request failed: {e}",
            ) from e

        except (ValueError, KeyError) as e:
            raise AuthenticationError(
                f"Invalid authentication response format: {e}",
            ) from e

    def get_headers(self) -> Dict[str, str]:
        """
        Get headers with authentication token.

        Returns:
            dict:
                Headers with Bearer token.

        Raises:
            AuthenticationError:
                If not authenticated.
        """

        if not self.is_authenticated():
            self.authenticate()

        return {"Authorization": f"Bearer {self.token}"}

    def close(self):
        """Close the session."""
        self.session.close()

    def __enter__(self):
        """Context manager entry."""
        self.authenticate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
