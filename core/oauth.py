"""OAuth 2.1 provider for DOPEHOUSE OPENMIC.

Implements the MCP SDK's OAuthAuthorizationServerProvider interface,
delegating user authentication to AceDataCloud's OAuth 2.0 Authorization Server.
"""

import base64
import hashlib
import json
import secrets
import time
from urllib.parse import urlencode

import httpx
from loguru import logger
from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    OAuthClientInformationFull,
    OAuthToken,
    RefreshToken,
)
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse

from core.client import set_request_api_token
from core.config import settings

MCP_ACCESS_SCOPE = "mcp:access"


def _normalize_scopes(scopes: list[str] | None) -> list[str]:
    return scopes or [MCP_ACCESS_SCOPE]


class AceDataCloudOAuthProvider:
    def __init__(self) -> None:
        self._clients: dict[str, OAuthClientInformationFull] = {}
        self._auth_codes: dict[str, tuple[AuthorizationCode, str]] = {}
        self._access_tokens: dict[str, AccessToken] = {}
        self._refresh_tokens: dict[str, RefreshToken] = {}
        self._pending_auth: dict[str, dict] = {}

    async def get_client(self, client_id: str) -> OAuthClientInformationFull | None:
        return self._clients.get(client_id)

    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        client_id = client_info.client_id
        assert client_id is not None
        self._clients[client_id] = client_info
        logger.info(f"Registered OAuth client: {client_id}")

    async def authorize(self, client: OAuthClientInformationFull, params: AuthorizationParams) -> str:
        mcp_state = secrets.token_urlsafe(32)
        code_verifier = secrets.token_urlsafe(48)
        digest = hashlib.sha256(code_verifier.encode("ascii")).digest()
        auth_code_challenge = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
        self._pending_auth[mcp_state] = {
            "client_id": client.client_id,
            "redirect_uri": str(params.redirect_uri),
            "state": params.state,
            "code_challenge": params.code_challenge,
            "redirect_uri_provided_explicitly": params.redirect_uri_provided_explicitly,
            "scopes": _normalize_scopes(params.scopes),
            "resource": params.resource,
            "auth_code_verifier": code_verifier,
        }
        callback_url = f"{settings.server_url}/oauth/callback"
        auth_params = {
            "client_id": settings.oauth_client_id,
            "redirect_uri": callback_url,
            "response_type": "code",
            "scope": "profile platform",
            "state": mcp_state,
            "code_challenge": auth_code_challenge,
            "code_challenge_method": "S256",
        }
        auth_url = f"{settings.auth_base_url}/oauth2/authorize?{urlencode(auth_params)}"
        logger.info(f"OAuth authorize: redirecting to consent page (mcp_state={mcp_state})")
        return auth_url

    async def handle_callback(self, request: Request) -> RedirectResponse | JSONResponse:
        mcp_state = request.query_params.get("state")
        adc_code = request.query_params.get("code")
        if not mcp_state or not adc_code:
            return JSONResponse({"error": "Missing state or code parameter"}, status_code=400)
        pending = self._pending_auth.pop(mcp_state, None)
        if not pending:
            return JSONResponse({"error": "Invalid or expired state"}, status_code=400)
        try:
            code_verifier = pending.get("auth_code_verifier", "")
            jwt_token = await self._exchange_code_for_jwt(adc_code, code_verifier)
            if not jwt_token:
                return JSONResponse({"error": "Failed to exchange authorization code"}, status_code=502)
            api_token = await self._get_user_credential(jwt_token)
            if not api_token:
                return JSONResponse(
                    {"error": "No API credential found. Please create an API key at https://platform.acedata.cloud first."},
                    status_code=403,
                )
            auth_code_str = secrets.token_urlsafe(48)
            auth_code = AuthorizationCode(
                code=auth_code_str,
                scopes=_normalize_scopes(pending.get("scopes")),
                expires_at=time.time() + 600,
                client_id=pending["client_id"],
                code_challenge=pending["code_challenge"],
                redirect_uri=pending["redirect_uri"],
                redirect_uri_provided_explicitly=pending["redirect_uri_provided_explicitly"],
                resource=pending.get("resource"),
            )
            self._auth_codes[auth_code_str] = (auth_code, api_token)
            redirect_uri = pending["redirect_uri"]
            params = {"code": auth_code_str}
            if pending.get("state"):
                params["state"] = pending["state"]
            separator = "&" if "?" in redirect_uri else "?"
            redirect_url = f"{redirect_uri}{separator}{urlencode(params)}"
            logger.info("OAuth callback: issuing auth code, redirecting to client")
            return RedirectResponse(url=redirect_url, status_code=302)
        except Exception:
            logger.exception("OAuth callback error")
            return JSONResponse({"error": "Internal server error"}, status_code=500)

    async def load_authorization_code(self, client: OAuthClientInformationFull, authorization_code: str) -> AuthorizationCode | None:
        data = self._auth_codes.get(authorization_code)
        if not data:
            return None
        auth_code, _ = data
        if auth_code.expires_at < time.time():
            self._auth_codes.pop(authorization_code, None)
            return None
        return auth_code

    async def exchange_authorization_code(self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode) -> OAuthToken:
        data = self._auth_codes.pop(authorization_code.code, None)
        if not data:
            raise ValueError("Authorization code not found or already used")
        _, api_token = data
        client_id = client.client_id or ""
        self._access_tokens[api_token] = AccessToken(
            token=api_token,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
            expires_at=None,
        )
        refresh_token_str = secrets.token_urlsafe(48)
        self._refresh_tokens[refresh_token_str] = RefreshToken(
            token=refresh_token_str,
            client_id=client_id,
            scopes=_normalize_scopes(authorization_code.scopes),
        )
        logger.info(f"OAuth token exchange: issued access token for client {client_id}")
        return OAuthToken(
            access_token=api_token,
            token_type="Bearer",
            scope=" ".join(_normalize_scopes(authorization_code.scopes)),
            refresh_token=refresh_token_str,
        )

    async def load_refresh_token(self, client: OAuthClientInformationFull, refresh_token: str) -> RefreshToken | None:
        return self._refresh_tokens.get(refresh_token)

    async def exchange_refresh_token(self, client: OAuthClientInformationFull, refresh_token: RefreshToken, scopes: list[str]) -> OAuthToken:
        self._refresh_tokens.pop(refresh_token.token, None)
        client_id = client.client_id or ""
        new_refresh = secrets.token_urlsafe(48)
        self._refresh_tokens[new_refresh] = RefreshToken(
            token=new_refresh,
            client_id=client_id,
            scopes=_normalize_scopes(scopes or refresh_token.scopes),
        )
        for token, at in self._access_tokens.items():
            if at.client_id == client.client_id:
                return OAuthToken(
                    access_token=token,
                    token_type="Bearer",
                    scope=" ".join(_normalize_scopes(scopes or refresh_token.scopes)),
                    refresh_token=new_refresh,
                )
        raise ValueError("No access token found for refresh")

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token in self._access_tokens:
            access_token = self._access_tokens[token]
            if access_token.expires_at and time.time() > access_token.expires_at:
                self._access_tokens.pop(token, None)
                return None
            set_request_api_token(token)
            return access_token
        set_request_api_token(token)
        return AccessToken(token=token, client_id="direct", scopes=[MCP_ACCESS_SCOPE])

    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            self._access_tokens.pop(token.token, None)
        elif isinstance(token, RefreshToken):
            self._refresh_tokens.pop(token.token, None)
        logger.info(f"Revoked token: {token.token[:8]}...")

    @staticmethod
    def _decode_jwt_payload(token: str) -> dict | None:
        try:
            parts = token.split(".")
            if len(parts) != 3:
                return None
            payload_b64 = parts[1]
            padding = 4 - len(payload_b64) % 4
            if padding != 4:
                payload_b64 += "=" * padding
            return json.loads(base64.urlsafe_b64decode(payload_b64))
        except Exception:
            return None

    async def _exchange_code_for_jwt(self, code: str, code_verifier: str) -> str | None:
        callback_url = f"{settings.server_url}/oauth/callback"
        token_url = f"{settings.auth_base_url}/oauth2/token"
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(
                    token_url,
                    data={
                        "grant_type": "authorization_code",
                        "code": code,
                        "client_id": settings.oauth_client_id,
                        "redirect_uri": callback_url,
                        "code_verifier": code_verifier,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("access_token")
                logger.error(f"OAuth token exchange failed: {response.status_code} {response.text}")
        except Exception:
            logger.exception("OAuth token exchange error")
        return None

    async def _get_user_credential(self, jwt_token: str) -> str | None:
        headers = {"Authorization": f"Bearer {jwt_token}"}
        claims = self._decode_jwt_payload(jwt_token)
        user_id = claims.get("user_id") if claims else None
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                creds_url = f"{settings.platform_base_url}/api/v1/credentials/"
                creds_params = {"user_id": user_id} if user_id else {}
                response = await client.get(creds_url, headers=headers, params=creds_params)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", data) if isinstance(data, dict) else data
                    if isinstance(results, list):
                        for cred in results:
                            cred_token = cred.get("token")
                            if cred_token:
                                return cred_token
                logger.info("No credentials found, auto-provisioning")
                apps_url = f"{settings.platform_base_url}/api/v1/applications/"
                apps_params = {"limit": "10", "ordering": "-created_at", "type": "Usage", "scope": "Global"}
                if user_id:
                    apps_params["user_id"] = user_id
                app_resp = await client.get(apps_url, params=apps_params, headers=headers)
                application_id = None
                if app_resp.status_code == 200:
                    app_data = app_resp.json()
                    items = app_data.get("items", app_data.get("results", []))
                    if isinstance(items, list) and items:
                        app = items[0]
                        application_id = app.get("id")
                        app_creds = app.get("credentials", [])
                        if isinstance(app_creds, list) and app_creds:
                            existing_token = app_creds[0].get("token")
                            if isinstance(existing_token, str) and existing_token:
                                return existing_token
                if not application_id:
                    create_payload = {"type": "Usage", "scope": "Global"}
                    create_app_resp = await client.post(apps_url, headers={**headers, "Content-Type": "application/json"}, json=create_payload)
                    if create_app_resp.status_code in (200, 201):
                        application_id = create_app_resp.json().get("id")
                if application_id:
                    cred_create_url = f"{settings.platform_base_url}/api/v1/credentials/"
                    cred_resp = await client.post(cred_create_url, headers={**headers, "Content-Type": "application/json"}, json={"application_id": application_id})
                    if cred_resp.status_code in (200, 201):
                        cred_data = cred_resp.json()
                        new_token = cred_data.get("token") if isinstance(cred_data, dict) else None
                        if isinstance(new_token, str) and new_token:
                            return new_token
        except Exception:
            logger.exception("Credential fetch/provision error")
        return None
