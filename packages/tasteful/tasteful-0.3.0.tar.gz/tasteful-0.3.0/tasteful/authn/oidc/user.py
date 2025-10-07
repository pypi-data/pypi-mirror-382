from pydantic import Field
from tasteful.authn.base import BaseUser


class OIDCUser(BaseUser):
    claims: dict = Field(default={})
