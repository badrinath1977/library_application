"""Structured logging configuration."""

from __future__ import annotations

import logging
import sys

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    """Configure process logging."""

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format=(
            "%(asctime)s | level=%(levelname)s | logger=%(name)s | "
            "module=%(module)s | function=%(funcName)s | message=%(message)s"
        ),
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True,
    )

