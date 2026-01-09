# zimran-config

Pydantic-based configuration for FastAPI services.

## Installation

```bash
pip install zimran-config
```

## Quick Start

```python
from zimran.config import CommonSettings, Environment


class Settings(CommonSettings):
    database_url: str
    api_key: str


settings = Settings()
```

## Features

- Built on pydantic-settings v2
- Automatic `.env` file loading
- Environment enum (development, staging, production)
- Computed `is_production` / `is_development` / `is_staging` properties
- Sentry DSN validation
- Debug mode flag
- Configurable log level
- Centralized locale configuration with fallback support

## Configuration

### Environment Variables

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DEBUG` | bool | `False` | Enable debug mode |
| `ENVIRONMENT` | str | `development` | One of: development, staging, production |
| `SENTRY_DSN` | url | `None` | Sentry error tracking DSN |
| `LOG_LEVEL` | str | `INFO` | Logging level |
| `LOCALE_CONFIG` | json | `None` | JSON string with locale metadata |
| `ENABLED_LOCALES` | str | `None` | Comma-separated list of enabled locales |

### Using .env Files

Create a `.env` file in your project root:

```env
DEBUG=true
ENVIRONMENT=development
SENTRY_DSN=https://public@sentry.example.com/1
LOG_LEVEL=DEBUG
```

Settings are automatically loaded from the `.env` file.

### Extending Settings

```python
from pydantic import PostgresDsn, SecretStr
from zimran.config import CommonSettings


class Settings(CommonSettings):
    database_url: PostgresDsn
    api_key: SecretStr
    app_name: str = 'my-service'


settings = Settings()

if settings.is_production:
    print('Running in production mode')
```

### Custom .env File Location

```python
from zimran.config import CommonSettings


class Settings(CommonSettings):
    model_config = CommonSettings.model_config.copy()
    model_config['env_file'] = '.env.local'
```

### Locale Configuration

Get supported locales with automatic fallback:

```python
from zimran.config import CommonSettings, DEFAULT_LOCALES

class Settings(CommonSettings):
    pass

settings = Settings()

# Returns DEFAULT_LOCALES if LOCALE_CONFIG env var is not set
supported = settings.get_supported_locales()
```

With full locale metadata from `LOCALE_CONFIG` environment variable:

```python
# LOCALE_CONFIG='{"defaultLocale":"en","locales":{"en":{"code":"en","displayName":"English","nativeName":"English","direction":"ltr"},"es":{"code":"es","displayName":"Spanish","nativeName":"Español","direction":"ltr","fallback":"en"}}}'

settings = Settings()

# Access locale metadata
if settings.locale_config:
    Locale = settings.locale_config.get_enum()  # Dynamic StrEnum
    en = settings.locale_config.get('en')
    print(en.display_name)  # "English"
    print(en.is_rtl)  # False
```

Filter to specific locales with `ENABLED_LOCALES`:

```python
# ENABLED_LOCALES='en,es,fr'

settings = Settings()
supported = settings.get_supported_locales()  # frozenset({'en', 'es', 'fr'})
```

#### LocaleMetadata Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `code` | str | required | Locale code (e.g., "en") |
| `display_name` | str | required | Display name (e.g., "English") |
| `native_name` | str | required | Native name (e.g., "English") |
| `direction` | str | `"ltr"` | Text direction: "ltr" or "rtl" |
| `fallback` | str | `None` | Fallback locale code |

#### Default Locales

When `LOCALE_CONFIG` is not set, `get_supported_locales()` returns:

```python
DEFAULT_LOCALES = {'en', 'es', 'fr', 'de', 'it', 'pt', 'ja', 'fil', 'id'}
```

## Development

```bash
pip install -e ".[dev]"

ruff check .
ruff format --check .
mypy .
pytest
```

## License

MIT
