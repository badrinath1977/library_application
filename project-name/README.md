# FastAPI Microservice Boilerplate

Configuration flow:

```text
config.json -> app/core/config.py -> all other modules
```

SQL connection flow:

```text
KeyVault DATABASE_CONNECTION_STRING -> config.json database settings -> app/core/sqldbconnection.py -> repositories
```

This template centralizes non-functional requirements so business teams only implement:

- API route orchestration
- Service logic
- Repository logic
- Request, response, and database models

The common platform concerns are handled by middleware and core helpers:

- JWT validation through direct PyJWT validation
- KeyVault-backed configuration through direct Azure KeyVault REST calls
- Request and response logging through standard Python JSON logging
- Correlation IDs
- Global exception handling
- Centralized error logging
- PII masking through built-in regex rules
- Standard API response envelopes

## Run Locally

Update `config.json` for local defaults. Environment variables can still override values when needed.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python run_server.py
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_server.py
```

## Endpoints

- `GET /api/sample/health/`
- `GET /api/sample/health/db`
- `POST /api/sample/`
- `POST /api/sample/customer/`
- `GET /api/sample/customer/`
- `GET /api/sample/customer/{customer_id}`
- `PUT /api/sample/customer/{customer_id}`
- `DELETE /api/sample/customer/{customer_id}`
- `GET /api/sample/docs`

The `sample` route segment comes from `route_name` in `config.json`.

## Build Container

Run from the repository root:

```bash
docker build -f project-name/Dockerfile -t project-name:local .
```

## Business Code Rules

- Keep route files thin.
- Put orchestration and business behavior in services.
- Put database access in repositories.
- Do not repeat JWT, logging, exception handling, or PII masking in API handlers.
- Add new routes under `app/api/routes`.
