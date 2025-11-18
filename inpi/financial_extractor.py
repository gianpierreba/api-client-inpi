"""
Financial data extractor for INPI bilans saisis.

This module provides a centralized way to extract financial metrics from
complex JSON structures, eliminating the 100+ duplicated methods.
"""

from enum import Enum
from typing import Any, Dict, List, Optional


class FinancialMetricType(Enum):
    """Types of financial metrics."""

    CAPITAUX_PROPRES = "capitaux_propres"
    BENEFICE_PERTE = "benefice_perte"
    RESULTAT_EXERCICE = "resultat_exercice"
    CHIFFRE_AFFAIRES = "chiffre_affaires"
    EFFECTIF = "effectif"


class BilanType(Enum):
    """Types of bilans (financial statements)."""

    # 'Type Bilan' from Version 5 - Juin 2025
    TBC = "C"  # Type Bilan "C": Postes associés aux comptes annuels complets
    TBS = "S"  # Type Bilan "S": Postes associés aux comptes annuels simplifiés
    TBK = "K"  # Type Bilan "K": Postes associés aux comptes consolidés
    TBB = "B"  # Type Bilan "B": Postes associés aux comptes annuels de banques
    TBAC = "AC"  # Type Bilan "AC": Postes associés aux comptes annuels de type agricole complets
    TBAS = "AS"  # Type Bilan "AS": Postes bilans de type agricole simplifiés


