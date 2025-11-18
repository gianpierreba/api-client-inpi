"""
Demonstration module for the refactored French Companies API Client.

This module shows how to use the new API structure to fetch company data
from INPI. It reads SIREN/SIRET codes from a text file and
retrieves information for each company.

Usage:
    python main.py

Requirements:
    - .env file with INPI_USERNAME and INPI_PASSWORD
    - sirens.txt file with one SIREN or SIRET per line (lines starting with '#' are ignored)
"""

import os
import traceback
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

from config import Config
from exceptions import (
    ApiRequestError,
    AuthenticationError,
    InvalidSirenError,
)
from inpi import BilanType, ComptesAnnuelsClient, InpiCompaniesClient
from inpi.financial_extractor import FinancialDataExtractor


class CompanyDataFetcher:
    """
    Demonstrates fetching company data from INPI API.
    """

    def __init__(self):
        """
        Initialize the fetcher with credentials from environment.
        """

        # Load environment variables
        load_dotenv()

        # Validate configuration
        print("=" * 80)
        print("🔧 Configuration Status")
        print("=" * 80)
        config_status = Config.validate_configuration()
        for key, value in config_status.items():
            status = "✓" if value else "✗"
            print(f"{status} {key}: {value}")
        print("----" * 9)

        # Get credentials
        try:
            self.inpi_username, self.inpi_password = Config.get_inpi_credentials()
            print("✓ INPI credentials loaded successfully.\n")
        except ValueError as e:
            print(f"✗ Configuration Error: {e}")
            print("\nPlease create a .env file with your credentials.")
            print("See .env.example for the template.\n")
            raise

    def read_sirens_from_file(
        self,
        filepath: str,
    ) -> List[str]:
        """
        Read SIREN/SIRET codes from a text file.

        Args:
            filepath: Path to the text file (one SIREN/SIRET per line)

        Returns:
            List of SIREN/SIRET codes
        """

        path = Path(filepath)
        if not path.exists():
            print(f"✗ File not found: {filepath}")
            return []

        with open(path, "r", encoding="utf-8") as f:
            # Read lines, strip whitespace, skip empty lines
            codes = [line.strip() for line in f if line.strip()]

        print(f"✓ Read {len(codes)} SIREN/SIRET codes from {filepath}\n")
        return codes

    def fetch_inpi_company_data(
        self,
        siren: str,
    ) -> Optional[dict]:
        """
        Fetch company data from INPI API.

        Args:
            siren: SIREN code (9 digits)

        Returns:
            dict with company data or None if error
        """
        print(f"  📋 Fetching INPI data for SIREN: {siren}")

        try:
            with InpiCompaniesClient(
                username=self.inpi_username,
                password=self.inpi_password,
                siren=siren,
            ) as client:
                # Fetch various company information
                data = {
                    "siren": siren,
                    "nom_societe": client.nom_societe(),
                    "forme_juridique": client.forme_juridique(),
                    "code_ape": client.code_ape(),
                    "nom_commercial": client.nom_commercial(),
                    "capital": client.montant_capital(),
                    "adresse": {
                        "numero_voie": client.numero_voie(),
                        "code_postal": client.code_postal(),
                        "ville": client.ville(),
                        "pays": client.pays(),
                    },
                    "siret_siege": client.siret_siege(),
                    "description": client.description_detaillee(),
                    "dirigeants_count": len(client.dirigeants_box()),
                }

                # Get dirigeants info (first 3 as example)
                dirigeants = []
                individus_indices = client.nombre_individus()[:3]  # First 3 only
                for individu in individus_indices:
                    dirigeants.append(
                        {
                            "nom": client.nom_dirigeant(individu),
                            "prenom": client.prenom_dirigeant(individu),
                            "role": client.role_dirigeant(individu),
                            "date_naissance": client.birth_date_dirigeant(individu),
                        }
                    )

                data["dirigeants_sample"] = dirigeants

                print(f"  ✓ Company: {data['nom_societe']}")
                print(f"    Legal form: {data['forme_juridique']}")
                print(f"    Location: {data['adresse']['ville']}")
                print(f"    Dirigeants: {data['dirigeants_count']}")

                return data

        except AuthenticationError as e:
            print(f"  ✗ Authentication failed: {e}")
            return None
        except InvalidSirenError as e:
            print(f"  ✗ Invalid SIREN: {e}")
            return None
        except ApiRequestError as e:
            print(f"  ✗ API request failed: {e}")
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"  ✗ Unexpected error: {e}")
            return None

    def fetch_inpi_financial_data(
        self,
        siren: str,
    ) -> Optional[dict]:
        """
        Fetch financial statements from INPI API.

        Args:
            siren: SIREN code (9 digits)

        Returns:
            dict with financial data or None if error
        """

        print(f"  💰 Fetching INPI financial data for SIREN: {siren}")

        try:
            with ComptesAnnuelsClient(
                username=self.inpi_username,
                password=self.inpi_password,
                siren=siren,
            ) as client:
                # Check if financial statements are available
                bilans_count = client.bilans_saisis_len()

                if bilans_count == 0:
                    print("  ℹ️  No financial statements available")
                    return None

                print(f"  ✓ Found {bilans_count} financial statement(s)")

                # Get the most recent statement type
                type_bilan_code = client.type_bilan_saisi(position=0)
                date_cloture = client.date_cloture(position=0)

                # Determine the correct BilanType
                bilan_type = None
                if type_bilan_code == "C":
                    bilan_type = BilanType.TBC
                elif type_bilan_code == "S":
                    bilan_type = BilanType.TBS
                elif type_bilan_code == "K":
                    bilan_type = BilanType.TBK
                elif type_bilan_code == "B":
                    bilan_type = BilanType.TBB

                # Extract financial data using FinancialDataExtractor
                chiffre_affaires = None
                benefice_perte = None
                capitaux_propres = None
                effectif = None

                if bilan_type:
                    chiffre_affaires = FinancialDataExtractor.get_chiffre_affaires(
                        bilan_data=client.documents_associes_entreprise,
                        position=0,
                        bilan_type=bilan_type,
                    )
                    benefice_perte = FinancialDataExtractor.get_benefice_perte(
                        bilan_data=client.documents_associes_entreprise,
                        position=0,
                        bilan_type=bilan_type,
                    )
                    capitaux_propres = FinancialDataExtractor.get_capitaux_propres(
                        bilan_data=client.documents_associes_entreprise,
                        position=0,
                        bilan_type=bilan_type,
                    )
                    effectif = FinancialDataExtractor.get_effectif(
                        bilan_data=client.documents_associes_entreprise,
                        position=0,
                        bilan_type=bilan_type,
                    )

                data = {
                    "siren": siren,
                    "bilans_count": bilans_count,
                    "date_cloture": date_cloture,
                    "type_bilan": type_bilan_code,
                    "chiffre_affaires": chiffre_affaires,
                    "benefice_perte": benefice_perte,
                    "capitaux_propres": capitaux_propres,
                    "effectif": effectif,
                }

                print(f"    Date: {data['date_cloture']}")
                print(f"    Type: {data['type_bilan']}")
                if data["chiffre_affaires"]:
                    print(f"    CA: {data['chiffre_affaires']:,.2f} €")
                if data["benefice_perte"] is not None:
                    print(f"    Net Profit: {data['benefice_perte']:,.2f} €")
                if data["capitaux_propres"]:
                    print(f"    Equity: {data['capitaux_propres']:,.2f} €")

                return data

        except AuthenticationError as e:
            print(f"  ✗ Authentication failed: {e}")
            return None
        except ApiRequestError as e:
            print(f"  ✗ API request failed: {e}")
            return None
        except Exception as e:  # pylint: disable=broad-exception-caught
            print(f"  ✗ Unexpected error: {e}")
            return None

    def process_companies(
        self,
        codes: List[str],
        max_count: Optional[int] = None,
    ):
        """
        Process a list of SIREN/SIRET codes.

        Args:
            codes: List of SIREN/SIRET codes
            max_count: Maximum number to process (None for all)
        """

        if max_count:
            codes = codes[:max_count]

        print("=" * 80)
        print(f"📊 Processing {len(codes)} company code(s)")
        print("=" * 80)
        print()

        results = {"successful": 0, "failed": 0, "companies": []}

        for i, code in enumerate(codes, start=1):
            print(f"\n[{i}/{len(codes)}] Processing: {code}")
            print("-" * 80)

            company_data = {
                "code": code,
                "inpi_data": None,
                "inpi_financial": None,
            }

            # Extract SIREN (needed for INPI)
            if len(code) == 9:
                siren = code
            elif len(code) == 14:
                siren = code[:9]
            else:
                print(f"✗ Invalid code: {code}\n")
                results["failed"] += 1
                continue

            # Fetch INPI company data
            company_data["inpi_data"] = self.fetch_inpi_company_data(siren)

            # Fetch INPI financial data
            company_data["inpi_financial"] = self.fetch_inpi_financial_data(siren)

            # Track results
            if any(
                [
                    company_data["inpi_data"],
                    company_data["inpi_financial"],
                ]
            ):

                results["successful"] += 1
                results["companies"].append(company_data)
            else:
                results["failed"] += 1

            print()

        # Summary
        print("=" * 80)
        print("📈 Summary")
        print("=" * 80)
        print(f"✓ Successful: {results['successful']}")
        print(f"✗ Failed: {results['failed']}")
        print(f"📊 Total: {len(codes)}")
        print()

        return results


