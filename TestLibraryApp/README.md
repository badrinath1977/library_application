# TestLibraryApp

`TestLibraryApp` is a consumer application used to validate that all local libraries can be installed from the shared `libraries-dist` folder and used like third-party packages.

## Shared Distribution Folder

All library artifacts are collected under:

```text
C:\Projects\Python-Library\libraries-dist
```

Expected libraries:

- `AppErrorDBLog_Library`
- `Keyvault_library`
- `llm_platform_library`
- `logging_library`
- `jwt_validation_library`
- `pii_protection_library`

## Install Libraries

```powershell
cd C:\Projects\Python-Library\TestLibraryApp
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` references wheels directly from `../libraries-dist/...`.

## Run All Library Smoke Tests

```powershell
python app.py
```

Or:

```powershell
python run_test_app.py
```

## What The App Tests

- `keyvault_library`: loads the app-owned `config.json`
- `app_error_db_log`: logs a synthetic exception and safely uses fallback logging
- `llm_platform_library`: routes a prompt, renders a template, and tracks cost
- `enterprise_logging`: writes a structured log file
- `jwt_validation`: validates a local HS256 JWT and returns `sub`
- `pii_protection`: tokenizes and restores an email placeholder

## Separate Test Files

Each library has its own test file so the examples are easy to understand:

```text
library_tests/test_keyvault_library.py
library_tests/test_app_error_db_log_library.py
library_tests/test_llm_platform_library.py
library_tests/test_enterprise_logging_library.py
library_tests/test_jwt_validation_library.py
library_tests/test_pii_protection_library.py
```

Run one test directly:

```powershell
.\.venv\Scripts\python.exe .\library_tests\test_pii_protection_library.py
```

## Per-Library READMEs

Each library also has a short explanation file:

```text
docs/keyvault_library.md
docs/app_error_db_log_library.md
docs/llm_platform_library.md
docs/enterprise_logging_library.md
docs/jwt_validation_library.md
docs/pii_protection_library.md
```

## Expected Output

```text
TestLibraryApp all-library smoke test started
PASS keyvault_library: ...
PASS app_error_db_log: ...
PASS llm_platform_library: ...
PASS enterprise_logging: ...
PASS jwt_validation: ...
PASS pii_protection: ...
All library smoke tests completed successfully
```

## Logs

Runtime logs are written under:

```text
TestLibraryApp/logs
```
