from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from django.http import JsonResponse
from secure_bite.utils import clear_cookie, get_jwt_cookie_settings, get_simple_jwt_settings

cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()

class CookieJWTAuthentication(JWTAuthentication):
    """
    Custom JWT authentication that retrieves tokens from HTTP-only cookies
    and handles token rotation.
    """
    def authenticate(self, request):
        access_token = request.COOKIES.get(cookie_settings["AUTH_COOKIE"])
        refresh_token = request.COOKIES.get(cookie_settings["REFRESH_COOKIE"])

        #  No tokens at all > unauthenticated
        if not access_token and not refresh_token:
            return None

        #  Try validating the access token first
        if access_token:
            try:
                validated_token = self.get_validated_token(access_token)
                user = self.get_user(validated_token)
                return user, validated_token
            except (TokenError, AuthenticationFailed):
                # Token invalid or expired > fall back to refresh
                pass

        #  Try refreshing using the refresh token if available
        if refresh_token:
            try:
                new_access_token, new_refresh_token = self.refresh_tokens(refresh_token)
                response = JsonResponse({"message": "Tokens refreshed"}, status=200)
                self.set_access_cookie(response, new_access_token)
                self.set_refresh_cookie(response, new_refresh_token)
                user = self.get_user(AccessToken(new_access_token))
                return user, AccessToken(new_access_token)
            except AuthenticationFailed:
                return None

        #  Nothing worked > return None
        return None


    def refresh_tokens(self, refresh_token):
        """Attempt to refresh both the access token and the refresh token."""
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = str(refresh.access_token)
            new_refresh_token = str(refresh)
            return new_access_token, new_refresh_token
        except TokenError:
            raise AuthenticationFailed("Invalid refresh token. Please log in again.")


    def set_access_cookie(self, response, access_token):
        try:
            access_max_age = int(jwt_settings["ACCESS_TOKEN_LIFETIME"].total_seconds())
        except Exception:
            access_max_age = int(jwt_settings["ACCESS_TOKEN_LIFETIME"])

        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            access_token,
            max_age=access_max_age,
            httponly=cookie_settings["AUTH_COOKIE_HTTP_ONLY"],
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
            path=cookie_settings.get("AUTH_COOKIE_PATH", "/"),
        )

    def set_refresh_cookie(self, response, refresh_token):
        try:
            refresh_max_age = int(jwt_settings["REFRESH_TOKEN_LIFETIME"].total_seconds())
        except Exception:
            refresh_max_age = int(jwt_settings["REFRESH_TOKEN_LIFETIME"])

        response.set_cookie(
            cookie_settings["REFRESH_COOKIE"],
            refresh_token,
            max_age=refresh_max_age,
            httponly=cookie_settings["AUTH_COOKIE_HTTP_ONLY"],
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
            path=cookie_settings.get("AUTH_COOKIE_PATH", "/"),
        )


    def clear_auth_cookies(self, response):
        """Clear authentication cookies."""
        clear_cookie(response=response,name=cookie_settings["AUTH_COOKIE"])
        clear_cookie(response=response,name=cookie_settings["REFRESH_COOKIE"])