import requests
from urllib.parse import urlencode


class OAuth2Provider:
    """
    Generic OAuth2/OpenID Connect provider.
    Expects provider config (client_id, client_secret, auth_url, token_url, userinfo_url, scope, redirect_uri).
    """

    def __init__(
        self,
        name,
        client_id,
        client_secret,
        auth_url,
        token_url,
        userinfo_url,
        scope="",
        redirect_uri=None,
        extra_auth_params=None,
        token_headers=None,
        userinfo_method="GET",
    ):
        self.name = name
        self.client_id = client_id
        self.client_secret = client_secret
        self.auth_url = auth_url
        self.token_url = token_url
        self.userinfo_url = userinfo_url
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.extra_auth_params = extra_auth_params or {}
        # default Accept json to make GitHub / others return JSON
        self.token_headers = token_headers or {"Accept": "application/json"}
        self.userinfo_method = userinfo_method.upper()

    def get_authorization_url(self, redirect_uri=None, state=None):
        redirect_uri = redirect_uri or self.redirect_uri
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": self.scope,
            "state": state,
        }
        params.update(self.extra_auth_params or {})
        # remove None values
        params = {k: v for k, v in params.items() if v is not None}
        return f"{self.auth_url}?{urlencode(params)}"

    def exchange_code_for_token(self, code, redirect_uri=None):
        redirect_uri = redirect_uri or self.redirect_uri
        data = {
            "code": code,
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }
        resp = requests.post(self.token_url, data=data, headers=self.token_headers, timeout=10)
        # try JSON first, fallback to form-encoded text
        try:
            return resp.json()
        except ValueError:
            # fallback: parse form encoded body like "access_token=...&scope=..."
            pairs = [p.split("=", 1) for p in resp.text.split("&") if "=" in p]
            return {k: v for k, v in pairs}

    def get_user_info(self, access_token):
        headers = {"Authorization": f"Bearer {access_token}"}
        headers.update({k: v for k, v in (self.token_headers or {}).items() if k.lower() != "accept"})
        if self.userinfo_method == "GET":
            resp = requests.get(self.userinfo_url, headers=headers, timeout=10)
        else:
            resp = requests.post(self.userinfo_url, headers=headers, data={"access_token": access_token}, timeout=10)
        resp.raise_for_status()
        # Common userinfo endpoints return JSON
        return resp.json()
