from tasteful.authn.base.middleware import (
    AsyncAuthenticationMiddleware,
    AuthenticationMiddleware,
)


## TODO: Destroy in next release (0.4.0 ?)
AsyncAuthenticationBackend = AsyncAuthenticationMiddleware
AuthenticationBackend = AuthenticationMiddleware
