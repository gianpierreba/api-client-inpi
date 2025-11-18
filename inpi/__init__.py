"""
INPI API client modules.

This module provides access to INPI (Institut national de la propriété industrielle) data including:
- Company information and dirigeants
- Financial statements (comptes annuels)
- Associated documents (actes)
"""

from .authenticator import InpiAuthenticator
from .companies import InpiCompaniesClient
from .documents import ActesClient
from .financial_extractor import BilanType, FinancialDataExtractor, FinancialMetricType
from .financials import ComptesAnnuelsClient

__all__ = [
    "InpiAuthenticator",
    "InpiCompaniesClient",
    "ComptesAnnuelsClient",
    "ActesClient",
    "FinancialDataExtractor",
    "BilanType",
    "FinancialMetricType",
]
