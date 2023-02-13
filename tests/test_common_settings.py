from os import environ

import pytest
from pydantic import ValidationError
from pytest_mock import MockerFixture

from zimran.config import CommonSettings, Environment

SENTRY_DSN = 'https://public@sentry.example.com/1'


def test_sentry_dsn_ok(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'SENTRY_DSN': SENTRY_DSN})
    settings = CommonSettings()
    assert settings.sentry_dsn == SENTRY_DSN


def test_sentry_dsn_fail() -> None:
    with pytest.raises(ValidationError):
        CommonSettings()


@pytest.mark.parametrize('environment', [
    Environment.DEVELOPMENT, Environment.STAGING, Environment.PRODUCTION,
])
def test_environment_ok(mocker: MockerFixture, environment: Environment) -> None:
    mocker.patch.dict(environ, {'SENTRY_DSN': SENTRY_DSN, 'ENVIRONMENT': environment})
    settings = CommonSettings()
    assert settings.environment == environment


def test_environment_fail(mocker: MockerFixture) -> None:
    mocker.patch.dict(environ, {'SENTRY_DSN': SENTRY_DSN, 'ENVIRONMENT': 'wrong_environment'})

    with pytest.raises(ValidationError):
        CommonSettings()
