"""
INPI API Python Client for accessing French company data
from INPI - Institut National de la Propriété Industrielle

Features:
- Clean, modular architecture
- Comprehensive error handling
- Input validation (SIREN/SIRET)
- Environment variable configuration
- Type hints throughout
- Context manager support

Quick Start:
    from dotenv import load_dotenv
    load_dotenv()

    from api_client_inpi import InpiCompaniesClient

    # INPI company data
    with InpiCompaniesClient(username, password, siren="552032534") as client:
        print(client.nom_societe())

For more information, see README.md
"""

__version__ = "2.0.0"
__author__ = "Gianpierre Benites"
__license__ = "MIT"

# Configuration and utilities
from .config import Config
from .exceptions import (
    ApiClientError,
    ApiRequestError,
    AuthenticationError,
    DataNotFoundError,
    InvalidSirenError,
    InvalidSiretError,
    ValidationError,
)

# INPI modules
from .inpi import (
    ActesClient,
    BilanType,
    ComptesAnnuelsClient,
    FinancialDataExtractor,
    InpiAuthenticator,
    InpiCompaniesClient,
)
from .utils.validators import SirenSiretValidator

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__license__",
    # INPI clients
    "InpiCompaniesClient",
    "ComptesAnnuelsClient",
    "ActesClient",
    "InpiAuthenticator",
    "FinancialDataExtractor",
    "BilanType",
    # Configuration & Utilities
    "Config",
    "SirenSiretValidator",
    # Exceptions
    "ApiClientError",
    "AuthenticationError",
    "ValidationError",
    "ApiRequestError",
    "DataNotFoundError",
    "InvalidSirenError",
    "InvalidSiretError",
]
