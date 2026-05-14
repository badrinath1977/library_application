"""Test consumer application for keyvault-library."""

from __future__ import annotations

import logging
from pathlib import Path

from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.secrets import SecretClient
from keyvault_library import KeyVaultManager
from keyvault_library.exceptions import KeyVaultLibraryError


def main() -> int:
    """Run the test consumer application."""

    config_path = Path("config.json").resolve()

    print("KeyVault Library Test Application Started")
    print(f"Config File Used: {config_path}")

    try:
        manager = KeyVaultManager.from_file("config.json")
    except KeyVaultLibraryError as ex:
        print(f"Configuration error: {ex}")
        return 1

    # Set up logging
    log_location = manager.get_log_location()
    logging.basicConfig(
        filename=f"{log_location}/app.log",
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )
    logger = logging.getLogger(__name__)

    print("Configuration loaded successfully")
    print(f"KeyVault URL: {manager.get_keyvault_url()}")
    print(f"Secrets Count: {len(manager.get_secret_names())}")
    print(f"Keys Count: {len(manager.get_keys())}")
    print(f"Log Location: {manager.get_log_location()}")

    # Set up Azure Key Vault clients
    credential = DefaultAzureCredential()
    keyvault_url = manager.get_keyvault_url()
    secret_client = SecretClient(vault_url=keyvault_url, credential=credential)
    key_client = KeyClient(vault_url=keyvault_url, credential=credential)

    # Read and log secrets
    logger.info("Starting to read secrets from Key Vault")
    for secret_name in manager.get_secret_names():
        try:
            secret = secret_client.get_secret(secret_name)
            logger.info(f"Read secret '{secret_name}': {secret.value}")
            print(f"Logged secret value: {secret.value}")
        except Exception as ex:
            logger.error(f"Failed to read secret '{secret_name}': {ex}")
            print(f"Error reading secret: {secret_name}")

    # Read and log keys
    logger.info("Starting to read keys from Key Vault")
    for key_name in manager.get_keys():
        try:
            key = key_client.get_key(key_name)
            logger.info(f"Read key '{key_name}': {key.key}")
            print(f"Logged key value: {key.key}")
        except Exception as ex:
            logger.error(f"Failed to read key '{key_name}': {ex}")
            print(f"Error reading key: {key_name}")

    print("Test completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
