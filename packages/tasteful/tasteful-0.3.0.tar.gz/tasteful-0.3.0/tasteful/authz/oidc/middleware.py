from fastapi import Request
from fastapi.security import OAuth2
from tasteful.authn.oidc.user import OIDCUser
from tasteful.authz.base.middleware import AsyncAuthorizationMiddleware


class OIDCAuthorizationMiddleware(AsyncAuthorizationMiddleware):
    # Looks like this attribute is mandatory
    model = OAuth2
    scheme_name = "OIDCScope"

    def __init__(self, role_claims_key: str = "") -> None:
        self.role_claims_key = role_claims_key

    async def authorize(self, request: Request, user: OIDCUser) -> bool:
        """Check if user has enough right to perfom an action."""
        route = request.scope.get("route")

        if route and hasattr(route.endpoint, "_required_permissions"):
            required_permissions = route.endpoint._required_permissions

            # If no required_permissions or empty array
            if not required_permissions:
                return True

            user_roles = user.claims.get(self.role_claims_key, {}).keys()

            # If the user has EVERY role that the decorator admits
            return all(role in user_roles for role in required_permissions)

        return False
