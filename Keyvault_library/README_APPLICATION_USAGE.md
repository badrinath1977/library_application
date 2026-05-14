# Application Usage Guide

This document explains how another application can consume `keyvault-library`.

## Install From Wheel File

After building the library:

```powershell
pip install dist/keyvault_library-0.1.0-py3-none-any.whl
```

## Install From Internal Artifact Repository

Publish the wheel to your internal package feed, then install it using your organization-approved index URL:

```powershell
pip install keyvault-library==0.1.0 --index-url https://your-internal-feed/simple
```

## Sample Consumer app.py

```python
from keyvault_library import KeyVaultManager
from keyvault_library.exceptions import KeyVaultLibraryError


def main() -> None:
    try:
        manager = KeyVaultManager.from_file("config/keyvault_library.config.json")
        keyvault_url = manager.get_keyvault_url()
        secrets = manager.get_secret_names()
        keys = manager.get_keys()

        print(keyvault_url)
        print(secrets)
        print(keys)
    except KeyVaultLibraryError as ex:
        print(f"Configuration error: {ex}")


if __name__ == "__main__":
    main()
```

## Recommended Configuration Pattern

The consuming application should own the configuration file. Avoid relying on a
library-internal `config.json`. A good application structure is:

```text
MyApplication/
├── app.py
└── config/
    └── keyvault_library.config.json
```

Then load it explicitly:

```python
manager = KeyVaultManager.from_file("config/keyvault_library.config.json")
```

You can also pass configuration that the application already loaded:

```python
manager = KeyVaultManager.from_dict(app_config["KeyVault"])
```

For CI/CD, containers, Windows services, and Azure deployments, store the config
path in an environment variable:

```powershell
$env:KEYVAULT_LIBRARY_CONFIG = "C:/Apps/MyApplication/config/keyvault_library.config.json"
```

```python
manager = KeyVaultManager.from_env()
```

## Sample keyvault_library.config.json

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

## Sample requirements.txt

For a published internal package:

```text
keyvault-library==0.1.0
```

For local development:

```text
-e C:/Projects/Python-Library/Keyvault_library
```

## Exception Handling In Consumer App

Applications can catch one base exception:

```python
from keyvault_library.exceptions import KeyVaultLibraryError

try:
    ...
except KeyVaultLibraryError as ex:
    print(f"Configuration error: {ex}")
```

## Recommended Enterprise Deployment Flow

1. Build and test the library in CI.
2. Run `pytest`, `ruff`, `mypy`, `pip-audit`, and coverage.
3. Publish only wheel and sdist artifacts from `dist/`.
4. Pin `keyvault-library==0.1.0` in consumer applications.
5. Keep environment-specific `config.json` files outside public repositories.
6. Restrict write access to `LogLocation`.
7. Use Managed Identity or `DefaultAzureCredential` when Azure SDK integration is added.
