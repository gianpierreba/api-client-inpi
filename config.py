"""
Configuration module for the French Companies API Client.

This module handles all configuration including API endpoints,
credentials, and environment variables.
"""

import os
from typing import Optional


class Config:
    """Central configuration for all API clients."""

    # INPI API Configuration
    INPI_BASE_URL: str = "https://registre-national-entreprises.inpi.fr/api"
    INPI_USERNAME: Optional[str] = os.getenv("INPI_USER_PERSONAL")
    INPI_PASSWORD: Optional[str] = os.getenv("INPI_PASS_PERSONAL")

    # Request Configuration
    DEFAULT_TIMEOUT: int = 30  # seconds
    MAX_RETRIES: int = 3

    @classmethod
    def get_inpi_credentials(cls) -> tuple[str, str]:
        """
        Get INPI credentials from environment.

        Returns:
            tuple: (username, password)

        Raises:
            ValueError: If credentials are not available
        """
        if not cls.INPI_USERNAME or not cls.INPI_PASSWORD:
            raise ValueError(
                "INPI credentials not found."
                "Please set INPI_USERNAME and INPI_PASSWORD environment variables."
            )
        return cls.INPI_USERNAME, cls.INPI_PASSWORD

    @classmethod
    def validate_configuration(cls) -> dict:
        """
        Validate configuration and return status.

        Returns:
            dict: Configuration validation status
        """
        return {
            "inpi_credentials_configured": bool(cls.INPI_USERNAME and cls.INPI_PASSWORD),
        }
