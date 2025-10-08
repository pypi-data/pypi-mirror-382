"""
Default settings for secure_bite app that automatically merge with
global project settings if defined in django.conf.settings.
"""

from datetime import timedelta
from django.conf import settings as django_settings
from copy import deepcopy

# --------------------------
# Default configurations
# --------------------------

DEFAULT_SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
}

DEFAULT_JWT_AUTH_COOKIE_SETTINGS = {
    "AUTH_COOKIE": "authToken",
    "REFRESH_COOKIE": "refreshToken",
    "AUTH_COOKIE_HTTP_ONLY": True,
    "AUTH_COOKIE_SECURE": False,
    "AUTH_COOKIE_SAMESITE": "Lax",
    "AUTH_COOKIE_PATH": "/",
    "USER_SERIALIZER": "secure_bite.serializers.UserSerializer",
}

DEFAULT_SECURE_BITE_PROVIDERS = {}

# --------------------------
# Utility: recursive dict merge
# --------------------------

def deep_merge(base: dict, overrides: dict) -> dict:
    """
    Recursively merge two dictionaries. The `overrides` dictionary takes precedence.
    """
    merged = deepcopy(base)
    for key, value in (overrides or {}).items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


# --------------------------
# Merge global Django settings with defaults
# --------------------------

SIMPLE_JWT = deep_merge(DEFAULT_SIMPLE_JWT, getattr(django_settings, "SIMPLE_JWT", {}))
JWT_AUTH_COOKIE_SETTINGS = deep_merge(
    DEFAULT_JWT_AUTH_COOKIE_SETTINGS, getattr(django_settings, "JWT_AUTH_COOKIE_SETTINGS", {})
)
SECURE_BITE_PROVIDERS = deep_merge(
    DEFAULT_SECURE_BITE_PROVIDERS, getattr(django_settings, "SECURE_BITE_PROVIDERS", {})
)

# --------------------------
# Helper access function
# --------------------------

def get_setting(key: str, default=None):
    """
    Retrieve a setting from Django settings, falling back to merged defaults.
    Example:
        get_setting("SIMPLE_JWT.ACCESS_TOKEN_LIFETIME")
    """
    parts = key.split(".")
    current = {
        "SIMPLE_JWT": SIMPLE_JWT,
        "JWT_AUTH_COOKIE_SETTINGS": JWT_AUTH_COOKIE_SETTINGS,
        "SECURE_BITE_PROVIDERS": SECURE_BITE_PROVIDERS,
    }
    try:
        for part in parts:
            current = current[part]
        return current
    except (KeyError, TypeError):
        return default
