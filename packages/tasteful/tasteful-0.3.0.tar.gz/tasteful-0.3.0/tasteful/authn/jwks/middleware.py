from typing import Optional, Union

import requests

from fastapi import Request
from fastapi.security import HTTPBearer
from joserfc import (
    errors as jose_errors,
    jwt,
)
from joserfc.jwk import KeySet
from tasteful.authn.base import AsyncAuthenticationMiddleware

from .user import JWKSUser


class JWKSAuthenticationMiddleware(AsyncAuthenticationMiddleware, HTTPBearer):
    """Middleware for JWT auth with any OIDC provider publishing JWKS.

    Works with AWS Cognito, Auth0, Keycloak, ZITADEL, etc.
    """

    def __init__(
        self, jwks_url: str, issuer: Optional[str] = None, client_id: Optional[str] = None
    ):
        super().__init__()
        self.jwks_url = jwks_url
        self.issuer = issuer
        self.client_id = client_id
        self.key_set = self._fetch_jwks()

    def _fetch_jwks(self) -> KeySet:
        """Fetch JWKS and build a KeySet."""
        resp = requests.get(self.jwks_url, timeout=5)
        resp.raise_for_status()
        data = resp.json()

        # Keep only usable signature or encryption keys
        valid_keys = [k for k in data.get("keys", []) if k.get("use") in {"sig", "enc"}]
        if not valid_keys:
            raise RuntimeError("No usable signature or encryption keys found in JWKS")

        return KeySet.import_key_set({"keys": valid_keys})

    async def authenticate(self, request: Request) -> Union[JWKSUser, None]:
        """Return a JWKSUser if valid token, None otherwise."""
        token = self._extract_token(request)
        if not token:
            return None

        for attempt in range(2):
            user = self._decode_and_validate_token(token)
            if user:
                return user
            if attempt == 0:
                self.key_set = self._fetch_jwks()

        return None

    def _extract_token(self, request: Request) -> Optional[str]:
        """Extract the Bearer token from the Authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None

        scheme, token = auth_header.split(" ", 1)
        if scheme.lower() == "bearer":
            return token

        return None

    def _decode_and_validate_token(self, token: str) -> Optional[JWKSUser]:
        """Decode the token and validate its claims."""
        try:
            token_obj = jwt.decode(token, self.key_set)
            claims = token_obj.claims

            if self.issuer and claims.get("iss") != self.issuer:
                return None

            if self.client_id and claims.get("client_id") != self.client_id:
                return None

            return JWKSUser(
                claims=claims,
                name=claims.get("username") or claims.get("sub"),
                authenticated=True,
            )
        except jose_errors.InvalidClaimError:
            return None
        except (
            jose_errors.ExpiredTokenError,
            jose_errors.BadSignatureError,
            jose_errors.JoseError,
            RuntimeError,
        ):
            return None
