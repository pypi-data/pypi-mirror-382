from pydantic import Field
from tasteful.authn.base import BaseUser


class JWKSUser(BaseUser):
    claims: dict = Field(default={})
