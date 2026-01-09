import json
from os import environ

from pytest_mock import MockerFixture

from zimran.config import DEFAULT_LOCALES, CommonSettings, LocaleConfig, LocaleMetadata

SAMPLE_LOCALE_CONFIG = {
    'defaultLocale': 'en',
    'locales': {
        'en': {
            'code': 'en',
            'displayName': 'English',
            'nativeName': 'English',
            'direction': 'ltr',
            'fallback': None,
        },
        'es': {
            'code': 'es',
            'displayName': 'Spanish',
            'nativeName': 'Español',
            'direction': 'ltr',
            'fallback': 'en',
        },
        'ar': {
            'code': 'ar',
            'displayName': 'Arabic',
            'nativeName': 'العربية',
            'direction': 'rtl',
            'fallback': 'en',
        },
    },
}


def test_locale_metadata_create_with_alias() -> None:
    meta = LocaleMetadata(code='en', displayName='English', nativeName='English')

    assert meta.code == 'en'
    assert meta.display_name == 'English'
    assert meta.native_name == 'English'
    assert meta.direction == 'ltr'
    assert meta.fallback is None


def test_locale_metadata_create_with_field_names() -> None:
    meta = LocaleMetadata(
        code='es', display_name='Spanish', native_name='Español', direction='ltr', fallback='en'
    )

    assert meta.code == 'es'
    assert meta.display_name == 'Spanish'


def test_locale_metadata_is_rtl_false() -> None:
    meta = LocaleMetadata(code='en', displayName='English', nativeName='English', direction='ltr')

    assert meta.is_rtl is False


def test_locale_metadata_is_rtl_true() -> None:
    meta = LocaleMetadata(code='ar', displayName='Arabic', nativeName='العربية', direction='rtl')

    assert meta.is_rtl is True


def test_locale_config_create_from_dict() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    assert config.default_locale == 'en'
    assert len(config.locales) == 3


def test_locale_config_supported_codes() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    assert config.supported_codes == frozenset({'en', 'es', 'ar'})


def test_locale_config_rtl_codes() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    assert config.rtl_codes == frozenset({'ar'})


def test_locale_config_get_enum() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    locale_enum = config.get_enum()
    assert locale_enum.EN == 'en'
    assert locale_enum.ES == 'es'
    assert locale_enum.AR == 'ar'


def test_locale_config_get_existing() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    meta = config.get('en')
    assert meta is not None
    assert meta.code == 'en'


def test_locale_config_get_nonexistent() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    meta = config.get('fr')
    assert meta is None


def test_locale_config_get_case_insensitive() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    meta = config.get('EN')
    assert meta is not None
    assert meta.code == 'en'


def test_locale_config_get_or_default() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    meta = config.get_or_default('fr')
    assert meta.code == 'en'


def test_locale_config_is_supported() -> None:
    config = LocaleConfig(**SAMPLE_LOCALE_CONFIG)

    assert config.is_supported('en') is True
    assert config.is_supported('fr') is False
    assert config.is_supported('EN') is True


def test_settings_locale_config_none_by_default(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.locale_config is None


def test_settings_locale_config_from_json_string(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'LOCALE_CONFIG': json.dumps(SAMPLE_LOCALE_CONFIG)}, clear=True)

    settings = CommonSettings()
    assert settings.locale_config is not None
    assert settings.locale_config.default_locale == 'en'
    assert len(settings.locale_config.locales) == 3


def test_settings_locale_config_from_dict(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings(locale_config=SAMPLE_LOCALE_CONFIG)
    assert settings.locale_config is not None
    assert settings.locale_config.default_locale == 'en'


def test_settings_locale_config_validator_with_string() -> None:
    result = CommonSettings.parse_locale_config(json.dumps(SAMPLE_LOCALE_CONFIG))

    assert isinstance(result, dict)
    assert result['defaultLocale'] == 'en'


def test_settings_enabled_locales_none_by_default(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.enabled_locales is None


def test_settings_enabled_locales_from_comma_string(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENABLED_LOCALES': 'en, es, fr'}, clear=True)

    settings = CommonSettings()
    assert settings.enabled_locales == frozenset({'en', 'es', 'fr'})


def test_settings_enabled_locales_from_set(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings(enabled_locales={'en', 'es'})
    assert settings.enabled_locales == frozenset({'en', 'es'})


def test_settings_enabled_locales_strips_whitespace(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENABLED_LOCALES': '  en  ,  es  '}, clear=True)

    settings = CommonSettings()
    assert settings.enabled_locales == frozenset({'en', 'es'})


def test_settings_enabled_locales_ignores_empty(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENABLED_LOCALES': 'en,,es,'}, clear=True)

    settings = CommonSettings()
    assert settings.enabled_locales == frozenset({'en', 'es'})


def test_get_supported_locales_default(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.get_supported_locales() == DEFAULT_LOCALES


def test_get_supported_locales_from_config(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'LOCALE_CONFIG': json.dumps(SAMPLE_LOCALE_CONFIG)}, clear=True)

    settings = CommonSettings()
    assert settings.get_supported_locales() == frozenset({'en', 'es', 'ar'})


def test_get_supported_locales_filtered(mocker: MockerFixture) -> None:
    mocker.patch.dict(
        environ,
        {
            'LOCALE_CONFIG': json.dumps(SAMPLE_LOCALE_CONFIG),
            'ENABLED_LOCALES': 'en,es',
        },
        clear=True,
    )
    settings = CommonSettings()
    assert settings.get_supported_locales() == frozenset({'en', 'es'})


def test_get_supported_locales_filtered_default(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENABLED_LOCALES': 'en,es,fr'}, clear=True)

    settings = CommonSettings()
    result = settings.get_supported_locales()
    assert result == frozenset({'en', 'es', 'fr'})


def test_default_locales_content() -> None:
    assert 'en' in DEFAULT_LOCALES
    assert 'es' in DEFAULT_LOCALES
    assert 'fr' in DEFAULT_LOCALES
    assert 'de' in DEFAULT_LOCALES
    assert 'it' in DEFAULT_LOCALES
    assert 'pt' in DEFAULT_LOCALES
    assert 'ja' in DEFAULT_LOCALES
    assert 'fil' in DEFAULT_LOCALES
    assert 'id' in DEFAULT_LOCALES


def test_default_locales_is_frozenset() -> None:
    assert isinstance(DEFAULT_LOCALES, frozenset)


def test_locale_exports() -> None:
    from zimran import config

    assert 'LocaleConfig' in config.__all__
    assert 'LocaleMetadata' in config.__all__
    assert 'DEFAULT_LOCALES' in config.__all__
