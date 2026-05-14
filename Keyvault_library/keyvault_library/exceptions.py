"""Custom exception hierarchy for keyvault_library."""


class KeyVaultLibraryError(Exception):
    """Base exception for all expected keyvault_library failures."""


class ConfigFileNotFoundError(KeyVaultLibraryError):
    """Raised when the configuration file cannot be found."""


class InvalidConfigJsonError(KeyVaultLibraryError):
    """Raised when the configuration file contains invalid JSON."""


class MissingConfigKeyError(KeyVaultLibraryError):
    """Raised when a required configuration key is missing."""


class InvalidConfigValueError(KeyVaultLibraryError):
    """Raised when a configuration value is invalid."""


class LoggerSetupError(KeyVaultLibraryError):
    """Raised when logger setup fails."""

