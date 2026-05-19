"""Smoke test for keyvault_library installed from libraries-dist."""

from __future__ import annotations

from keyvault_library import KeyVaultManager


def run() -> str:
    manager = KeyVaultManager.from_file("config.json")
    return (
        "PASS keyvault_library: "
        f"url={manager.get_keyvault_url()} "
        f"secrets={len(manager.get_secret_names())} "
        f"keys={len(manager.get_keys())}"
    )


if __name__ == "__main__":
    print(run())
