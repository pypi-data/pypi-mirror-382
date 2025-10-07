from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SentryConfig(BaseSettings):
    SENTRY_ENABLE: bool = Field(default=False)
    SENTRY_DNS: str = Field(default="")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


sentry_config = SentryConfig()
