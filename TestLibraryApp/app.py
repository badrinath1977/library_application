"""Compatibility entrypoint for the TestLibraryApp consumer app."""

from __future__ import annotations

from keyvault_testing import main


if __name__ == "__main__":
    raise SystemExit(main())
