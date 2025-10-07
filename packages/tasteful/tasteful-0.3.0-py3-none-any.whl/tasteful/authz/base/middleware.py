from abc import ABC, abstractmethod
from typing import Type

from fastapi import HTTPException, Request
from fastapi.security.base import SecurityBase
from tasteful.authn.base.user import BaseUser


class AuthorizationMiddleware(SecurityBase, ABC):
    @abstractmethod
    def authorize(self, request: Request, user: Type[BaseUser]) -> bool:
        """Check if user has enough right to perfom an action."""
        raise NotImplementedError()

    def __call__(self, request: Request) -> None:
        """Callable method."""
        # As this method is supposed to be "Provider Agnostic",
        # it only calls the authorize method, which returns a boolean.

        user: Type[BaseUser] | None = getattr(request.state, "user")

        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if self._is_public_route(request=request) and not user.authenticated:
            return

        is_authorized = self.authorize(request=request, user=user)

        if not is_authorized:
            raise HTTPException(status_code=403, detail="Forbidden")

    def _is_public_route(self, request: Request) -> bool:
        route = request.scope.get("route")

        return (
            route
            and hasattr(route.endpoint, "_is_public_route")
            and route.endpoint._is_public_route
        )


class AsyncAuthorizationMiddleware(SecurityBase, ABC):
    @abstractmethod
    async def authorize(self, request: Request, user: Type[BaseUser]) -> bool:
        """Check if user has enough right to perfom an action."""
        raise NotImplementedError()

    async def __call__(self, request: Request) -> None:
        """Callable method."""
        # As this method is supposed to be "Provider Agnostic",
        # it only calls the authorize method, which returns a boolean.

        user = getattr(request.state, "user")

        if not user:
            raise HTTPException(status_code=401, detail="Unauthorized")

        if self._is_public_route(request=request) and not user.authenticated:
            return

        is_authorized = await self.authorize(request=request, user=user)

        if not is_authorized:
            raise HTTPException(status_code=403, detail="Forbidden")

        return

    def _is_public_route(self, request: Request) -> bool:
        route = request.scope.get("route")

        return (
            route
            and hasattr(route.endpoint, "_is_public_route")
            and route.endpoint._is_public_route
        )
