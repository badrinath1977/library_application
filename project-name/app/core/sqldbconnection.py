from contextlib import contextmanager
from typing import Any, Iterator

from app.core.config import get_settings


def get_sql_connection_string() -> str:
    settings = get_settings()
    keyvault_connection_string = settings.get_secret("DATABASE_CONNECTION_STRING")

    if keyvault_connection_string:
        return keyvault_connection_string

    database = settings.database
    if database.connection_string:
        return database.connection_string

    trusted_connection = "yes" if database.trusted_connection else "no"
    trust_server_certificate = "yes" if database.trust_server_certificate else "no"

    return (
        f"Driver={{{database.driver}}};"
        f"Server={database.server};"
        f"Database={database.database};"
        f"Trusted_Connection={trusted_connection};"
        f"TrustServerCertificate={trust_server_certificate};"
    )


def get_sql_connection():
    try:
        import pyodbc
    except ImportError as exc:
        raise RuntimeError("pyodbc is required for SQL Server connections") from exc

    return pyodbc.connect(get_sql_connection_string(), timeout=5)


@contextmanager
def sql_connection() -> Iterator[Any]:
    connection = get_sql_connection()
    try:
        yield connection
    finally:
        connection.close()


def check_sql_database_connection() -> dict[str, Any]:
    settings = get_settings()
    try:
        with sql_connection() as connection:
            cursor = connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return {
            "connected": True,
            "database_type": settings.database.type,
            "server": settings.database.server,
            "database": settings.database.database,
            "message": "SQL database connection is healthy",
        }
    except Exception as exc:
        return {
            "connected": False,
            "database_type": settings.database.type,
            "server": settings.database.server,
            "database": settings.database.database,
            "message": str(exc),
        }
