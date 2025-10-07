from pydantic import BaseModel, Field


class BaseUser(BaseModel):
    name: str = Field(default="anonymous")
    authenticated: bool = Field(default=False)
