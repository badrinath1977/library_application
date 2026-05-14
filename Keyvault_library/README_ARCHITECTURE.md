# Keyvault Library Architecture

## Architecture Overview

`keyvault-library` separates configuration loading, validation, logging, models, and exceptions into small modules. This keeps the public API stable while allowing future Azure SDK integration behind the `KeyVaultManager` class.

## Module Responsibility

- `manager.py`: orchestrates file loading, JSON parsing, validation, logging setup, reloads, and public getters.
- `models.py`: defines the immutable `KeyVaultConfig` dataclass.
- `validators.py`: validates required config fields and converts lists into tuples.
- `logger.py`: creates structured daily file logs and protects logger setup.
- `exceptions.py`: defines the enterprise-safe custom exception hierarchy.
- `__init__.py`: exposes stable public imports.

## Data Flow

1. Application owns configuration and chooses how to provide it.
2. For file-backed config, the application calls `KeyVaultManager.from_file(path)`.
3. For already-loaded config, the application calls `KeyVaultManager.from_dict(data)`.
4. For deployment-driven paths, the application calls `KeyVaultManager.from_env()`.
5. Validators enforce required fields and types.
6. A frozen dataclass stores validated metadata.
7. Logger is created from `LogLocation`.
8. Applications retrieve safe immutable values through getter methods.

## Exception Flow

Internal failures are logged and converted to custom exceptions:

- missing file -> `ConfigFileNotFoundError`
- invalid JSON -> `InvalidConfigJsonError`
- missing key -> `MissingConfigKeyError`
- invalid value -> `InvalidConfigValueError`
- logger failure -> `LoggerSetupError`

All inherit from `KeyVaultLibraryError`, so consuming applications can catch one base exception.

## Logging Flow

Before `LogLocation` is known, the library uses a bootstrap package logger. After validation succeeds, it creates a file logger under `LogLocation` with the daily filename `keyvault_library_YYYYMMDD.log`.

Logs include method entry and exit, load success, validation success/failure, reload start/end, and exception stack traces through `logger.exception()`.

## Validation Flow

`validators.py` checks:

- `KeyVaultURL`: required non-empty string
- `SecretsName`: required non-empty list of strings
- `Key`: required non-empty list of strings
- `LogLocation`: required non-empty string

List values are returned as tuples to avoid exposing mutable state.

## Future Azure Key Vault SDK Integration Plan

Future versions can add an Azure SDK adapter module for:

- Managed Identity
- `DefaultAzureCredential`
- secret retrieval by configured secret name
- secret masking in logs
- centralized configuration services

The existing manager API can remain stable while new methods or injected adapters handle Azure-specific behavior.

## Security Design Principles

- Do not store real secrets.
- Do not log secret values.
- Do not hardcode credentials.
- Expose metadata only.
- Convert internal failures to custom exceptions.
- Use immutable data models and tuple responses.
- Include `pip-audit` in the development workflow.

## Why This Library Is Reusable

The library is configuration-driven, dependency-light, typed, tested, and isolated from application-specific behavior. Multiple applications can install the same wheel and provide their own config file path, dictionary, or environment variable.
