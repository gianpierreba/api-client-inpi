"""
Version information for French Companies API Client
"""

__version__ = "2.0.0"
__version_info__ = (2, 0, 0)
VERSION_HISTORY = {
    "2.0.0": {
        "date": "2025-10-27",
        "changes": [
            "Complete architecture refactoring",
            "Eliminated 100+ duplicate methods",
            "Added environment variable configuration",
            "Removed hard-coded credentials (security fix)",
            "Comprehensive error handling with custom exception hierarchy",
            "Full type hints throughout codebase",
            "Modular, maintainable codebase with base classes",
            "Context manager support for automatic resource cleanup",
            "SIREN/SIRET input validation",
        ],
        "breaking_changes": [
            "Removed backward compatibility aliases (InpiCompanies -> InpiCompaniesClient)",
            "Changed from hard-coded credentials to environment variables",
            "New import paths and module structure",
            "Requires .env file setup",
        ],
    },
    "1.0.0": {
        "date": "2023-06-13",
        "changes": [
            "Initial release with basic functionality",
            "Intended for internal use by professionals in the M&A sector in France",
        ],
        "breaking_changes": [],
    },
}


def get_version():
    """Get current version string"""
    return __version__


def get_version_info():
    """Get current version as tuple"""
    return __version_info__
