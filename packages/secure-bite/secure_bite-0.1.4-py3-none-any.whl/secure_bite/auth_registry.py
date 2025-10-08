from secure_bite import defaults
from secure_bite.auth_providers.oauth2 import OAuth2Provider

class ProviderRegistry:
    _providers = {}

    @classmethod
    def load_providers(cls):
        for name, conf in defaults.SECURE_BITE_PROVIDERS.items():
            cls._providers[name] = OAuth2Provider(
                name=name,
                client_id=conf["client_id"],
                client_secret=conf["client_secret"],
                auth_url=conf["auth_url"],
                token_url=conf["token_url"],
                userinfo_url=conf["userinfo_url"],
                scope=conf["scope"],
            )

    @classmethod
    def get(cls, name):
        return cls._providers[name]

    @classmethod
    def list(cls):
        return list(cls._providers.keys())
