from enum import Enum

from pydantic import AnyUrl, BaseSettings


class Environment(str, Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


class CommonSettings(BaseSettings):
    debug: bool = False
    environment: Environment = Environment.DEVELOPMENT
    sentry_dsn: AnyUrl = None
