from django.apps import AppConfig


class SecureBiteConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'secure_bite'

    def ready(self):
        # load provider configs from settings on startup
        from secure_bite.provider_registry import ProviderRegistry
        import secure_bite.signals

        ProviderRegistry.load_providers()