class FinancialCodeMapping:
    """Mapping of financial codes to extract from bilans."""

    ######################
    # CHIFFRE D'AFFAIRES #
    ######################

    # Chiffre d'affaires (Turnover) mappings

    CHIFFRE_AFFAIRES = {
        BilanType.TBC: {"field": "m3", "code": "FJ"},
        BilanType.TBK: {"field": "m3", "code": "FJ"},
    }

    CHIFFRE_AFFAIRES_N_1 = {
        BilanType.TBC: {"field": "m4", "code": "FJ"},
        BilanType.TBK: {"field": "m4", "code": "FJ"},
    }

    # For TBS, 'chiffre d'affaires' is calculated from multiple components:
    # Ventes de marchandises - France et Export
    # Production vendue de biens - France et Export
    # Production vendue de services - France et Export
    CHIFFRE_AFFAIRES_TBS = {
        "ventes_marchandises_export": {"field": "m1", "code": "209"},
        "production_biens_export": {"field": "m1", "code": "215"},
        "production_services_export": {"field": "m1", "code": "217"},
        "ventes_marchandises_france": {"field": "m1", "code": "210"},
        "production_biens_france": {"field": "m1", "code": "214"},
        "production_services_france": {"field": "m1", "code": "218"},
    }

    CHIFFRE_AFFAIRES_N_1_TBS = {
        "ventes_marchandises": {"field": "m2", "code": "210"},
        "production_biens": {"field": "m2", "code": "214"},
        "production_services": {"field": "m2", "code": "218"},
    }

    ####################
    # CAPITAUX PROPRES #
    ####################

    # Capitaux propres (Equity) mappings

    CAPITAUX_PROPRES = {
        BilanType.TBC: {"field": "m1", "code": "DL"},
        BilanType.TBS: {"field": "m3", "code": "142"},
        BilanType.TBK: {"field": "m1", "code": "DL"},
    }

    CAPITAUX_PROPRES_N_1 = {
        BilanType.TBC: {"field": "m2", "code": "DL"},
        BilanType.TBS: {"field": "m4", "code": "142"},
        BilanType.TBK: {"field": "m2", "code": "DL"},
    }

    # For TBB, 'capitaux propres' is calculated from multiple components
    CAPITAUX_PROPRES_TBB = {
        "capital_souscrit": {"field": "m1", "code": "P3"},
        "primes_emission": {"field": "m1", "code": "P4"},
        "reserves": {"field": "m1", "code": "P5"},
        "ecarts_reevaluation": {"field": "m1", "code": "P6"},
        "report_nouveau": {"field": "m1", "code": "P7"},
        "resultat_exercice": {"field": "m1", "code": "P8"},
    }

    CAPITAUX_PROPRES_N_1_TBB = {
        "capital_souscrit": {"field": "m2", "code": "P3"},
        "primes_emission": {"field": "m2", "code": "P4"},
        "reserves": {"field": "m2", "code": "P5"},
        "ecarts_reevaluation": {"field": "m2", "code": "P6"},
        "report_nouveau": {"field": "m2", "code": "P7"},
        "resultat_exercice": {"field": "m2", "code": "P8"},
    }

    ####################
    # BÉNÉFICE / PERTE #
    ####################

    # Bénéfice/Perte (Profit/Loss) mappings

    BENEFICE_PERTE = {
        BilanType.TBK: {"field": "m1", "code": "R6"},
        BilanType.TBS: [
            # 'Bénéfice/Perte' from 'Compte de Résultat'
            {"field": "m1", "code": "310"},
            # 'Bénéfice/Perte' from 'Bilan - Passif'
            {"field": "m3", "code": "136"},  # Fallback
        ],
        BilanType.TBC: [
            # 'Bénéfice/Perte' from 'Compte de Résultat'
            {"field": "m1", "code": "HN"},
            # 'Bénéfice/Perte' from 'Bilan - Passif'
            {"field": "m1", "code": "DI"},  # Fallback
        ],
    }

    BENEFICE_PERTE_N_1 = {
        BilanType.TBK: {"field": "m2", "code": "R6"},
        BilanType.TBS: [
            # 'Bénéfice/Perte' from 'Compte de Résultat'
            {"field": "m2", "code": "310"},
            # 'Bénéfice/Perte' from 'Bilan - Passif'
            {"field": "m4", "code": "136"},  # Fallback
        ],
        BilanType.TBC: [
            # 'Bénéfice/Perte' from 'Compte de Résultat'
            {"field": "m2", "code": "HN"},
            # 'Bénéfice/Perte' from 'Bilan - Passif'
            {"field": "m2", "code": "DI"},  # Fallback
        ],
    }

    # For TBB, 'résultat de l'exercice' (Net profit) ou bénéfice/perte mappings
    RESULTAT_EXERCICE_TBB = [
        # 'Résultat de l'exercice' from 'Compte de Résultat'
        {"field": "m1", "code": "R3"},
        # 'Résultat de l'exercice' from 'Bilan - Passif'
        {"field": "m1", "code": "P8"},  # Fallback
    ]

    RESULTAT_EXERCICE_N_1_TBB = [
        # 'Résultat de l'exercice' from 'Compte de Résultat'
        {"field": "m2", "code": "R3"},
        # 'Résultat de l'exercice' from 'Bilan - Passif'
        {"field": "m2", "code": "P8"},  # Fallback
    ]

    #############
    # EFFECTIFS #
    #############

    # Effectif (Employee count) mappings

    EFFECTIF = {
        BilanType.TBS: {"field": "m1", "code": "376"},
        BilanType.TBC: {"field": "m1", "code": "YP"},
    }

    EFFECTIF_N_1 = {
        BilanType.TBS: {"field": "m2", "code": "376"},
        BilanType.TBC: {"field": "m2", "code": "YP"},
    }


