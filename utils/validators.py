"""
Validation utilities for SIREN and SIRET codes.

This module provides validation functions for French company identifiers.
"""

from typing import Optional

from exceptions import InvalidSirenError, InvalidSiretError


class SirenSiretValidator:
    """Validator for SIREN and SIRET codes."""

    @staticmethod
    def validate_siren(
        siren: Optional[str],
        allow_none: bool = False,
    ) -> str:
        """
        Validate SIREN format.

        Args:
            siren:
                SIREN code to validate (9 digits).
            allow_none:
                Whether to allow None values.

        Returns:
            str:
                Validated SIREN code.

        Raises:
            InvalidSirenError:
                If SIREN format is invalid.
        """
        if siren is None:
            if allow_none:
                return None
            raise InvalidSirenError("SIREN cannot be None")

        if not isinstance(siren, str):
            siren = str(siren)

        # Remove spaces and common separators
        siren = siren.replace(" ", "").replace("-", "").replace(".", "")

        if len(siren) != 9:
            raise InvalidSirenError(
                f"SIREN must have exactly 9 digits. Provided value has {len(siren)} digits: {siren}"
            )

        if not siren.isdigit():
            raise InvalidSirenError(f"SIREN must contain only digits. Provided value: {siren}")

        return siren

    @staticmethod
    def validate_siret(
        siret: Optional[str],
        allow_none: bool = False,
    ) -> str:
        """
        Validate SIRET format.

        Args:
            siret:
                SIRET code to validate (14 digits).
            allow_none:
                Whether to allow None values.

        Returns:
            str:
                Validated SIRET code.

        Raises:
            InvalidSiretError:
                If SIRET format is invalid.
        """
        if siret is None:
            if allow_none:
                return None
            raise InvalidSiretError("SIRET cannot be None")

        if not isinstance(siret, str):
            siret = str(siret)

        # Remove spaces and common separators
        siret = siret.replace(" ", "").replace("-", "").replace(".", "")

        if len(siret) != 14:
            raise InvalidSiretError(
                f"SIRET must have exactly 14 digits. "
                f"Provided value has {len(siret)} digits: {siret}"
            )

        if not siret.isdigit():
            raise InvalidSiretError(f"SIRET must contain only digits. Provided value: {siret}")

        return siret

    @staticmethod
    def extract_siren_from_siret(
        siret: str,
    ) -> str:
        """
        Extract SIREN (first 9 digits) from SIRET.

        Args:
            siret:
                SIRET code (14 digits).

        Returns:
            str:
                SIREN code (9 digits).

        Raises:
            InvalidSiretError:
                If SIRET format is invalid.
        """
        validated_siret = SirenSiretValidator.validate_siret(siret)
        return validated_siret[:9]

    @staticmethod
    def is_valid_siren(
        siren: str,
    ) -> bool:
        """
        Check if SIREN is valid without raising exception.

        Args:
            siren:
                SIREN code to check.

        Returns:
            bool:
                True if valid, False otherwise.
        """
        try:
            SirenSiretValidator.validate_siren(siren)
            return True
        except InvalidSirenError:
            return False

    @staticmethod
    def is_valid_siret(
        siret: str,
    ) -> bool:
        """
        Check if SIRET is valid without raising exception.

        Args:
            siret:
                SIRET code to check.

        Returns:
            bool:
                True if valid, False otherwise.
        """
        try:
            SirenSiretValidator.validate_siret(siret)
            return True
        except InvalidSiretError:
            return False
