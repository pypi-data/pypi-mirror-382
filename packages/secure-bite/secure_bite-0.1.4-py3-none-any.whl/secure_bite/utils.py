import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from secure_bite import defaults
from secure_bite.signals import user_account_created

def get_jwt_cookie_settings():
    """
    Returns the JWT auth cookie settings, falling back to defaults if not overridden.
    """
    final = defaults.JWT_AUTH_COOKIE_SETTINGS
    return final

def get_simple_jwt_settings():
    """
    Returns SIMPLE_JWT settings, falling back to defaults if not overridden.
    """
    final = defaults.SIMPLE_JWT
    return final

cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()

def clear_cookie(response, name, path="/", domain=None):
    response.set_cookie(
        name,
        value="",
        max_age=0,
        expires="Thu, 01 Jan 1970 00:00:00 GMT",
        path=path,
        domain=domain,
        secure=cookie_settings["AUTH_COOKIE_SECURE"],
        httponly=cookie_settings["AUTH_COOKIE_HTTP_ONLY"],
        samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
    )

def _seconds(delta):
    """Convert timedelta to total seconds (int)."""
    return int(delta.total_seconds())

def populate_user_fields(user, user_info: dict, provider_name: str):
    """
    Generic mapper: copies values from user_info into fields
    that exist on the User model.
    """
    field_map = {
        "email": ["email"],
        "first_name": ["given_name", "first_name"],
        "last_name": ["family_name", "last_name"],
        "username": ["preferred_username", "email", "sub", "id"],
    }

    user_fields = {f.name for f in user._meta.get_fields()}

    for field, candidates in field_map.items():
        if field in user_fields:
            for key in candidates:
                value = user_info.get(key)
                if value:
                    setattr(user, field, value)
                    break

    # fallback username if missing
    if hasattr(user, "username") and not getattr(user, "username", None):
        setattr(user, "username", f"{provider_name}_{user_info.get('sub') or user_info.get('id')}")

    return user

def exchange_code_for_token(provider, code):
    """Exchange authorization code for access token."""
    config = settings.SOCIAL_AUTH_PROVIDERS[provider]
    response = requests.post(
        config["token_url"],
        data={
            "client_id": config["client_id"],
            "client_secret": config["client_secret"],
            "redirect_uri": config["redirect_uri"],
            "code": code,
            "grant_type": "authorization_code",
        },
        headers={"Accept": "application/json"},
    )
    response.raise_for_status()
    return response.json()

def get_user_info(provider, access_token):
    """Retrieve user profile info from provider."""
    config = settings.SOCIAL_AUTH_PROVIDERS[provider]
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(config["userinfo_url"], headers=headers)
    response.raise_for_status()
    return response.json()

def get_or_create_user_from_social(provider, user_info):
    """Map provider user info -> Django user."""
    User = get_user_model()
    email = user_info.get("email")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": user_info.get("name") or email.split("@")[0],
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
        },
    )

    if created:
        # Email user after account creation
        send_mail(
            subject="Welcome to SecureBite",
            message=f"Hello {user.username}, your account has been created via {provider.capitalize()} login.",
            from_email="no-reply@securebite.com",
            recipient_list=[user.email],
            fail_silently=True,
        )
    return user, created

def get_or_create_user_from_social(provider, user_info):
    """Map provider user info -> Django user."""
    User = get_user_model()
    email = user_info.get("email")

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            "username": user_info.get("name") or email.split("@")[0],
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
        },
    )

    if created:
        user_account_created.send(sender=User, user=user, provider=provider)

    return user, created