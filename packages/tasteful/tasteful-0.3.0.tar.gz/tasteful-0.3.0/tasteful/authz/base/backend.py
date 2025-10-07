from tasteful.authz.base.middleware import (
    AsyncAuthorizationMiddleware,
    AuthorizationMiddleware,
)


# TODO: Remove in next release (0.4.0 ?)
AsyncAuthorizationBackend = AsyncAuthorizationMiddleware
AuthorizationBackend = AuthorizationMiddleware
