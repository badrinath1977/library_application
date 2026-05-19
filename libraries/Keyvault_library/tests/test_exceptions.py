"""Tests for the custom exception hierarchy."""

from libraries.Keyvault_library.keyvault_library.exceptions import (
    ConfigFileNotFoundError,
    InvalidConfigJsonError,
    InvalidConfigValueError,
    KeyVaultLibraryError,
    LoggerSetupError,
    MissingConfigKeyError,
)


def test_custom_exceptions_inherit_from_keyvault_library_error() -> None:
    exception_types = (
        ConfigFileNotFoundError,
        InvalidConfigJsonError,
        MissingConfigKeyError,
        InvalidConfigValueError,
        LoggerSetupError,
    )

    for exception_type in exception_types:
        assert issubclass(exception_type, KeyVaultLibraryError)

