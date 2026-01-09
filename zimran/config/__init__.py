import json
from enum import Enum

from pydantic import AnyUrl, computed_field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from zimran.config.locale import DEFAULT_LOCALES, LocaleConfig, LocaleMetadata

__version__ = '1.2.0'
__all__ = [
    'Environment',
    'CommonSettings',
    'LocaleConfig',
    'LocaleMetadata',
    'DEFAULT_LOCALES',
    '__version__',
]


class Environment(str, Enum):
    DEVELOPMENT = 'development'
    STAGING = 'staging'
    PRODUCTION = 'production'


class CommonSettings(BaseSettings):
    model_config = SettingsConfigDict(
        use_enum_values=True,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    debug: bool = False
    environment: Environment = Environment.DEVELOPMENT
    sentry_dsn: AnyUrl | None = None
    log_level: str = 'INFO'

    locale_config: LocaleConfig | None = None
    enabled_locales: frozenset[str] | None = None

    @field_validator('locale_config', mode='before')
    @classmethod
    def parse_locale_config(cls, v: str | dict | None) -> dict | None:
        if isinstance(v, str):
            return json.loads(v)  # type: ignore[no-any-return]

        return v

    @field_validator('enabled_locales', mode='before')
    @classmethod
    def parse_enabled_locales(cls, v: str | set | frozenset | None) -> frozenset[str] | None:
        if isinstance(v, str):
            return frozenset(x.strip() for x in v.split(',') if x.strip())

        if isinstance(v, set):
            return frozenset(v)

        return v

    def get_supported_locales(self) -> frozenset[str]:
        if self.locale_config is None:
            base = DEFAULT_LOCALES

        else:
            base = self.locale_config.supported_codes

        if self.enabled_locales:
            return base & self.enabled_locales

        return base

    @computed_field
    @property
    def is_production(self) -> bool:
        return self.environment == Environment.PRODUCTION

    @computed_field
    @property
    def is_development(self) -> bool:
        return self.environment == Environment.DEVELOPMENT

    @computed_field
    @property
    def is_staging(self) -> bool:
        return self.environment == Environment.STAGING
