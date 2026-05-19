# AppErrorDBLog Library Test

## Library

Installed from:

```text
../libraries-dist/AppErrorDBLog_Library/apperrordblog_library-0.1.0-py3-none-any.whl
```

Import package:

```python
from app_error_db_log import AppErrorLogConfig, AppErrorLogger
```

## Test File

```text
TestLibraryApp/library_tests/test_app_error_db_log_library.py
```

## What It Tests

The test creates `AppErrorLogConfig` with an empty database connection string and `suppress_logger_errors=True`. It logs a synthetic exception and verifies that the library safely falls back to a local fallback file instead of crashing the parent application.

## Why This Matters

Applications should be able to use the error logging library even when SQL Server is temporarily unavailable. The test proves safe failure behavior.

## Run Only This Test

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\python.exe .\library_tests\test_app_error_db_log_library.py
```

Expected output:

```text
PASS app_error_db_log: success=False fallback=True
```
