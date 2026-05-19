# Enterprise Logging Library Test

## Library

Installed from:

```text
../libraries-dist/logging_library/enterprise_logging_library-1.0.0-py3-none-any.whl
```

Import package:

```python
from enterprise_logging import initialize_logger, get_logger, flush, shutdown
```

## Test File

```text
TestLibraryApp/library_tests/test_enterprise_logging_library.py
```

## What It Tests

The test initializes the logging framework from an in-memory config, writes one structured log event, flushes it, and shuts the logger down.

## Output

The log file is written to:

```text
TestLibraryApp/logs/enterprise_logging.log
```

## Run Only This Test

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\python.exe .\library_tests\test_enterprise_logging_library.py
```

Expected output:

```text
PASS enterprise_logging: wrote logs/enterprise_logging.log
```
