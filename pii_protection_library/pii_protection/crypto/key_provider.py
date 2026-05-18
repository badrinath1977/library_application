from __future__ import annotations

import base64
import hashlib
import os
from typing import Protocol

from pii_protection.exceptions import PiiConfigError
from pii_protection.models import KeyConfig, PiiRequestContext


class KeyProvider(Protocol):
    def encryption_key(self, context: PiiRequestContext) -> bytes:
        """Return AES key bytes."""

    def hmac_key(self, context: PiiRequestContext) -> bytes:
        """Return HMAC key bytes."""


class EnvKeyProvider:
    def __init__(self, key_config: KeyConfig) -> None:
        self.key_config = key_config

    def encryption_key(self, context: PiiRequestContext) -> bytes:
        del context
        return hashlib.sha256(self._resolve(self.key_config.key1_ref)).digest()

    def hmac_key(self, context: PiiRequestContext) -> bytes:
        del context
        key1 = self._resolve(self.key_config.key1_ref)
        key2 = self._resolve(self.key_config.key2_ref)
        return hashlib.sha256(key1 + b":" + key2).digest()

    @staticmethod
    def _resolve(ref: str | None) -> bytes:
        if not ref:
            raise PiiConfigError("Key reference is required")
        value = os.getenv(ref)
        if not value:
            raise PiiConfigError(f"Missing key environment variable: {ref}")
        try:
            return base64.b64decode(value, validate=True)
        except ValueError:
            return value.encode("utf-8")
