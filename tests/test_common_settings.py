from os import environ

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from zimran.config import CommonSettings, Environment

SENTRY_DSN = 'https://public@sentry.example.com/1'


def test_sentry_dsn_valid(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'SENTRY_DSN': SENTRY_DSN})

    settings = CommonSettings()
    assert str(settings.sentry_dsn) == SENTRY_DSN


def test_sentry_dsn_none_by_default(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.sentry_dsn is None


@pytest.mark.parametrize(
    'env_value',
    [
        Environment.DEVELOPMENT,
        Environment.STAGING,
        Environment.PRODUCTION,
    ],
)
def test_environment_valid(mocker: MockerFixture, env_value: Environment) -> None:
    mocker.patch.dict(environ, {'ENVIRONMENT': env_value.value})

    settings = CommonSettings()
    assert settings.environment == env_value.value


def test_environment_invalid(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENVIRONMENT': 'invalid'})

    with pytest.raises(ValidationError):
        CommonSettings()


def test_environment_default_development(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.environment == Environment.DEVELOPMENT.value


def test_is_production_true(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENVIRONMENT': 'production'})

    settings = CommonSettings()
    assert settings.is_production is True
    assert settings.is_development is False
    assert settings.is_staging is False


def test_is_development_true(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENVIRONMENT': 'development'})

    settings = CommonSettings()
    assert settings.is_production is False
    assert settings.is_development is True
    assert settings.is_staging is False


def test_is_staging_true(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'ENVIRONMENT': 'staging'})

    settings = CommonSettings()
    assert settings.is_production is False
    assert settings.is_development is False
    assert settings.is_staging is True


def test_debug_default_false(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.debug is False


@pytest.mark.parametrize(
    'value,expected',
    [
        ('true', True),
        ('True', True),
        ('1', True),
        ('false', False),
        ('False', False),
        ('0', False),
    ],
)
def test_debug_boolean_parsing(mocker: MockerFixture, value: str, expected: bool) -> None:
    mocker.patch.dict(environ, {'DEBUG': value})

    settings = CommonSettings()
    assert settings.debug is expected


def test_log_level_default_info(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {}, clear=True)

    settings = CommonSettings()
    assert settings.log_level == 'INFO'


def test_log_level_custom(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'LOG_LEVEL': 'DEBUG'})

    settings = CommonSettings()
    assert settings.log_level == 'DEBUG'


def test_exports_all() -> None:
    from zimran import config

    assert hasattr(config, '__all__')
    assert 'CommonSettings' in config.__all__
    assert 'Environment' in config.__all__
    assert '__version__' in config.__all__


def test_version_exists() -> None:
    from zimran.config import __version__

    assert isinstance(__version__, str)
