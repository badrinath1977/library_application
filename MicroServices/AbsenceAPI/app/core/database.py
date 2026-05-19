from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

import pyodbc

from app.core.settings import Settings


class Database:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def connect(self) -> Any:
        connection = pyodbc.connect(
            self._settings.sql_server_connection_string,
            timeout=self._settings.db_timeout_seconds,
        )
        # SQL Server datetimeoffset is exposed by ODBC as type -155. Some
        # pyodbc builds do not decode it automatically, so convert it here once
        # at the connection boundary instead of leaking driver bytes upward.
        connection.add_output_converter(-155, _decode_datetimeoffset)
        return connection


def _decode_datetimeoffset(raw: bytes) -> str:
    if not raw:
        return ""
    try:
        if len(raw) < 10:
            return raw.hex()
        time_units = int.from_bytes(raw[0:5], byteorder="little", signed=False)
        day_count = int.from_bytes(raw[5:8], byteorder="little", signed=False)
        offset_minutes = int.from_bytes(raw[8:10], byteorder="little", signed=True)
        base_date = date(1, 1, 1) + timedelta(days=day_count)
        whole_seconds, remainder_100ns = divmod(time_units, 10_000_000)
        microseconds = remainder_100ns // 10
        hours, remainder = divmod(whole_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        tz = timezone(timedelta(minutes=offset_minutes))
        return datetime(
            base_date.year,
            base_date.month,
            base_date.day,
            int(hours),
            int(minutes),
            int(seconds),
            int(microseconds),
            tzinfo=tz,
        ).isoformat()
    except Exception:  # noqa: BLE001
        return raw.hex()
