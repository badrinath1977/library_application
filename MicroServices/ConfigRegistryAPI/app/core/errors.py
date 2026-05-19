from __future__ import annotations


class ConfigRegistryError(Exception):
    status_code = 500
    error_code = "config_registry_error"


class DatabaseOperationError(ConfigRegistryError):
    status_code = 502
    error_code = "database_operation_failed"


class AuthenticationConfigurationError(ConfigRegistryError):
    status_code = 503
    error_code = "authentication_not_configured"

