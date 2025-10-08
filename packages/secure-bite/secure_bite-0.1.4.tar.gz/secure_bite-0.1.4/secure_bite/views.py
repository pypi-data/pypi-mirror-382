from django.contrib.auth import authenticate, get_user_model
from django.shortcuts import redirect
from django.utils.module_loading import import_string
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from secure_bite.authentication import CookieJWTAuthentication
from secure_bite.utils import (
    exchange_code_for_token,
    get_user_info,
    get_jwt_cookie_settings,
    get_simple_jwt_settings,
    get_or_create_user_from_social,
    clear_cookie,
    _seconds,
    populate_user_fields,
)
from secure_bite.provider_registry import ProviderRegistry
from django.core.signing import dumps, loads, BadSignature
from secure_bite.models import SocialAccount
from secure_bite import defaults


cookie_settings = get_jwt_cookie_settings()
jwt_settings = get_simple_jwt_settings()


class AuthenticationViewset(ViewSet):
    authentication_classes = [CookieJWTAuthentication]
    permission_classes = (IsAuthenticated,)
    serializer_class = import_string(cookie_settings["USER_SERIALIZER"])

    PUBLIC_ACTIONS = ["login", "oauth_start", "oauth_callback", "social_login"]

    def get_permissions(self):
        public_actions = ("login", "oauth_start", "oauth_callback", "social_login")
        if getattr(self, "action", None) in public_actions:
            self.permission_classes = (AllowAny,)
        else:
            self.permission_classes = (IsAuthenticated,)
        return super().get_permissions()

    def get_authenticators(self):
        """Skip authentication for public endpoints like OAuth start/callback"""
        if getattr(self, "action", None) in self.PUBLIC_ACTIONS:
            return []
        return super().get_authenticators()

    # ---------------------------
    # Authentication endpoints
    # ---------------------------
    @action(methods=["POST"], detail=False)
    def login(self, request, *args, **kwargs):
        """Authenticates the user using the dynamic username field and password and sets JWT tokens in cookies."""
        if request.user and request.user.is_authenticated:
            return Response({"message": "Already authenticated"}, status=status.HTTP_200_OK)
        User = get_user_model()
        username_field = User.USERNAME_FIELD
        identifier = request.data.get(username_field)
        password = request.data.get("password")

        if not identifier or not password:
            return Response({"error": f"Both '{username_field}' and 'password' are required."}, status=400)

        user = authenticate(**{username_field: identifier, "password": password})
        if user is None:
            return Response({"error": "Invalid credentials"}, status=401)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({"message": "Login successful"})

        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            access_token,
            max_age=_seconds(jwt_settings["ACCESS_TOKEN_LIFETIME"]),
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )
        response.set_cookie(
            cookie_settings["REFRESH_COOKIE"],
            refresh_token,
            max_age=_seconds(jwt_settings["REFRESH_TOKEN_LIFETIME"]),
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

        return response

    @action(methods=["POST"], detail=False)
    def logout(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get(cookie_settings["REFRESH_COOKIE"])
        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

        response = Response({"message": "Logged out"}, status=status.HTTP_200_OK)
        clear_cookie(response, name=cookie_settings["AUTH_COOKIE"])
        clear_cookie(response, name=cookie_settings["REFRESH_COOKIE"])
        return response

    @action(methods=["GET"], detail=False)
    def me(self, request, *args, **kwargs):
        serializer = self.serializer_class(request.user)
        data = serializer.data.copy()
        data.pop("access", None)
        data.pop("refresh", None)
        return Response(data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def auth_check(self, request, *args, **kwargs):
        return Response({"message": "You are authenticated"}, status=status.HTTP_200_OK)

    # ---------------------------
    # OAuth2 endpoints
    # ---------------------------
    @action(methods=["GET"], detail=False, permission_classes=[AllowAny])
    def oauth_start(self, request, *args, **kwargs):
        provider_name = request.query_params.get("provider")
        next_url = request.query_params.get("next") or request.query_params.get("redirect_uri")

        if not provider_name:
            return Response({"error": "Missing 'provider' query param."}, status=400)

        try:
            provider = ProviderRegistry.get(provider_name)
        except KeyError:
            return Response({"error": f"Provider '{provider_name}' is not configured."}, status=400)

        if not provider.redirect_uri:
            return Response({"error": "Provider missing 'redirect_uri' in settings."}, status=400)

        state = dumps({"provider": provider_name, "next": next_url})
        auth_url = provider.get_authorization_url(redirect_uri=provider.redirect_uri, state=state)
        return Response({"auth_url": auth_url}, status=200)

    @action(methods=["GET"], detail=False, permission_classes=[AllowAny])
    def oauth_callback(self, request, *args, **kwargs):
        provider_name = request.query_params.get("provider")
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        if not provider_name or not code:
            return Response({"error": "Missing 'provider' or 'code'."}, status=400)

        try:
            provider = ProviderRegistry.get(provider_name)
        except KeyError:
            return Response({"error": f"Provider '{provider_name}' is not configured."}, status=400)

        try:
            state_data = loads(state)
        except BadSignature:
            return Response({"error": "Invalid or tampered 'state'."}, status=400)

        if state_data.get("provider") != provider_name:
            return Response({"error": "State provider mismatch."}, status=400)

        try:
            tokens = provider.exchange_code_for_token(code, redirect_uri=provider.redirect_uri)
        except Exception as exc:
            return Response({"error": f"Failed to exchange code: {str(exc)}"}, status=400)

        access_token = tokens.get("access_token") or tokens.get("id_token")
        if not access_token:
            return Response({"error": "No access token returned."}, status=400)

        try:
            user_info = provider.get_user_info(access_token)
        except Exception as exc:
            return Response({"error": f"Failed to fetch user info: {str(exc)}"}, status=400)

        User = get_user_model()
        provider_user_id = user_info.get("sub") or user_info.get("id") or user_info.get("node_id") or user_info.get("user_id")
        user = None

        if provider_user_id:
            sa = SocialAccount.objects.filter(provider=provider_name, provider_id=str(provider_user_id)).select_related("user").first()
            if sa:
                user = sa.user

        if user is None and user_info.get("email"):
            user = User.objects.filter(email__iexact=user_info["email"]).first()

        if user is None:
            username_field = User.USERNAME_FIELD
            create_kwargs = {}
            if username_field == "email" and user_info.get("email"):
                create_kwargs["email"] = user_info["email"]
            else:
                create_kwargs[username_field] = user_info.get("email") or f"{provider_name}_{provider_user_id or ''}"

            user = User.objects.create_user(**create_kwargs)
            user.set_unusable_password()
            user = populate_user_fields(user, user_info, provider_name)
            user.save()

            try:
                SocialAccount.objects.create(
                    user=user, provider=provider_name, provider_id=str(provider_user_id or ""), extra_data=user_info
                )
            except Exception:
                pass

        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        refresh_token = str(refresh)

        next_url = state_data.get("next") or "/"
        response = redirect(next_url)
        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            access,
            max_age=_seconds(jwt_settings["ACCESS_TOKEN_LIFETIME"]),
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )
        response.set_cookie(
            cookie_settings["REFRESH_COOKIE"],
            refresh_token,
            max_age=_seconds(jwt_settings["REFRESH_TOKEN_LIFETIME"]),
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

        return response

    @action(methods=["POST"], detail=False, permission_classes=[AllowAny])
    def social_login(self, request, *args, **kwargs):
        provider = request.data.get("provider")
        code = request.data.get("code")

        if not provider or provider not in getattr(defaults, "SECURE_BITE_PROVIDERS", {}):
            return Response({"error": "Unsupported or missing provider"}, status=400)
        if not code:
            return Response({"error": "Authorization code required"}, status=400)

        token_data = exchange_code_for_token(provider, code)
        access_token = token_data.get("access_token")
        user_info = get_user_info(provider, access_token)
        user, created = get_or_create_user_from_social(provider, user_info)

        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)

        response = Response({"message": f"Login with {provider} successful"})
        response.set_cookie(
            cookie_settings["AUTH_COOKIE"],
            access_token,
            max_age=_seconds(jwt_settings["ACCESS_TOKEN_LIFETIME"]),
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )
        response.set_cookie(
            cookie_settings["REFRESH_COOKIE"],
            refresh_token,
            max_age=_seconds(jwt_settings["REFRESH_TOKEN_LIFETIME"]),
            httponly=True,
            secure=cookie_settings["AUTH_COOKIE_SECURE"],
            samesite=cookie_settings["AUTH_COOKIE_SAMESITE"],
        )

        return response
