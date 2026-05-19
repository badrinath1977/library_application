from __future__ import annotations

from enterprise_logging import get_logger
from keyvault_library import KeyVaultManager

from app.core.settings import Settings


def initialize_keyvault_manager(settings: Settings) -> KeyVaultManager | None:
    """Load optional Key Vault metadata through the shared library.

    ConfigRegistryAPI intentionally does not resolve secret references in API
    responses; the manager is initialized only so deployments can validate their
    Key Vault metadata consistently with other services.
    """

    if not settings.keyvault_config_path:
        return None
    logger = get_logger("core.keyvault")
    manager = KeyVaultManager.from_file(settings.keyvault_config_path)
    logger.info(
        "keyvault.config.loaded",
        {
            "keyVaultUrl": manager.get_keyvault_url(),
            "secretCount": len(manager.get_secret_names()),
        },
    )
    return manager
