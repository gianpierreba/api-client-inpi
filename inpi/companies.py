"""
INPI Companies API client.

This module provides access to company information and dirigeants data from INPI.

Classes:
- InpiCompaniesClient: Client for INPI companies API.

Examples:
    Basic usage:
    >>> from apis.inpi import InpiCompaniesClient
    >>> client = InpiCompaniesClient(
    ...     username="your_username",
    ...     password="your_password",
    ...     siren="123456789",
    ... )
    >>> try:
    >>>     company_name = client.nom_societe()
    >>>     print(company_name)
    >>> finally
    >>>     client.close()

    Dirigeants example:
    >>> from apis.inpi import InpiCompaniesClient
    >>> client = InpiCompaniesClient(
    ...     username="your_username",
    ...     password="your_password",
    ...     siren="123456789",
    ... )
    >>> try:
    >>>     individus = client.nombre_individus()
    >>>     for idx in individus:
    ...         nom_dirigeant = client.nom_dirigeant(idx)
    ...         prenom_dirigeant = client.prenom_dirigeant(idx)
    ...         role = client.role_dirigeant(idx)
    ...         print(f"Director: {prenom_dirigeant} {nom_dirigeant} - {role_dirigeant}")
    >>> finally:
    >>>     client.close()

    Read README for more examples.
"""

from typing import Any, Dict, List, Optional

from base.http_client import BaseHttpClient
from config import Config
from utils.validators import SirenSiretValidator

from .authenticator import InpiAuthenticator


