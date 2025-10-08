from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
import logging
from secure_bite.utils import get_jwt_cookie_settings, get_simple_jwt_settings

logger = logging.getLogger(__name__)

cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()


class RefreshTokenMiddleware(MiddlewareMixin):
    """Middleware to automatically refresh JWT tokens when expired."""

    def process_request(self, request):
        request.new_access_token = None

        refresh_token = request.COOKIES.get(cookie_settings["REFRESH_COOKIE"])
        if not refresh_token:
            return None

        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)

            # Store the new token to be set in the response
            request.new_access_token = new_access_token
        except TokenError:
            logger.warning("Invalid or expired refresh token.")
            request.new_access_token = None

    def process_response(self, request, response):
        """If a new token was generated, set it in cookies — but don't overwrite deletion cookies."""
        # Only proceed if created a new access token in process_request
        new_token = getattr(request, "new_access_token", None)
        if not new_token:
            return response

        # If the response has already instructed deletion for the auth cookie, do not overwrite it.
        existing = response.cookies.get(cookie_settings["AUTH_COOKIE"])
        if existing:
            # If cookie marked for deletion, skip adding the new cookie
            # Morsel stores max-age as a string; check for "0" or an expiry in the past marker
            if existing.get("max-age") == "0" or (
                existing.get("expires") and "1970" in existing.get("expires")
            ):
                return response

        # Convert lifetimes to seconds if they are timedelta
        try:
            access_max_age = int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds())
        except Exception:
            access_max_age = int(jwt_settings["ACCESS_TOKEN_LIFETIME"])

        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            new_token,
            max_age=access_max_age,
            httponly=cookie_settings["AUTH_COOKIE_HTTP_ONLY"],
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
            path=cookie_settings.get("AUTH_COOKIE_PATH", "/"),
        )
        return response
