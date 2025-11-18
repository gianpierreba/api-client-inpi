"""
INPI Actes (Documents) API client.

Accéder aux actes associés à une entreprise
Registre national des entreprises.
"""

from typing import Any, Dict, List, Optional, Tuple

from base.http_client import BaseHttpClient
from config import Config
from exceptions import ApiRequestError
from utils.validators import SirenSiretValidator

from .authenticator import InpiAuthenticator


class ActesClient:
    """Client for INPI actes (documents) API."""

    def __init__(
        self,
        username: str,
        password: str,
        siren: Optional[str] = None,
    ):
        """
        Initialize INPI Actes client.

        Args:
            username: INPI account username (email)
            password: INPI account password
            siren: SIREN code (9 digits)

        Raises:
            InvalidSirenError: If SIREN format is invalid
        """

        # Validate SIREN
        self.siren = SirenSiretValidator.validate_siren(
            siren=siren,
            allow_none=True,
        )

        # Initialize authenticator and HTTP client
        self.authenticator = InpiAuthenticator(
            username=username,
            password=password,
        )
        self.http_client = BaseHttpClient(
            base_url=Config.INPI_BASE_URL,
        )

        # Authenticate
        self.token = self.authenticator.authenticate()

    def _get_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        return self.authenticator.get_headers()

    def documents_associes_entreprise(self) -> Dict[str, Any]:
        """
        Get associated documents (actes, bilans) for a company.

        Recherche des documents associés à une entreprise :
            actes, bilans en PDF et bilans saisis au format JSON

        Returns:
            dict:
                Documents data.

        Raises:
            ApiRequestError:
                If request fails.
        """

        endpoint = f"companies/{self.siren}/attachments"

        return self.http_client.get_json(
            endpoint=endpoint,
            headers=self._get_headers(),
        )

    def acte_depot_id(self) -> List[Tuple[int, str, str, str]]:
        """
        Get position, date de dépôt, ID, and type for each acte.

        Position, date de dépôt, ID du document et type d'acte

        Returns:
            list:
                List of tuples (position, date_depot, id, type_rdd).
        """

        documents = self.documents_associes_entreprise()
        actes = documents.get(
            "actes",
            [],
        )

        return [
            (i, acte.get("dateDepot"), acte.get("id"), acte.get("typeRdd"))
            for i, acte in enumerate(actes)
        ]

    def actes_len(self) -> int:
        """
        Get count of actes available.

        Returns:
            int:
                Number of actes.
        """

        documents = self.documents_associes_entreprise()

        return len(documents.get("actes", []))

    def recherche_acte_pdf(
        self,
        id_acte: str,
    ) -> Dict[str, Any]:
        """
        Get acte PDF metadata by ID.

        Récupérer les métadonnées d'un acte via son identifiant.

        Args:
            id_acte ():
                Acte ID.

        Returns:
            dict:
                Acte metadata.
        """

        endpoint = f"actes/{id_acte}"

        return self.http_client.get_json(
            endpoint=endpoint,
            headers=self._get_headers(),
        )

    def telecharger_acte_pdf(
        self,
        id_acte: str,
        file_path: str,
        file_name: str,
    ) -> str:
        """
        Download acte PDF.

        Télécharger un acte PDF à partir de son identifiant.

        Args:
            id_acte (str):
                Acte ID.
            file_path (str):
                Directory path for saving.
            file_name (str):
                File name (without .pdf extension).

        Returns:
            str:
                Success or error message.
        """

        try:
            endpoint = f"actes/{id_acte}/download"
            response = self.http_client.get(
                endpoint=endpoint,
                headers=self._get_headers(),
            )

            if response.status_code == 200:
                full_path = f"{file_path}/{file_name}.pdf"
                with open(full_path, "wb") as output_file:
                    output_file.write(response.content)
                return "PDF attachment downloaded successfully"

            return f"Download failed with status code: {response.status_code}"
        except ApiRequestError as e:
            return f"An error occurred: {e}"

    def close(self):
        """Close HTTP client and authenticator sessions."""
        self.http_client.close()
        self.authenticator.close()

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
