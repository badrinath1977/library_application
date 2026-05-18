from __future__ import annotations

import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from pii_protection.exceptions import PiiCryptoError


class AesGcmCrypto:
    def encrypt(self, plaintext: str, key: bytes) -> str:
        try:
            nonce = os.urandom(12)
            ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
            encoded = base64.urlsafe_b64encode(nonce + ciphertext).decode("ascii").rstrip("=")
            return f"ENC({encoded})"
        except Exception as exc:
            raise PiiCryptoError("Unable to encrypt value") from exc

    def decrypt(self, protected_value: str, key: bytes) -> str:
        try:
            encoded = protected_value[4:-1]
            padded = encoded + "=" * (-len(encoded) % 4)
            raw = base64.urlsafe_b64decode(padded)
            nonce, ciphertext = raw[:12], raw[12:]
            return AESGCM(key).decrypt(nonce, ciphertext, None).decode("utf-8")
        except Exception as exc:
            raise PiiCryptoError("Unable to decrypt value") from exc