class InpiCompaniesClient:
    """Client for INPI companies API."""

    def __init__(
        self,
        username: str,
        password: str,
        siren: Optional[str] = None,
        siret: Optional[str] = None,
    ):
        """
        Initialize INPI Companies client.

        Args:
            username: INPI account username (email)
            password: INPI account password
            siren: SIREN code (9 digits)
            siret: SIRET code (14 digits)

        Raises:
            InvalidSirenError: If SIREN format is invalid
            InvalidSiretError: If SIRET format is invalid
        """

        # Validate and store identifiers
        self.siren = SirenSiretValidator.validate_siren(
            siren=siren,
            allow_none=True,
        )
        self.siret = SirenSiretValidator.validate_siret(
            siret=siret,
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

        # Authenticate and fetch data if SIREN is provided
        self.token = self.authenticator.authenticate()
        self.output: Optional[Dict[str, Any]] = None
        if self.siren:
            try:
                self.output = self._fetch_company_data()
                if self.output is None:
                    raise ValueError("API returned None for company data")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to fetch company data for SIREN {self.siren}: {e}."
                ) from e

    def _get_headers(self) -> Dict[str, str]:
        """
        Get authentication headers.

        Returns:
            dict: Headers with authentication token
        """

        return self.authenticator.get_headers()

    def _fetch_company_data(self) -> Dict[str, Any]:
        """
        Fetch company data from INPI API.

        Returns:
            dict: Company data

        Raises:
            ApiRequestError: If request fails
        """

        endpoint = f"companies/{self.siren}"
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

        return self.output

    def _get_nested_value(
        self,
        *keys,
        default=None,
    ):
        """
        Safely get nested value from output dictionary.

        Args:
            *keys: Keys to navigate nested dictionary
            default: Default value if key not found

        Returns:
            Value at the nested key or default

        Raises:
            RuntimeError: If self.output is None (data not fetched)
        """
        if self.output is None:
            raise RuntimeError(
                "Company data not available. "
                "This usually means the API request failed during initialization. "
                "Please check your SIREN and credentials."
            )

        current = self.output
        for key in keys:
            if current is None:
                return default

            # Handle dictionary access
            if isinstance(current, dict):
                current = current.get(key)

            # Handle list/array access with integer index
            elif isinstance(current, list):
                if isinstance(key, int):
                    try:
                        current = current[key]
                    except (IndexError, KeyError):
                        return default
                else:
                    # key is not an integer but current is a list
                    return default
            else:
                return default

        return current if current is not None else default

    # Company Information Methods

    def nature_cessation(self) -> Optional[str]:
        """
        Get nature de cessation.

        Nature de cessation.

        Cette valeur est obligatoire si c'est une formalité de cessation.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "natureCessation",
        )

    def date_cessation_entreprise(self) -> Optional[str]:
        """
        Get date de cessation.

        Date de cessation.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "detailCessationEntreprise",
            "dateRadiation",
        )

    def date_effet_cessation_entreprise(self) -> Optional[str]:
        """
        Get date effet de cessation.

        Date effet de cessation.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "detailCessationEntreprise",
            "dateEffet",
        )

    def description_detaillee(self) -> Optional[str]:
        """
        Get detailed description of the company.

        Description detaillée de la société.

        Returns:
            str: Company description or None
        """

        # Try from 'identite'
        description = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "identite",
            "description",
            "objet",
        )
        if description:
            return description.strip()

        # Try from 'etablissementPrincipal'
        description = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "activites",
            0,
            "descriptionDetaillee",
        )
        if description:
            return description.strip()

        # Try from 'autresEtablissements'
        description = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "autresEtablissements",
            0,
            "activites",
            0,
            "descriptionDetaillee",
        )
        if description:
            return description.strip()

        return None

    def montant_capital(self) -> Optional[int]:
        """
        Get company capital amount.

        Capital de la société.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "identite",
            "description",
            "montantCapital",
        )

    def nom_societe(self) -> Optional[str]:
        """
        Get company name.

        Nom de la société.
        """

        # Try personneMorale
        nom = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "identite",
            "entreprise",
            "denomination",
        )
        if nom:
            return nom

        # Try exploitation
        nom = self._get_nested_value(
            "formality",
            "content",
            "exploitation",
            "identite",
            "entreprise",
            "denomination",
        )
        if nom:
            return nom

        # Try personnePhysique
        return self._get_nested_value(
            "formality",
            "content",
            "personnePhysique",
            "identite",
            "entreprise",
            "denomination",
        )

    def forme_juridique(self) -> Optional[str]:
        """
        Get legal form.

        Forme juridique de la société.
        """

        # Try from formeJuridique
        forme = self._get_nested_value(
            "formality",
            "formeJuridique",
        )
        if forme:
            return forme

        # Try from natureCreation
        forme = self._get_nested_value(
            "formality",
            "content",
            "natureCreation",
            "formeJuridique",
        )
        if forme:
            return forme

        # Try from personneMorale
        forme = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "identite",
            "entreprise",
            "formeJuridique",
        )
        if forme:
            return forme

        # Try from personnePhysique
        return self._get_nested_value(
            "formality",
            "content",
            "personnePhysique",
            "identite",
            "entreprise",
            "formeJuridique",
        )

    def code_ape(self) -> Optional[str]:
        """
        Get APE code.

        Code APE.
        """

        # Try personneMorale
        code = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "identite",
            "entreprise",
            "codeApe",
        )
        if code:
            return code

        # Try exploitation
        return self._get_nested_value(
            "formality",
            "content",
            "exploitation",
            "identite",
            "entreprise",
            "codeApe",
        )

    def nom_commercial(self) -> Optional[str]:
        """
        Get commercial name.

        Nom Commercial.
        """

        # Try from etablissementPrincipal
        nom_commercial = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "descriptionEtablissement",
            "nomCommercial",
        )
        if nom_commercial:
            return nom_commercial

        # Try from identite
        nom_commercial = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "identite",
            "entreprise",
            "nomCommercial",
        )
        if nom_commercial:
            return nom_commercial

        # Try from autresEtablissements
        autres = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "autresEtablissements",
        )
        if autres and isinstance(autres, list):
            noms_commerciaux = [
                etab.get("descriptionEtablissement", {}).get("nomCommercial")
                for etab in autres
                if etab.get("descriptionEtablissement", {}).get("nomCommercial")
            ]
            if noms_commerciaux:
                return ", ".join(noms_commerciaux)

        return None

    def siret_siege(self) -> Optional[str]:
        """
        Get SIRET of headquarters.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "descriptionEtablissement",
            "siret",
        )

    def code_postal(self) -> Optional[str]:
        """
        Get postal code.

        Code postal où se localise la société.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "adresse",
            "codePostal",
        )

    def ville(self) -> Optional[str]:
        """
        Get city.

        Ville où se localise la société.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "adresse",
            "commune",
        )

    def pays(self) -> Optional[str]:
        """
        Get country.

        Pays où se localise la société.
        """

        # Try etablissementPrincipal in personneMorale
        pays = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "adresse",
            "pays",
        )
        if pays:
            return pays

        # Try exploitation
        pays = self._get_nested_value(
            "formality",
            "content",
            "exploitation",
            "etablissementPrincipal",
            "adresse",
            "pays",
        )
        if pays:
            return pays

        # Try adresseEntreprise
        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "adresseEntreprise",
            "adresse",
            "pays",
        )

    def code_pays(self) -> Optional[str]:
        """
        Get country code.

        Code pays où se localise la société.
        """

        # Try etablissementPrincipal in personneMorale
        code = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "etablissementPrincipal",
            "adresse",
            "codePays",
        )
        if code:
            return code

        # Try exploitation
        code = self._get_nested_value(
            "formality",
            "content",
            "exploitation",
            "etablissementPrincipal",
            "adresse",
            "codePays",
        )
        if code:
            return code

        # Try adresseEntreprise
        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "adresseEntreprise",
            "adresse",
            "codePays",
        )

    def numero_voie(self) -> str:
        """
        Get street address.

        Ville où se localise la société

        Exemple:
            "complementLocalisation": "ZI",
            "numVoie": "207",
            "typeVoie": "IMP",
            "voie": "DES QUATRE VENTS".
        """

        base = (
            self._get_nested_value(
                "formality",
                "content",
                "personneMorale",
                "etablissementPrincipal",
                "adresse",
            )
            or {}
        )

        parts = []

        complement = base.get(
            "complementLocalisation",
            "",
        )
        if complement:
            parts.append(complement)

        num_voie = base.get(
            "numVoie",
            "",
        )
        type_voie = base.get(
            "typeVoie",
            "",
        )
        voie = base.get(
            "voie",
            "",
        )
        if any([num_voie, type_voie, voie]):
            parts.append(f"{num_voie} {type_voie} {voie}".strip())

        dist_speciale = base.get(
            "distributionSpeciale",
            "",
        )
        if dist_speciale:
            parts.append(
                object=dist_speciale,
            )

        return "\n".join(parts).strip()

    # Dirigeants Methods

    def dirigeants_box(self) -> List[Dict[str, Any]]:
        """
        Get list of dirigeants.

        Number of dirigeants.

        Raises:
            RuntimeError: If self.output is None (data not fetched)
        """
        if self.output is None:
            raise RuntimeError("Company data not available. Cannot access dirigeants information.")

        return (
            self._get_nested_value(
                "formality",
                "content",
                "personneMorale",
                "composition",
                "pouvoirs",
            )
            or []
        )

    def nombre_individus(self) -> List[int]:
        """
        Get list of indices for individual dirigeants.

        Check the len position of the Dirigeants dictionary.
        """

        pouvoirs = self.dirigeants_box()

        return [
            index
            for index, individu in enumerate(pouvoirs)
            if individu.get("typeDePersonne") == "INDIVIDU"
        ]

    def nombre_entreprises(self) -> List[int]:
        """
        Get list of indices for company dirigeants.

        Check the len position of the Dirigeants dictionary.
        """

        pouvoirs = self.dirigeants_box()

        return [
            index
            for index, individu in enumerate(pouvoirs)
            if individu.get("typeDePersonne") == "ENTREPRISE"
        ]

    def nom_entreprise(self, entreprise: int) -> Optional[str]:
        """
        Get company name (for company dirigeants).

        Nom de l'entreprise.

        Arg:
            entreprise: Index of the company dirigeant.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            entreprise,
            "entreprise",
            "denomination",
        )

    def siren_entreprise(
        self,
        entreprise: int,
    ) -> Optional[str]:
        """
        Get SIREN (for company dirigeants).

        Numéro SIREN de l'entreprise.

        Arg:
            entreprise: Index of the company dirigeant.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            entreprise,
            "entreprise",
            "siren",
        )

    def role_entreprise(
        self,
        entreprise: int,
    ) -> Optional[str]:
        """
        Get role (for company dirigeants).

        Role de l'entreprise.

        Arg:
            entreprise: Index of the company dirigeant.
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            entreprise,
            "entreprise",
            "roleEntreprise",
        )

    def type_personne(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get person type.

        Type de personne.

        Arg:
            dirigeant: Dirigeant index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "typeDePersonne",
        )

    def nom_dirigeant(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get dirigeant last name.

        Nom du dirigeant.

        Arg:
            dirigeant: Dirigeant index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "nom",
        )

    def prenom_dirigeant(
        self,
        dirigeant: int,
        first_prenom: bool = False,
        output_list: bool = False,
    ) -> Optional[str | List[str]]:
        """
        Get dirigeant first name(s).

        Prénom du dirigeant.

        Args:
            dirigeant: Dirigeant index
            first_prenom: Return only first name
            output_list: Return as list

        Returns:
            str or list: First name(s) or None
        """
        prenoms = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "prenoms",
        )

        if prenoms is None:
            return None

        if output_list:
            return prenoms

        if first_prenom:
            return prenoms[0] if prenoms else None

        if len(prenoms) == 0:
            return "Pas de prénom"
        if len(prenoms) == 1:
            return prenoms[0]
        return " ".join(prenoms)

    def birth_date_dirigeant(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get dirigeant birth date.

        Date de naissance du dirigeant.

        Arg:
            dirigeant: Dirigeant index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "dateDeNaissance",
        )

    def nationalite_dirigeant(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get dirigeant nationality.

        Nationalité du dirigeant.

        Arg:
            dirigeant: Dirigeant index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "nationalite",
        )

    def situation_matrimoniale(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get dirigeant marital status.

        Situation matrimoniale du dirigeant.

        Arg:
            dirigeant: Dirigeant index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "situationMatrimoniale",
        )

    def role_dirigeant(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get dirigeant role code.

        Le rôle du dirigeant dans la société / Poste.

        Arg:
            dirigeant: Dirigeant index
        """

        # Try from descriptionPersonne
        role = self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "role",
        )
        if role:
            return role

        # Try from roleEntreprise
        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "roleEntreprise",
        )

    def second_role_dirigeant(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get second dirigeant role code.

        Le deuxième rôle du dirigeant dans la société / Poste.

        Arg:
            dirigeant: Dirigeant index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "secondRoleEntreprise",
        )

    def dirigeant_actif(
        self,
        index: int,
    ) -> bool:
        """
        Return if dirigeant is active.

        Retour si dirigeant est actif.

        Arg:
            index: dirigeant or entreprise index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            index,
            "actif",
        )

    def demission_ordre(
        self,
        index: int,
    ) -> bool:
        """
        Return a dirigeant's resignation.

        Retour démission pour ordre de dirigeant.

        Arg:
            index: dirigeant or entreprise index
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            index,
            "mentionDemissionOrdre",
        )

    def genre_dirigeant(
        self,
        dirigeant: int,
    ) -> Optional[str]:
        """
        Get dirigeant gender.

        Genre du dirigeant.

        Arg:
            dirigeant: Dirigeant index

        Example:
            'M' for male and 'F' for female
        """

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "descriptionPersonne",
            "genre",
        )

    def adresse_domicile_dirigeant(
        self,
        dirigeant: int,
        field: str,
    ) -> Optional[str]:
        """
        Get dirigeant home address field.

        Domicile du dirigeant.

        Args:
            dirigeant: Dirigeant index
            field: Field name ('pays', 'codePostal', 'codePays' or 'commune')

        Returns:
            str: Address field value or None

        Raises:
            ValueError: If invalid field name
        """

        valid_fields = [
            "pays",
            "codePostal",
            "commune",
            "codePays",
        ]

        if field not in valid_fields:
            raise ValueError(f"Invalid field '{field}'. Must be one of: {valid_fields}")

        return self._get_nested_value(
            "formality",
            "content",
            "personneMorale",
            "composition",
            "pouvoirs",
            dirigeant,
            "individu",
            "adresseDomicile",
            field,
        )

    def close(self):
        """
        Close HTTP client and authenticator sessions.
        """

        self.http_client.close()
        self.authenticator.close()

    def __enter__(self):
        """
        Context manager entry.
        """

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):
        """
        Context manager exit.
        """

        self.close()
