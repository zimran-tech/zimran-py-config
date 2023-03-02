from enum import Enum
from typing import Literal

from pydantic import AnyUrl, BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


class CommonSettings(BaseSettings):
    debug: bool = False
    environment: Environment = Environment.DEVELOPMENT
    sentry_dsn: AnyUrl | None = None

    class Config:
        use_enum_values = True
