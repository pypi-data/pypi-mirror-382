from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)


class BaseConfig(BaseSettings):
    model_config = SettingsConfigDict(
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
    )
