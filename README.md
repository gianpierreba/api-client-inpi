# INPI API Client For French Companies

A comprehensive INPI API Python Client for accessing French company data from INPI
(Institut national de la propriété industrielle).

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## 📋 Table of Contents

- [Features](#features)
- [Data Sources](#data-sources)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **🔒 Secure**: Environment variable configuration, no hard-coded credentials
- **🏗️ Clean Architecture**: Modular, maintainable, and well-documented code
- **🛡️ Robust**: Comprehensive error handling and input validation
- **📝 Type Safe**: Full type hints throughout the codebase
- **🔄 Context Managers**: Automatic resource cleanup
- **🧪 Testable**: Demonstration module included

## 🌐 Data Sources

This client accesses data from [INPI - Institut national de la propriété industrielle](https://www.inpi.fr/):

### INPI (Institut National de la Propriété Industrielle)
- Company information and legal data
- Financial statements (comptes annuels)
- Official documents (actes)
- **API Documentation**:
  - [Data INPI API](https://data.inpi.fr/)
  - [Accès aux API - Entreprises](https://data.inpi.fr/content/editorial/Acces_API_Entreprises)
- Documentations techniques
  - [Documentation technique Base RNE (Registre national des entreprises)](https://www.inpi.fr/sites/default/files/2025-06/documentation%20technique%20API%20formalit%C3%A9s_v4.0.pdf)
  - [Documentation technique Comptes annuels](https://www.inpi.fr/sites/default/files/2025-06/documentation%20technique%20API_comptes_annuels%20v5.pdf)
  - [Documentation technique Actes](https://www.inpi.fr/sites/default/files/2025-06/documentation%20technique%20API%20Actes%20v4.0.pdf)
  - [Dictionnaire des données](https://www.inpi.fr/sites/default/files/2025-06/Dictionnaire_de_donnees_INPI_2025_05_09.xlsx)
  - [Table des catégories d’activités](https://www.inpi.fr/sites/default/files/INPI%20RNE%20Table%20des%20categories%20activites_2024_08_28.xlsx)

## 📦 Installation

### Requirements

- Python 3.8 or higher
- Valid INPI account credentials

### Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt:**
```
requests>=2.31.0
python-dotenv>=1.0.0
```

### Setup Credentials

1. Copy the example environment file:
```bash
cp .env.EXAMPLE .env
```

2. Edit `.env` with your credentials:
```bash
# .env
INPI_USERNAME=your_email@example.com
INPI_PASSWORD=your_password
```

3. Get your API credentials [here](https://data.inpi.fr/register).

## 🚀 Quick Start

### Two Ways to Use This API Client

#### Option 1: Using the Demonstration Module (Batch Processing)

The included `main.py` module processes multiple companies from a text file:

```bash
# 1. Create a text file with SIREN/SIRET codes (one per line)
echo "552032534" > sirens.txt
echo "542051180" >> sirens.txt

# 2. Run the demonstration module
python main.py
```

**Workflow:**
1. Place SIREN/SIRET codes in a text file (e.g., `sirens.txt`)
2. The module reads codes line by line
3. For each code, it fetches:
   - INPI company data (name, legal form, directors)
   - INPI financial statements (revenue, profits, balance sheets)
4. Results are displayed with formatted output and status indicators
5. Summary statistics are shown at the end

#### Option 2: Direct API Usage in Your Code (Recommended for Integration)

**You can call the API clients directly without using main.py:**

```python
from dotenv import load_dotenv
import os
load_dotenv()

from inpi import InpiCompaniesClient, ComptesAnnuelsClient
from config import Config

# Get credentials
username, password = Config.get_inpi_credentials()

# INPI: Get company information
with InpiCompaniesClient(username, password, siren="552032534") as client:
    print(f"Company: {client.nom_societe()}")
    print(f"Legal form: {client.forme_juridique()}")
    print(f"Location: {client.ville()}")

# INPI: Get financial statements
with ComptesAnnuelsClient(username, password, siren="552032534") as client:
    if client.bilans_saisis_len() > 0:
        ca = client.chiffre_affaires_tbc(position=0)
        print(f"Revenue: {ca:,.2f} €")
```

**Key Points:**
- `main.py` is a demonstration tool for batch processing
- For production integration, import and use the clients directly in your code
- Both approaches use the same underlying API clients
- Direct usage gives you more control and flexibility

## ⚙️ Configuration

### Environment Variables

| Variable        | Required | Description                |
| --------------- | -------- | -------------------------- |
| `INPI_USERNAME` | Yes      | Your INPI account email    |
| `INPI_PASSWORD` | Yes      | Your INPI account password |

Get your API credentials [here](https://data.inpi.fr/register).

### Validation

Check your configuration:

```python
from api_client_inpi import Config

# Validate configuration
status = Config.validate_configuration()
print(status)

# Get credentials
username, password = Config.get_inpi_credentials()
```

## 📖 Usage Examples

### INPI API Examples

#### Company Information

```python
from config import Config
from api_client_inpi import InpiCompaniesClient

# Get credentials
username, password = Config.get_inpi_credentials()

# With context manager (recommended)
with InpiCompaniesClient(username, password, siren="552032534") as client:
    # Basic information
    nom_societe = client.nom_societe()
    forme_juridique = client.forme_juridique()
    code_ape = client.code_ape()
    capital = client.montant_capital()

    # Address
    ville = client.ville()
    code_postal = client.code_postal()
    adresse = client.numero_voie()

    # Directors (dirigeants)
    individus = client.nombre_individus()

    for idx in individus:
        nom_dirigeant = client.nom_dirigeant(idx)
        prenom_dirigeant = client.prenom_dirigeant(idx)
        role = client.role_dirigeant(idx)
        print(f"Director: {prenom_dirigeant} {nom_dirigeant} - {role}")

# Without context manager (manual):
client = InpiCompaniesClient(username, password, siren="552032534")
try:
    nom_societe = client.nom_societe()
    print(nom_societe)
finally:
    client.close()
```

#### Financial Statements

```python
from config import Config
from api_client_inpi import ComptesAnnuelsClient, BilanType
from api_client_inpi import FinancialDataExtractor

# Get credentials
username, password = Config.get_inpi_credentials()

with ComptesAnnuelsClient(username, password, siren="552032534") as client:
    # Check availability
    count = client.bilans_saisis_len()
    print(f"Financial statements available: {count}")

    if count > 0:
        # Most recent statement (position 0)
        date_cloture = client.date_cloture(position=0)
        type_bilan = client.type_bilan_saisi(position=0)
        print(f"Statement type: {type_bilan}")  # e.g., "C", "S", "K", "B"

        # ⚠️ IMPORTANT: Use the correct BilanType for accurate data extraction
        # Each company files a specific type of financial statement:
        # - BilanType.TBC: Complete accounts (most common)
        # - BilanType.TBS: Simplified accounts
        # - BilanType.TBK: Consolidated accounts
        # - BilanType.TBB: Bank accounts
        # The bilan_type parameter MUST match the actual statement type
        # returned by type_bilan_saisi() to get correct financial data.

        # Determine the correct BilanType based on type_bilan
        if type_bilan == "C":
            bilan_type = BilanType.TBC
        elif type_bilan == "S":
            bilan_type = BilanType.TBS
        elif type_bilan == "K":
            bilan_type = BilanType.TBK
        elif type_bilan == "B":
            bilan_type = BilanType.TBB
        else:
            print(f"Unsupported bilan type: {type_bilan}")
            bilan_type = None

        if bilan_type:
            # Extract financial data using the correct bilan type
            # Most recent statement (position 0)
            capitaux = FinancialDataExtractor.get_capitaux_propres(
                bilan_data=client.documents_associes_entreprise,
                position=0,
                bilan_type=bilan_type  # ← Must match actual statement type!
            )

            chiffre_affaires = FinancialDataExtractor.get_chiffre_affaires(
                bilan_data=client.documents_associes_entreprise,
                position=0,
                bilan_type=bilan_type
            )

            benefice_perte = FinancialDataExtractor.get_benefice_perte(
                bilan_data=client.documents_associes_entreprise,
                position=0,
                bilan_type=bilan_type
            )

            print(f"Equity: {capitaux:,} €")
            print(f"Revenue: {chiffre_affaires:,} €")
            print(f"Profit/Loss: {benefice_perte:,} €")
```

> **⚠️ Note:** Financial data extraction is currently limited to key metrics (revenue, profit
> loss, equity, employee count). Additional financial fields and support for agricultural bilan
> types (TBAC/TBAS) will be added in future releases. For more details about *bilan types* and
> *financial fields* click [here](https://www.inpi.fr/sites/default/files/2025-06/documentation%20technique%20API_comptes_annuels%20v5.pdf)
> to download *Documentation technique Comptes annuels* or read [Data sources](#-data-sources)

#### Official Documents (Actes)

```python
from config import Config
from api_client_inpi import ActesClient

# Get credentials
username, password = Config.get_inpi_credentials()

with ActesClient(username, password, siren="552032534") as client:
    # Check how many actes are available
    actes_count = client.actes_len()
    print(f"Number of actes: {actes_count}")

    if actes_count > 0:
        # Get list of all actes with metadata
        actes_list = client.acte_depot_id()
        # Returns: [(position, date_depot, id, type_rdd), ...]

        for position, date_depot, acte_id, type_acte in actes_list:
            print(f"Acte #{position + 1}:")
            print(f"  Date: {date_depot}")
            print(f"  ID: {acte_id}")
            print(f"  Type: {type_acte}")

        # Get metadata for a specific acte
        acte_id = actes_list[0][2]  # Get ID of first acte
        metadata = client.recherche_acte_pdf(id_acte=acte_id)
        print(f"Acte details: {metadata}")

        # Download acte PDF
        result = client.telecharger_acte_pdf(
            id_acte=acte_id,
            file_path="/path/to/download/folder",
            file_name="acte_document"  # Will be saved as "acte_document.pdf"
        )
        print(result)  # "PDF acte downloaded successfully"
```

### Input Validation

```python
from api_client_inpi import SirenSiretValidator, InvalidSirenError

try:
    # Validate SIREN
    siren = SirenSiretValidator.validate_siren("552032534")

    # Validate SIRET
    siret = SirenSiretValidator.validate_siret("55203253400054")

    # Extract SIREN from SIRET
    siren_from_siret = SirenSiretValidator.extract_siren_from_siret(siret)

    # Check without raising exception
    is_valid = SirenSiretValidator.is_valid_siren("552032534")

except InvalidSirenError as e:
    print(f"Invalid format: {e}")
```

### Error Handling

```python
from api_client_inpi import (
    InpiCompaniesClient,
    AuthenticationError,
    ApiRequestError,
    InvalidSirenError
)

try:
    with InpiCompaniesClient(username, password, siren="552032534") as client:
        data = client.nom_societe()

except AuthenticationError as e:
    print(f"Authentication failed: {e}")

except InvalidSirenError as e:
    print(f"Invalid SIREN format: {e}")

except ApiRequestError as e:
    print(f"API request failed: {e.status_code}")
    print(f"Response: {e.response_text}")

except Exception as e:
    print(f"Unexpected error: {e}")
```

## 📚 API Reference

### INPI Clients

#### `InpiCompaniesClient`
- Company information and directors
- Methods: `nom_societe()`, `forme_juridique()`, `code_ape()`, `dirigeants_box()`, etc.

#### `ComptesAnnuelsClient`
- Financial statements (PDF and JSON)
- Methods: `bilans_saisis_len()`, `chiffre_affaires_tbc()`, `benefice_perte_tbc()`, etc.

#### `ActesClient`
- Official documents
- Methods: `actes_len()`, `telecharger_acte_pdf()`, etc.

### Utilities

#### `Config`
- Configuration management
- Methods: `get_inpi_credentials()`, `validate_configuration()`

#### `SirenSiretValidator`
- Input validation
- Methods: `validate_siren()`, `validate_siret()`, `extract_siren_from_siret()`

#### `FinancialDataExtractor`
- Financial data extraction
- Methods: `get_capitaux_propres()`, `get_benefice_perte()`, `get_chiffre_affaires()`

### Exceptions

- `ApiClientError` - Base exception
- `AuthenticationError` - Authentication failures
- `ApiRequestError` - API request failures
- `ValidationError` - Input validation errors
- `InvalidSirenError` - Invalid SIREN format
- `InvalidSiretError` - Invalid SIRET format
- `DataNotFoundError` - Data not found in API response

## 🏗️ Project Structure

```
api-client-inpi/
├── __init__.py              # Main package entry point
├── config.py                # Configuration management
├── exceptions.py            # Custom exception classes
├── main.py                  # Demonstration module
├── base/                    # Base classes
│   ├── http_client.py      # Base HTTP client
│   └── authenticator.py    # Base authenticator
├── utils/                   # Utilities
│   └── validators.py       # SIREN/SIRET validation
└── inpi/                    # INPI API modules
    ├── authenticator.py    # INPI authentication
    ├── companies.py        # Company data
    ├── financials.py       # Financial statements
    ├── documents.py        # Documents
    └── financial_extractor.py  # Financial data extraction

Documentation/
├── README.md               # This file
├── .env.EXAMPLE           # Environment variables template
└── CONTRIBUTING.md         # Development Setup
```

## 🤝 Contributing

Contributions are welcome !

Feel free to submit a Pull Request !

### Development Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your `.env` file with test credentials
5. Run the demonstration module to verify setup

### Code Style

- Follow PEP 8 guidelines
- Use type hints
- Document all public methods with docstrings
- Handle errors gracefully

## 📄 Licenses

- This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
- This INPI API Python Client accesses datasets from INPI (Institut National de la
  Propriété Industrielle). The data reuse is governed by INPI's homologated
  reuse licences (for RNE and industrial property).
  See [INPI licence page](https://data.inpi.fr/content/editorial/licences_reutilisation_donnees_inpi)
  for details.

## 📞 Support

For questions, bug reports, or feature requests, please use the
[GitHub Issues](https://github.com/gianpierreba/api-client-inpi/issues) page.

> ⚠️ When reporting an issue, please include:
> - Your Python version and environment
> - Steps to reproduce the problem
> - Any error messages or stack traces

## 📊 Version History

### Version 2.0.0 (2025-10-27)
- Complete architecture refactoring
- Added environment variable configuration
- Comprehensive error handling
- Full type hints
- Modular, maintainable codebase

### Version 1.0.0 (2023-06-13)
- Initial release with basic functionality
- Intended for internal use by professionals in the M&A sector in France

---

**Made with ❤️ for the French business data community**
