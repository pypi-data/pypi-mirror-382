from typing import Union

from authlib.integrations.starlette_client import OAuth
from fastapi import Request
from fastapi.security import HTTPBearer
from httpx import HTTPError
from pydantic import ValidationError
from tasteful.authn.base import AsyncAuthenticationMiddleware

from .user import OIDCUser


class OIDCAuthenticationMiddleware(AsyncAuthenticationMiddleware, HTTPBearer):
    metatada: dict

    def __init__(
        self,
        name: str = "oidc_app",
        metadata_url: str = "",
        client_id: str = "",
        client_secret: str = "",
        scopes: str = "",
        introspection_endpoint: str = "",
    ):
        super().__init__()

        self.name = name
        self.metadata_url = metadata_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scopes = scopes
        self.introspection_endpoint = introspection_endpoint

        self.oauth = OAuth()
        self.oauth.register(
            self.name,
            client_id=self.client_id,
            client_secret=self.client_secret,
            server_metadata_url=self.metadata_url,
            introspection_endpoint=self.introspection_endpoint,
            client_kwargs={"scope": self.scopes},
        )

        self.client = self.oauth.create_client(self.name)

    async def authenticate(self, request: Request) -> Union[OIDCUser, None]:
        """Authenticate the user depending on the token in the request headers."""
        authorization = request.headers.get("Authorization")

        if not authorization:
            return None

        else:
            scheme, token = authorization.split(" ")

            # This method calls the OIDC Backend (zitadel for example)
            # to authenticate the user
            user = await self._validate_token((token))
            return user

    async def _validate_token(self, token: str) -> Union[OIDCUser, None]:
        """Return the user info from the backend API."""
        try:
            if not self.introspection_endpoint:
                metadata = await self.client.load_server_metadata()
                self.introspection_endpoint = metadata.get("introspection_endpoint", "")

            result = (
                await self.client._get_oauth_client().introspect_token(
                    url=self.introspection_endpoint,
                    token=token,
                )
            ).json()

            if result.get("active", False):
                try:
                    return OIDCUser(
                        claims=result, name=result.get("name"), authenticated=True
                    )
                except ValidationError as e:
                    print(f"Validation Error: {e}")

        except HTTPError as e:
            print("Error happened when trying to call OIDC apps", e)
            return None

        return None
