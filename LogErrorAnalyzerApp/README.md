# LogErrorAnalyzerApp

FastAPI backend application that reads log files from a file or folder, extracts errors and stack traces, groups duplicate errors, optionally asks an LLM for solution suggestions, and optionally creates a ticket.

This app also consumes the reusable internal libraries:

- `keyvault-library` from `../Keyvault_library/dist/keyvault_library-0.1.0-py3-none-any.whl`
- `AppErrorDBLog-Library` from `../AppErrorDBLog_Library/dist/apperrordblog_library-0.1.0-py3-none-any.whl`

`keyvault-library` reads app-owned config from `config/keyvault_library.config.json`.
`AppErrorDBLog-Library` reads app-owned config from `config/app_error_db_log.config.json` and logs API failures to SQL Server or fallback file.

## Setup

```powershell
cd C:\Projects\Python-Library\LogErrorAnalyzerApp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and adjust values if needed.

## Run

```powershell
uvicorn app.main:app --reload
```

## APIs

### Health

```powershell
curl http://127.0.0.1:8000/health
```

The health response includes safe Key Vault metadata loaded through `KeyVaultManager.from_file(...)`.

### Analyze File Or Folder

```powershell
curl -X POST http://127.0.0.1:8000/analyze-log ^
  -H "Content-Type: application/json" ^
  -d "{\"path\":\"sample_logs\",\"recursive\":true,\"call_llm\":true,\"create_ticket\":true}"
```

### Get Error

```powershell
curl http://127.0.0.1:8000/errors/{error_id}
```

### Create Ticket

```powershell
curl -X POST http://127.0.0.1:8000/create-ticket ^
  -H "Content-Type: application/json" ^
  -d "{\"error_id\":\"<error-id>\"}"
```

## Example Response

```json
{
  "status": "success",
  "summary": {
    "files_scanned": 1,
    "errors_found": 1,
    "unique_errors": 1
  },
  "errors": [
    {
      "id": "abc123",
      "error_message": "division by zero",
      "exception_type": "ZeroDivisionError",
      "stacktrace": "...",
      "method_name": "process_payment",
      "file_name": "service.py",
      "line_number": 42,
      "class_name": null,
      "module_name": "service",
      "timestamp": "2026-05-13 10:15:22",
      "occurrence_count": 1,
      "root_cause_guess": "ZeroDivisionError: division by zero",
      "llm_solution": "Severity: High...",
      "ticket": {
        "created": true,
        "ticket_id": "LOG-ABC12345"
      }
    }
  ]
}
```

## Notes

- Supported extensions default to `.log,.txt`.
- Unknown stack formats are parsed best-effort and raw error content is always preserved.
- The mock LLM provider is enabled by default. Real providers can be added behind `LLMService`.
- Ticket creation uses a mock provider by default.
- Failures are logged and returned as clear JSON responses.
- API route failures are logged through `AppErrorDBLog_Library`.
- With the default `config/app_error_db_log.config.json`, DB logging falls back to `logs/app_error_db_fallback.log` because the connection string is intentionally empty.

## Internal Library Config

Key Vault config:

```text
config/keyvault_library.config.json
```

DB error logging config:

```text
config/app_error_db_log.config.json
```

Update the DB logging config with a real SQL Server connection string when you want inserts into `GenAI_V1.ErrorLog`.

## Tests

```powershell
pytest
```
