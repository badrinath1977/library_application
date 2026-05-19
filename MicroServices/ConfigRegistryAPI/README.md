# ConfigRegistryAPI

ConfigRegistryAPI is the stored-procedure-only FastAPI service for `GenAI.AppConfig`.
Parent services should call this API instead of accessing `GenAI.AppConfig` directly.

## Technology

- Python 3.11
- FastAPI
- SQL Server through `pyodbc`
- Windows Authentication
- JWT validation through `jwt_validation_library`
- Structured logging through `logging_library`
- PII masking through `pii_protection_library`
- Optional Key Vault metadata validation through `Keyvault_library`
- Exception capture through `AppErrorDBLog_Library` fallback logging

## Database Contract

Application code calls only these procedures:

- `GenAI.sp_AppConfig_GetAll`
- `GenAI.sp_AppConfig_GetByKey`
- `GenAI.sp_AppConfig_Insert`
- `GenAI.sp_AppConfig_Update`
- `GenAI.sp_AppConfig_Upsert`
- `GenAI.sp_AppConfig_SetActive`

There is no table access, ORM access, or inline AppConfig data access.

## Folder Structure

```text
MicroServices/ConfigRegistryAPI/
  app/
    config/database.py
    core/exception_handler.py
    core/keyvault.py
    core/settings.py
    middleware/auth_middleware.py
    middleware/correlation_middleware.py
    models/request_models.py
    models/response_models.py
    repositories/appconfig_repository.py
    routes/appconfig_routes.py
    services/appconfig_service.py
    services/security.py
    main.py
  main.py
  requirements.txt
  .env.sample
  Dockerfile
```

## Setup

```powershell
cd C:\Projects\Python-Library\MicroServices\ConfigRegistryAPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.sample .env
```

Edit `.env` for your JWT issuer and SQL Server settings.

Default SQL Server connection:

```text
DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=genai_db;Trusted_Connection=yes;TrustServerCertificate=yes;
```

## Run

```powershell
python run_server.py
```

Swagger UI:

- `http://localhost:8000/docs`
- `http://localhost:8000/redoc`
- `http://localhost:8000/openapi.json`

## Health APIs

These endpoints are public:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/live
curl http://localhost:8000/ready
```

## Protected APIs

All `/api/config/*` endpoints require:

```text
Authorization: Bearer <jwt>
```

### Get All

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/config/all?ApplicationName=loan-service&EnvironmentName=dev&OnlyActive=true"
```

### Get By Key

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/config/by-key?ConfigKey=llm.provider&ApplicationName=loan-service&EnvironmentName=dev"
```

### Create

```bash
curl -X POST "http://localhost:8000/api/config" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ApplicationName": "loan-service",
    "EnvironmentName": "dev",
    "ConfigKey": "llm.provider",
    "ConfigValue": "azure-openai",
    "ConfigType": "string",
    "IsSensitive": false,
    "IsActive": true,
    "Description": "Default LLM provider",
    "CreatedBy": "admin"
  }'
```

### Update

```bash
curl -X PUT "http://localhost:8000/api/config/10" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ConfigValue": "openai",
    "ConfigType": "string",
    "IsSensitive": false,
    "IsActive": true,
    "Description": "Updated provider",
    "UpdatedBy": "admin"
  }'
```

### Upsert

```bash
curl -X POST "http://localhost:8000/api/config/upsert" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ApplicationName": "loan-service",
    "EnvironmentName": "dev",
    "ConfigKey": "secret.reference",
    "ConfigValue": "keyvault://loan-service/api-key",
    "ConfigType": "secret-ref",
    "IsSensitive": true,
    "IsActive": true,
    "Description": "Key Vault reference",
    "UpdatedBy": "admin"
  }'
```

### Set Active

```bash
curl -X PATCH "http://localhost:8000/api/config/10/active" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"IsActive": false, "UpdatedBy": "admin"}'
```

## Security Behavior

- Sensitive rows return `ConfigValue` as the configured mask.
- Key Vault references return `<KEYVAULT_SECRET_REF>` unless the row is already sensitive.
- Raw sensitive config values are masked before logging.
- JWTs are validated with the shared JWT validation library.
- `alg=none` is rejected by the JWT library.
- Configure issuer, audience, scopes, roles, and allowed algorithms in `.env`.

## Stored Procedure Signatures

The repository calls procedure parameters in this order:

- `sp_AppConfig_GetAll`: `ApplicationName`, `EnvironmentName`, `OnlyActive`
- `sp_AppConfig_GetByKey`: `ConfigKey`, `ApplicationName`, `EnvironmentName`
- `sp_AppConfig_Insert`: `ApplicationName`, `EnvironmentName`, `ConfigKey`, `ConfigValue`, `ConfigType`, `IsSensitive`, `IsActive`, `Description`, `CreatedBy`
- `sp_AppConfig_Update`: `ConfigId`, `ConfigValue`, `ConfigType`, `IsSensitive`, `IsActive`, `Description`, `UpdatedBy`
- `sp_AppConfig_Upsert`: `ApplicationName`, `EnvironmentName`, `ConfigKey`, `ConfigValue`, `ConfigType`, `IsSensitive`, `IsActive`, `Description`, `UpdatedBy`
- `sp_AppConfig_SetActive`: `ConfigId`, `IsActive`, `UpdatedBy`

If your database procedure parameters differ, update only `app/repositories/appconfig_repository.py`.

## Docker

```powershell
cd C:\Projects\Python-Library
docker build -f MicroServices/ConfigRegistryAPI/Dockerfile -t config-registry-api .
docker run --rm -p 8000:8000 --env-file MicroServices/ConfigRegistryAPI/.env config-registry-api
```

Windows Authentication from Linux containers requires domain/gMSA or a deployment-specific identity strategy. For local Windows development, running directly on Windows with the ODBC Driver 17 for SQL Server is the simplest path.

## Production Notes

- Keep `AUTH_ENABLED=true` outside local troubleshooting.
- Prefer JWKS over embedded public keys.
- Restrict `JWT_ALLOWED_ALGORITHMS` to the exact algorithms your issuer uses.
- Send logs to stdout in Kubernetes and centralize with your platform log collector.
- Keep secret values in Key Vault; store only references in AppConfig.
- Monitor procedure latency and failure rates at the service boundary.
