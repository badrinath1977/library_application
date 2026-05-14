# AppErrorDBLog_Library

Production-ready reusable Python package for logging application exceptions into SQL Server.

## Features

- Logs exceptions to SQL Server table or stored procedure
- Uses `pyodbc` parameterized queries only
- Configurable connection string, schema, table, stored procedure, timeout, retries, app name, and column names
- Defaults to `GenAI_V1.ErrorLog`
- Thread-safe sync logging
- Async logging via worker thread
- Fallback JSON-lines file logging when SQL logging fails
- Decorator and context manager
- FastAPI, Flask, and Django integrations
- JSON, YAML, and environment-based config
- Logger failures do not crash the main application when `suppress_logger_errors=true`

## Installation

```powershell
pip install .
```

For YAML support:

```powershell
pip install ".[yaml]"
```

## Basic Usage

```python
from app_error_db_log import AppErrorLogger, AppErrorLogConfig

logger = AppErrorLogger.from_config_file("config.json", section="AppErrorDBLog")

try:
    1 / 0
except Exception as ex:
    logger.log_exception(
        ex,
        module_name="PaymentModule",
        user_id="123",
        correlation_id="abc-123",
    )
    raise
```

## Decorator

```python
@logger.log_exceptions(module_name="MyModule")
def my_function():
    risky_code()
```

## Context Manager

```python
with logger.capture(module_name="MyModule"):
    risky_code()
```

## FastAPI

```python
app.add_middleware(AppErrorDBLogMiddleware, logger=logger)
```

## Flask

```python
register_flask_error_handler(app, logger)
```

## Django

Use `AppErrorDBLogDjangoMiddleware` and inject an `AppErrorLogger` from your application setup.

## Configuration

See `examples/config.json` and `examples/config.yaml`.

If `stored_procedure_name` is set, the logger executes the stored procedure. Otherwise it writes to the configured schema/table with a parameterized `INSERT`.

## SQL Scripts

- `sql/create_table.sql`
- `sql/create_stored_procedure.sql`
- `sql/create_indexes.sql`

## Tests

```powershell
pytest
```

