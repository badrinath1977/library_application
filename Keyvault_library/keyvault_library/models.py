"""Immutable configuration models for keyvault_library."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class KeyVaultConfig:
    """Validated Azure Key Vault configuration metadata.

    This model stores configuration metadata only. It does not store or expose
    secret values.
    """

    keyvault_url: str
    secret_names: tuple[str, ...]
    keys: tuple[str, ...]
    log_location: str