class FinancialDataExtractor:
    """Extractor for financial data from bilans saisis."""

    @staticmethod
    def extract_from_pages(
        pages: List[Dict[str, Any]],
        field: str,
        code: str,
    ) -> Optional[int]:
        """
        Extract financial data from pages using field and code.

        Args:
            pages:
                List of pages from bilan data
            field:
                Field name (e.g., 'm1', 'm2', 'm3', 'm4')
            code:
                Code to match (e.g., 'DL', 'R6', '142')

        Returns:
            int:
                Extracted value or None if not found or invalid
        """
        try:
            value = next(
                int(liasse[field])
                for page in pages
                for liasse in page.get("liasses", [])
                if liasse.get("code") == code
            )
            return value
        except (
            StopIteration,
            ValueError,
            KeyError,
            TypeError,
        ):
            return None

    @staticmethod
    def extract_with_fallback(
        pages: List[Dict[str, Any]],
        mappings: List[Dict[str, str]],
    ) -> Optional[int]:
        """
        Extract data with fallback options.

        Tries multiple field/code combinations in order until one succeeds.
        This is necessary because the same financial metric can appear in
        different locations depending on company type, reporting format, etc.

        Parameters:
            pages:
                List of pages from bilan data
            mappings:
                List of mapping dictionaries with 'field' and 'code'
                (ordered by preference, primary source first)

        Returns:
            int:
                Extracted value from first successful mapping, or None if all fail.

        Example:
            >>> mappings = [
            ...     {"field": "m1", "code": "310"},  # Primary: Compte de Résultat
            ...     {"field": "m3", "code": "136"},  # Fallback: Bilan - Passif
            ... ]
            >>> extract_with_fallback(pages, mappings)
        """
        for mapping in mappings:
            result = FinancialDataExtractor.extract_from_pages(
                pages=pages,
                field=mapping["field"],
                code=mapping["code"],
            )
            if result is not None:
                return result
        return None

    @staticmethod
    def extract_sum_from_components(
        pages: List[Dict[str, Any]],
        components: Dict[str, Dict[str, str]],
    ) -> Optional[int]:
        """
        Extract data by summing multiple components.

        Generic method to sum financial values from multiple field/code pairs.
        Used for TBB capitaux propres, TBS chiffre d'affaires, etc.

        Args:
            pages:
                List of pages from bilan data
            components:
                Dictionary of components to sum, where each value is a dict
                with 'field' and 'code' keys

        Returns:
            int:
                Sum of all component values, or None if total is 0

        Example:
            >>> components = {
            ...     "ventes": {"field": "m1", "code": "210"},
            ...     "production": {"field": "m1", "code": "214"}
            ... }
            >>> extract_sum_from_components(pages, components)
        """
        total = 0

        for mapping in components.values():
            value = FinancialDataExtractor.extract_from_pages(
                pages=pages,
                field=mapping["field"],
                code=mapping["code"],
            )
            if value is not None:
                total += value

        return total if total > 0 else None

    @classmethod
    def get_capitaux_propres(
        cls,
        bilan_data: Dict[str, Any],
        position: int,
        bilan_type: BilanType,
        n_minus_1: bool = False,
    ) -> Optional[int]:
        """
        Get 'capitaux propres' (equity) for a specific bilan type.

        Parameters:
            bilan_data (dict):
                Full bilan saisis data.
            position (int):
                Position in the bilans array.
            bilan_type (BilanType):
                Type of bilan.
            n_minus_1 (bool):
                Whether to get N-1 (previous year) data.

        Returns:
            int:
                'Capitaux propres' (equity) value or None
        """

        try:
            pages = bilan_data["bilansSaisis"][position]["bilanSaisi"]["bilan"]["detail"]["pages"]

            # TBB requires summing multiple components
            if bilan_type == BilanType.TBB:
                components = (
                    FinancialCodeMapping.CAPITAUX_PROPRES_N_1_TBB
                    if n_minus_1
                    else FinancialCodeMapping.CAPITAUX_PROPRES_TBB
                )
                return cls.extract_sum_from_components(
                    pages=pages,
                    components=components,
                )

            # All other types (TBK, TBS, TBC) use single field/code lookup
            mappings = (
                FinancialCodeMapping.CAPITAUX_PROPRES_N_1
                if n_minus_1
                else FinancialCodeMapping.CAPITAUX_PROPRES
            )
            if bilan_type in mappings:
                mapping = mappings[bilan_type]
                return cls.extract_from_pages(
                    pages=pages,
                    field=mapping["field"],
                    code=mapping["code"],
                )

        except (
            KeyError,
            IndexError,
            TypeError,
        ):
            pass

        return None

    @classmethod
    def get_benefice_perte(
        cls,
        bilan_data: Dict[str, Any],
        position: int,
        bilan_type: BilanType,
        n_minus_1: bool = False,
    ) -> Optional[int]:
        """
        Get bénéfice/perte (profit/loss) for a specific bilan type.

        Args:
            bilan_data: Full bilan saisis data
            position: Position in the bilans array
            bilan_type: Type of bilan
            n_minus_1: Whether to get N-1 (previous year) data

        Returns:
            int: Bénéfice/perte value or None
        """
        try:
            pages = bilan_data["bilansSaisis"][position]["bilanSaisi"]["bilan"]["detail"]["pages"]

            mappings = (
                FinancialCodeMapping.BENEFICE_PERTE_N_1
                if n_minus_1
                else FinancialCodeMapping.BENEFICE_PERTE
            )

            if bilan_type in mappings:
                mapping = mappings[bilan_type]
                if isinstance(mapping, list):
                    return cls.extract_with_fallback(
                        pages=pages,
                        mappings=mapping,
                    )
                return cls.extract_from_pages(
                    pages=pages,
                    field=mapping["field"],
                    code=mapping["code"],
                )

        except (
            KeyError,
            IndexError,
            TypeError,
        ):
            pass

        return None

    @classmethod
    def get_resultat_exercice_tbb(
        cls,
        bilan_data: Dict[str, Any],
        position: int,
        n_minus_1: bool = False,
    ) -> Optional[int]:
        """
        Get résultat exercice for TBB type.

        Args:
            bilan_data: Full bilan saisis data
            position: Position in the bilans array
            n_minus_1: Whether to get N-1 (previous year) data

        Returns:
            int: Résultat exercice value or None
        """
        try:
            pages = bilan_data["bilansSaisis"][position]["bilanSaisi"]["bilan"]["detail"]["pages"]
            mappings = (
                FinancialCodeMapping.RESULTAT_EXERCICE_N_1_TBB
                if n_minus_1
                else FinancialCodeMapping.RESULTAT_EXERCICE_TBB
            )
            return cls.extract_with_fallback(
                pages=pages,
                mappings=mappings,
            )
        except (
            KeyError,
            IndexError,
            TypeError,
        ):
            return None

    @classmethod
    def get_chiffre_affaires(
        cls,
        bilan_data: Dict[str, Any],
        position: int,
        bilan_type: BilanType,
        n_minus_1: bool = False,
    ) -> Optional[int]:
        """
        Get chiffre d'affaires (turnover) for a specific bilan type.

        Args:
            bilan_data (dict):
                Full bilan saisis data.
            position (int):
                Position in the bilans array.
            bilan_type (BilanType):
                Type of bilan.
            n_minus_1 (bool):
                Whether to get N-1 (previous year) data.

        Returns:
            int:
                Chiffre d'affaires value or None.
        """

        try:
            pages = bilan_data["bilansSaisis"][position]["bilanSaisi"]["bilan"]["detail"]["pages"]

            if bilan_type == BilanType.TBS:
                components = (
                    FinancialCodeMapping.CHIFFRE_AFFAIRES_N_1_TBS
                    if n_minus_1
                    else FinancialCodeMapping.CHIFFRE_AFFAIRES_TBS
                )
                # Sum TBS components:
                # Ventes de marchandises,
                # Production vendue de biens,
                # Production vandue de services
                return cls.extract_sum_from_components(
                    pages=pages,
                    components=components,
                )

            mappings = (
                FinancialCodeMapping.CHIFFRE_AFFAIRES_N_1
                if n_minus_1
                else FinancialCodeMapping.CHIFFRE_AFFAIRES
            )
            if bilan_type in mappings:
                mapping = mappings[bilan_type]
                return cls.extract_from_pages(
                    pages=pages,
                    field=mapping["field"],
                    code=mapping["code"],
                )

        except (
            KeyError,
            IndexError,
            TypeError,
        ):
            pass

        return None

    @classmethod
    def get_effectif(
        cls,
        bilan_data: Dict[str, Any],
        position: int,
        bilan_type: BilanType,
        n_minus_1: bool = False,
    ) -> Optional[int]:
        """
        Get effectif (employee count) for a specific bilan type.

        Args:
            bilan_data: Full bilan saisis data
            position: Position in the bilans array
            bilan_type: Type of bilan
            n_minus_1: Whether to get N-1 (previous year) data

        Returns:
            int: Effectif value or None
        """
        try:
            pages = bilan_data["bilansSaisis"][position]["bilanSaisi"]["bilan"]["detail"]["pages"]

            mappings = (
                FinancialCodeMapping.EFFECTIF_N_1 if n_minus_1 else FinancialCodeMapping.EFFECTIF
            )

            if bilan_type in mappings:
                mapping = mappings[bilan_type]
                return cls.extract_from_pages(
                    pages=pages,
                    field=mapping["field"],
                    code=mapping["code"],
                )

        except (
            KeyError,
            IndexError,
            TypeError,
        ):
            pass

        return None
