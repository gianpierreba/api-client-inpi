"""
INPI Comptes Annuels (Financial Statements) API client.
INPI Financial Statements API client.

Accéder aux comptes annuels PDF et saisis associés à une entreprise.
Access the PDF and entered annual accounts associated with a company.
"""

import json
from typing import Any, Dict, List, Optional, Tuple

from base.http_client import BaseHttpClient
from config import Config
from exceptions import ApiRequestError
from utils.validators import SirenSiretValidator

from .authenticator import InpiAuthenticator


class ComptesAnnuelsClient:
    """Client for INPI comptes annuels (financial statements) API."""

    def __init__(
        self,
        username: str,
        password: str,
        siren: Optional[str] = None,
    ):
        """
        Initialize INPI Comptes Annuels client.

        Parameters:
            username (str):
                INPI account username.
            password (str):
                INPI account password.
            siren:
                SIREN code (9 digits).

        Raises:
            InvalidSirenError:
                If SIREN format is invalid.
        """

        # Validate SIREN
        self.siren = SirenSiretValidator.validate_siren(
            siren,
            allow_none=True,
        )

        # Initialize authenticator and HTTP client
        self.authenticator = InpiAuthenticator(
            username,
            password,
        )
        self.http_client = BaseHttpClient(
            Config.INPI_BASE_URL,
        )

        # Authenticate and fetch data if SIREN is provided
        self.token = self.authenticator.authenticate()
        self.documents_associes_entreprise: Optional[Dict[str, Any]] = None
        if self.siren:
            try:
                self.documents_associes_entreprise = self._fetch_attachments()
                if self.documents_associes_entreprise is None:
                    raise ValueError("API returned None for financial statements")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to fetch financial statement data for {self.siren}: {e}"
                ) from e

    def _get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            dict: Headers with authentication token
        """

        return self.authenticator.get_headers()

    def _fetch_attachments(self) -> Dict[str, Any]:
        """
        Fetch attachments (documents) from INPI API.

        Returns:
            dict: Attachments data including bilans

        Raises:
            ApiRequestError: If request fails
        """

        endpoint = f"companies/{self.siren}/attachments"

        return self.http_client.get_json(
            endpoint=endpoint,
            headers=self._get_headers(),
        )

    def full_json_outcome(self) -> Dict[str, Any]:
        """
        Get full JSON output.

        Returns:
            dict: Full JSON response from INPI API
        """

        return self.documents_associes_entreprise

    # PDF Bilans Methods

    def bilans_pdf_detail(
        self,
        position: Optional[int] = None,
    ) -> list | dict:
        """
        Get detailed PDF bilan(s).

        La totalité des bilans disponibles en PDF detaillé

        Args:
            position: Position in bilans array, or None for all

        Returns:
            dict or list: Bilan details
        """

        if position is None:
            return self.documents_associes_entreprise.get(
                "bilans",
                [],
            )

        return self.documents_associes_entreprise.get(
            "bilans",
            [],
        )[position]

    def bilans_pdf_len(self) -> int:
        """
        Get count of PDF bilans available.

        Returns:
            int: Number of PDF bilans
        """

        return len(
            self.documents_associes_entreprise.get(
                "bilans",
                [],
            )
        )

    def bilans_pdf_cloture_id(
        self,
        as_json: bool = True,
    ) -> str | list:
        """
        Get position, date de clôture, and document ID for each PDF bilan.

        Position, date de clôture and document ID

        Parameters:
            as_json (bool, optional):
                Whether to format as JSON string. Default to True.

        Returns:
            str|list:
                Formatted JSON sting if `as_json` is True or list of tuples,
                otherwise a list (position, date_cloture, document_id).
        """

        bilans = self.documents_associes_entreprise.get(
            "bilans",
            [],
        )
        output = [(i, bilan.get("dateCloture"), bilan.get("id")) for i, bilan in enumerate(bilans)]

        if as_json:
            return json.dumps(
                output,
                indent=4,
                ensure_ascii=False,
            )

        return output

    def recherche_bilans_pdf(
        self,
        id_bilan: str,
    ) -> dict:
        """
        Get PDF bilan metadata by ID.

        Récupérer les métadonnées d'un bilan via son identifiant.

        Parameters:
            id_bilan: Bilan ID

        Returns:
            dict: Bilan metadata
        """

        endpoint = f"bilans/{id_bilan}"

        return self.http_client.get_json(
            endpoint=endpoint,
            headers=self._get_headers(),
        )

    def telecharger_bilan_pdf(
        self,
        id_bilan: str,
        file_path: str,
        file_name: str,
    ) -> str:
        """
        Download PDF bilan.

        Télécharger un bilan PDF à partir de son identifiant.

        Parameters:
            id_bilan (str): Bilan ID.
            file_path (str): Directory path for saving.
            file_name (str): File name (without .pdf extension).

        Returns:
            str:
                Success or error message
        """

        try:
            endpoint = f"bilans/{id_bilan}/download"
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

    # Bilans Saisis (JSON) Methods

    def bilans_saisis_len(self) -> int:
        """
        Get count of 'bilans saisis' available.

        Returns:
            int:
                Number of 'bilans saisis'
        """

        return len(
            self.documents_associes_entreprise.get(
                "bilansSaisis",
                [],
            )
        )

    def bilans_saisis_detail(
        self,
        position: Optional[int] = None,
    ) -> list | dict:
        """
        Get detailed bilans saisis (JSON format).

        La totalité des bilans saisis detaillés disponibles.

        Parameters:
            position (int):
                Position in bilans array or None for all.

        Returns:
            list|dict:
                Bilan saisi details.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position is None:
            return bilans

        return bilans[position] if position < len(bilans) else None

    def bilans_saisis_cloture_id(self) -> List[Tuple[int, str, str]]:
        """
        Get position, date de clôture, and ID for each bilan saisi.

        Position, date de clôture et ID

        Returns:
            list:
                List of tuples (position, date_cloture, id)
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        return [(i, bilan.get("dateCloture"), bilan.get("id")) for i, bilan in enumerate(bilans)]

    def recherche_bilans_saisis(
        self,
        id_bilan: str,
    ) -> Dict[str, Any]:
        """
        Get bilan saisi data by ID.

        Récupérer les données d'un bilan-saisis via son identifiant.

        Parameters:
            id_bilan: Bilan saisi ID

        Returns:
            dict:
                Bilan saisi data
        """

        endpoint = f"bilans-saisis/{id_bilan}"

        return self.http_client.get_json(
            endpoint,
            headers=self._get_headers(),
        )

    def type_bilan_saisi(
        self,
        id_bilan: Optional[str] = None,
        position: Optional[int] = None,
    ) -> Optional[str]:
        """
        Get type of 'bilan saisi' (C, S, K, B, A).

        Type de 'bilan saisi'.

        Parameters:
            id_bilan (str, optional):
                Bilan ID (if provided, fetches from API). Defaults to None.
            position (int, optional):
                Position in array (if id_bilan not provided). Defaults to None.

        Returns:
            str|None:
                Bilan type (C, S, K, B or A) or None if not found.
        """

        if id_bilan is not None:
            output = self.recherche_bilans_saisis(
                id_bilan=id_bilan,
            )
            return output.get("typeBilan")

        if position is not None:
            bilans = self.documents_associes_entreprise.get(
                "bilansSaisis",
                [],
            )
            if position < len(bilans):
                return bilans[position].get("typeBilan")

        return None

    # Metadata Methods

    def version_metadata(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get metadata version.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Metadata version.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get("bilanSaisi", {}).get("version")

        return None

    def adresse_metadata(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get metadata address.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Metadata address.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "adresse",
            )

        return None

    def info_traitement(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'traitement' info metadata.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'traitement' info metadata.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "infoTraitement",
            )

        return None

    def code_confidentialite(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get confidentiality code.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Confidentiality code.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "codeConfidentialite",
            )

        return None

    def code_saisie(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'saisie' code.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'saisie' code.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "codeSaisie",
            )

        return None

    def code_origine_devise(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'devise' origin code.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'devise' origin code.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "codeOrigineDevise",
            )

        return None

    def code_devise(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'devise' code.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'devise' code.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "codeDevise",
            )

        return None

    def code_type_bilan(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get type bilan code.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                bilan code.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "codeTypeBilan",
            )

        return None

    def num_gestion(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get gestion number.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Gestion number.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "numGestion",
            )

        return None

    def num_depot(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'depot' number.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'depot' number.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "numDepot",
            )

        return None

    def code_greffe(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'greffe' code.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'greffe' number.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "codeGreffe",
            )

        return None

    def duree_exercice_n_moins_1(
        self,
        position: int,
    ) -> Optional[int]:
        """
        Get exercise duration N-1.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Exercise duration N-1.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "dureeExerciceNMoins1",
            )

        return None

    def date_cloture_exercice_n_moins_1(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get exercise closing date N-1.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Closing date N-1.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "dateClotureExerciceNMoins1",
            )

        return None

    def duree_exercice_n(
        self,
        position: int,
    ) -> Optional[int]:
        """
        Get exercise duration N.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Exercise duration N.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "dureeExerciceN",
            )

        return None

    def date_cloture_exercice(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get exercise closing date.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Exercise closing date.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            bilan_saisi = bilans[position].get(
                "bilanSaisi",
                {},
            )
            bilan = bilan_saisi.get(
                "bilan",
                {},
            )
            identite = bilan.get(
                "identite",
                {},
            )
            return identite.get(
                "dateClotureExercice",
            )

        return None

    def confidentiality(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get confidentiality status.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Confidentiality status.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get(
                "confidentiality",
            )

        return None

    def num_chrono(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'chrono' number.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'chrono' number.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get(
                "numChrono",
            )

        return None

    def date_depot(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get 'depot' date.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                'depot' date.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get(
                "dateDepot",
            )

        return None

    def id_bilan_saisi(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get bilan 'saisi' ID.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                bilan 'saisi' ID.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get(
                "id",
            )

        return None

    def updated_at(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get update timestamp.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                update timestamp.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get(
                "updatedAt",
            )

        return None

    def date_cloture(
        self,
        position: int,
    ) -> Optional[str]:
        """
        Get closing date.

        Parameters:
            position (int):
                Position in array.

        Returns:
            str|None:
                Closing date.
        """

        bilans = self.documents_associes_entreprise.get(
            "bilansSaisis",
            [],
        )

        if position < len(bilans):
            return bilans[position].get(
                "dateCloture",
            )

        return None

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
