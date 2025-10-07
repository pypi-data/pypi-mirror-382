from tasteful.authz.oidc.middleware import OIDCAuthorizationMiddleware


class ZitadelAuthorizationMiddleware(OIDCAuthorizationMiddleware):
    scheme_name = "ZitadelRole"

    def __init__(self) -> None:
        super().__init__(role_claims_key="urn:zitadel:iam:org:project:roles")
