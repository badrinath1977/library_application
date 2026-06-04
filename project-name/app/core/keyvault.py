import os
import json
from functools import lru_cache
from urllib.parse import quote
from urllib.request import Request, urlopen


class KeyVaultProvider:
    def __init__(self, keyvault_url: str | None) -> None:
        self.keyvault_url = keyvault_url
        self._client = None

    def get_secret(self, name: str, default: str | None = None) -> str | None:
        env_value = os.getenv(name)
        if env_value is not None:
            return env_value

        if not self.keyvault_url:
            return default

        try:
            token = self._get_managed_identity_token()
            secret_url = (
                f"{self.keyvault_url.rstrip('/')}/secrets/{quote(name)}"
                "?api-version=7.4"
            )
            request = Request(secret_url, headers={"Authorization": f"Bearer {token}"})
            with urlopen(request, timeout=5) as response:
                payload = json.loads(response.read().decode("utf-8"))
                return payload.get("value", default)
        except Exception:
            return default

    @staticmethod
    def _get_managed_identity_token() -> str:
        token_url = (
            "http://169.254.169.254/metadata/identity/oauth2/token"
            "?api-version=2018-02-01"
            "&resource=https%3A%2F%2Fvault.azure.net"
        )
        request = Request(token_url, headers={"Metadata": "true"})
        with urlopen(request, timeout=5) as response:
            payload = json.loads(response.read().decode("utf-8"))
            return payload["access_token"]


@lru_cache
def get_keyvault_provider(keyvault_url: str | None) -> KeyVaultProvider:
    return KeyVaultProvider(keyvault_url)
