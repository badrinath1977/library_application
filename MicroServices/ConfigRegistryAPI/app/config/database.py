from __future__ import annotations

from typing import Any

import pyodbc

from app.core.settings import Settings


class Database:
    """Small pyodbc adapter so repositories stay testable and procedure-only."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def connect(self) -> Any:
        return pyodbc.connect(
            self._settings.sql_server_connection_string,
            timeout=self._settings.db_timeout_seconds,
        )
