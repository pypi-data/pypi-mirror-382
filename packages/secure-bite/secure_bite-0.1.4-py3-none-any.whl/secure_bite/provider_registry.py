from secure_bite import defaults
from secure_bite.auth_providers.oauth2 import OAuth2Provider


class ProviderRegistry:
    _providers = {}

    @classmethod
    def load_providers(cls):
        """
        Loads providers from defaults.SECURE_BITE_PROVIDERS.
        Example settings format:
        SECURE_BITE_PROVIDERS = {
            "google": { "client_id": "...", "client_secret": "...", "auth_url": "...",
                        "token_url": "...", "userinfo_url": "...", "scope": "openid email profile",
                        "redirect_uri": "https://api.example.com/auth/oauth/callback/?provider=google" },
            ...
        }
        """
        cls._providers = {}
        conf = getattr(defaults, "SECURE_BITE_PROVIDERS", {}) or {}
        for name, cfg in conf.items():
            cls._providers[name] = OAuth2Provider(
                name=name,
                client_id=cfg.get("client_id"),
                client_secret=cfg.get("client_secret"),
                auth_url=cfg.get("auth_url"),
                token_url=cfg.get("token_url"),
                userinfo_url=cfg.get("userinfo_url"),
                scope=cfg.get("scope", ""),
                redirect_uri=cfg.get("redirect_uri"),
                extra_auth_params=cfg.get("extra_auth_params"),
                token_headers=cfg.get("token_headers"),
                userinfo_method=cfg.get("userinfo_method", "GET"),
            )

    @classmethod
    def get(cls, name):
        if name not in cls._providers:
            raise KeyError(f"Provider '{name}' is not configured for secure_bite.")
        return cls._providers[name]

    @classmethod
    def list(cls):
        return list(cls._providers.keys())
