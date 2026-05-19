from __future__ import annotations


class PiiProtectionError(Exception):
    """Base exception for PII protection failures."""


class PiiConfigError(PiiProtectionError):
    """Raised when PII configuration is invalid."""


class PiiValidationError(PiiProtectionError):
    """Raised when a configured PII value fails regex validation."""


class PiiRestoreDeniedError(PiiProtectionError):
    """Raised when restore policy denies a restore operation."""


class PiiMappingNotFoundError(PiiProtectionError):
    """Raised when a reversible token cannot be resolved."""


class PiiCryptoError(PiiProtectionError):
    """Raised when encryption or decryption fails."""
