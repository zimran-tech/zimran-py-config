from enum import StrEnum
from functools import cached_property
from typing import Any, Literal

from pydantic import BaseModel, Field

__all__ = ['DEFAULT_LOCALES', 'LocaleMetadata', 'LocaleConfig']

DEFAULT_LOCALES: frozenset[str] = frozenset({'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'fil', 'id'})


class LocaleMetadata(BaseModel):
    code: str
    display_name: str = Field(alias='displayName')
    native_name: str = Field(alias='nativeName')
    direction: Literal['ltr', 'rtl'] = 'ltr'
    fallback: str | None = None

    model_config = {'populate_by_name': True}

    @property
    def is_rtl(self) -> bool:
        return self.direction == 'rtl'


class LocaleConfig(BaseModel):
    default_locale: str = Field(alias='defaultLocale', default='en')
    locales: dict[str, LocaleMetadata]

    model_config = {'populate_by_name': True}

    @cached_property
    def supported_codes(self) -> frozenset[str]:
        return frozenset(self.locales.keys())

    @cached_property
    def rtl_codes(self) -> frozenset[str]:
        return frozenset(code for code, meta in self.locales.items() if meta.is_rtl)

    def get_enum(self) -> Any:
        return StrEnum('Locale', {c.upper(): c for c in self.supported_codes})

    def get(self, code: str) -> LocaleMetadata | None:
        return self.locales.get(code.lower())

    def get_or_default(self, code: str) -> LocaleMetadata:
        return self.locales.get(code.lower()) or self.locales[self.default_locale]

    def is_supported(self, code: str) -> bool:
        return code.lower() in self.supported_codes
