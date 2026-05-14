# keyvault-library

`keyvault-library` is a reusable enterprise Python 3.11+ library for Azure Key Vault configuration management. It validates Key Vault metadata, creates structured logs, exposes safe immutable configuration values, and prepares the codebase for future Azure Key Vault SDK integration.

The recommended production pattern is simple: the consuming application owns configuration and passes it explicitly to the library.

## Features

- Safe JSON configuration loading from an explicit application-owned path
- `from_file`, `from_dict`, and `from_env` constructors
- Strict validation for required Azure Key Vault metadata
- Custom exception hierarchy rooted at `KeyVaultLibraryError`
- Structured file logging with daily log files
- Immutable tuple responses for list values
- No hardcoded credentials or real secrets
- Modern packaging with `pyproject.toml`
- Build automation through `build_library.py`

## Project Structure

```text
Keyvault_library/
├── keyvault_library/
├── tests/
├── config.json
├── build_library.py
├── README.md
├── README_ARCHITECTURE.md
├── README_APPLICATION_USAGE.md
├── pyproject.toml
└── .gitignore
```

## Configuration Pattern

Do not rely on the library folder's sample `config.json` in production. Each application should provide its own config path:

```python
from keyvault_library import KeyVaultManager

manager = KeyVaultManager.from_file("config/keyvault_library.config.json")
```

If the application already loaded configuration:

```python
manager = KeyVaultManager.from_dict(app_config["KeyVault"])
```

If the path is supplied by deployment:

```powershell
$env:KEYVAULT_LIBRARY_CONFIG = "C:/Apps/MyApp/config/keyvault_library.config.json"
```

```python
manager = KeyVaultManager.from_env()
```

## Sample Config Format

```json
{
  "KeyVaultURL": "https://testingkeyvalut.vault.azure.net/",
  "SecretsName": [
    "sec1",
    "sec2",
    "sec3"
  ],
  "Key": [
    "k1",
    "k2"
  ],
  "LogLocation": "C:/Logs/keyvault_library"
}
```

## Install Steps

```powershell
cd C:\Projects\Python-Library\Keyvault_library
python -m pip install .
```

## Editable Install

```powershell
python -m pip install -e ".[dev]"
```

## Quality Commands

```powershell
pytest
ruff check .
mypy keyvault_library
pip-audit
pytest --cov=keyvault_library
python -m build
```

## build_library.py Usage

```powershell
python build_library.py
```

The script cleans old build artifacts, installs dev dependencies, runs tests, linting, type checking, audit, coverage, and package build.

## Exception Handling Example

```python
from keyvault_library import KeyVaultManager
from keyvault_library.exceptions import KeyVaultLibraryError

try:
    manager = KeyVaultManager.from_file("config/keyvault_library.config.json")
    keyvault_url = manager.get_keyvault_url()
    secrets = manager.get_secret_names()
    keys = manager.get_keys()
except KeyVaultLibraryError as ex:
    print(f"Configuration error: {ex}")
```

## Logging Explanation

Logs are created in `LogLocation` using this filename format:

```text
keyvault_library_YYYYMMDD.log
```

The library logs method start/end, successful config loading, validation success/failure, reload activity, and exceptions with stack traces. Library code does not use `print()` for logging.

