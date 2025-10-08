from django.conf import settings
from django.db import models


class SocialAccount(models.Model):
    """
    Helper model to link a provider account to a local user. Migrations will be required.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="social_accounts")
    provider = models.CharField(max_length=64)
    provider_id = models.CharField(max_length=256)
    extra_data = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("provider", "provider_id")
        indexes = [models.Index(fields=("provider", "provider_id"))]

    def __str__(self):
        return f"{self.provider}:{self.provider_id}"