def main():
    """
    Main demonstration function.
    """

    print("\n" + "=" * 80)
    print("🚀 French Companies API Client - Demonstration")
    print("=" * 80)
    print()

    try:
        # Initialize fetcher
        fetcher = CompanyDataFetcher()

        # Path to your SIREN/SIRET file
        # You can change this to match your file location
        test_file = "sirens.txt"

        # Check if file exists
        if not os.path.exists(test_file):
            print(f"ℹ️  Test file '{test_file}' not found.")
            print("   Creating a sample file with example SIRENs...\n")

            # Create sample file with some example SIRENs
            sample_sirens = [
                "# Sample SIREN codes for testing",
                "# Add your own SIREN or SIRET codes below (one per line)",
                "# Lines starting with # are ignored",
                "",
                "# Example: 552032534 (Total Energies)",
                "# Example: 542051180 (Carrefour)",
                "",
            ]

            with open(test_file, "w", encoding="utf-8") as f:
                f.write("\n".join(sample_sirens))

            print(f"✓ Created sample file: {test_file}")
            print("   Please add your SIREN/SIRET codes to this file and run again.\n")
            return

        # Read codes from file
        codes = fetcher.read_sirens_from_file(
            filepath=test_file,
        )
        fetcher.process_companies(
            codes=codes,
            max_count=2,  # Modify at will for demostration purpose.
        )

        if not codes:
            print("⚠️  No valid codes found in file.")
            print("   Please add SIREN or SIRET codes (one per line).\n")
            return
        print("✅ Demonstration complete!")
        print("\nNext steps:")
        print("1. Review the output above.")
        print("2. Check that data is being fetched correctly.")
        print("3. Modify this script for your specific needs.")
        print("4. Integrate with your main workflow.\n")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user\n")
    except Exception as e:  # pylint: disable=broad-exception-caught
        print(f"\n❌ Fatal error: {e}\n")
        traceback.print_exc()


if __name__ == "__main__":
    main()
