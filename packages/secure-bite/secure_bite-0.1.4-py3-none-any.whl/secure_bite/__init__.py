r"""
SecureBite — Secure Authentication & Session Management for Django
------------------------------------------------------------------
A robust JWT-based authentication middleware & utilities layer for Django REST Framework.
"""

__title__ = "secure_bite"
__version__ = "0.1.4"
__author__ = "Mbulelo Peyi"
__license__ = "MIT"
__copyright__ = "Copyright 2025 Mbulelo Peyi"

# Version alias
VERSION = __version__

import warnings
import importlib


def _check_dependencies():
    """Ensure optional dependencies are installed for extended functionality."""
    optional_deps = {
        "dj_rest_auth": "Provides REST endpoints for authentication (used by secure_bite.auth_provider).",
        "allauth": "Provides OAuth/social account integrations required by dj_rest_auth.",
    }

    for pkg, desc in optional_deps.items():
        if importlib.util.find_spec(pkg) is None:
            warnings.warn(
                f"Optional dependency '{pkg}' not found.\n"
                f"   → {desc}\n"
                f"   To install all optional features, run:\n"
                f"     pip install secure_bite[full]\n",
                ImportWarning,
                stacklevel=2,
            )


_check_dependencies()
