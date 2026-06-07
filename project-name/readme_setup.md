# Setup Guide

## Configuration Flow

Default configuration lives in `config.json`.

```text
config.json -> app/core/config.py -> all other modules
```

Do not read `config.json` directly from routes, services, repositories, or middleware. Use `get_settings()` from `app/core/config.py`.

## Local Environment Variables

Environment variables are optional overrides for local testing or deployment:

```env
APP_ENV=local
SERVICE_NAME=project-name
ROUTE_NAME=sample
DOCS_URL=docs
REDOC_URL=redoc
OPENAPI_URL=openapi.json
HOST=0.0.0.0
PORT=8000
RELOAD=true
JWT_AUDIENCE=local-audience,another-audience
JWT_ISSUER=local-issuer,another-issuer
JWT_SECRET=local-dev-secret
JWT_JWKS_URL=
JWT_ALGORITHMS=HS256,RS256
JWT_REQUIRED=false
JWT_TEST_TOKEN_ENABLED=true
JWT_TEST_TOKEN_EXPIRY_SECONDS=3600
KEYVAULT_URL=
LOG_LEVEL=INFO
ERROR_DB_ENABLED=false
ERROR_DB_PATH=error_logs.db
DATABASE_TYPE=sqlserver
DATABASE_SERVER=localhost\SQLEXPRESS
DATABASE_NAME=master
DATABASE_DRIVER=ODBC Driver 17 for SQL Server
DATABASE_TRUSTED_CONNECTION=true
DATABASE_TRUST_SERVER_CERTIFICATE=true
DATABASE_CONNECTION_STRING=
EXTERNAL_API_ENABLED=false
EXTERNAL_API_BASE_URL=https://external-api.example.com
EXTERNAL_API_ENDPOINT=/api/resource
EXTERNAL_API_METHOD=POST
EXTERNAL_API_TIMEOUT_SECONDS=30
EXTERNAL_API_VERIFY_SSL=false
EXTERNAL_API_OAUTH_ENABLED=true
EXTERNAL_API_TOKEN_URL=https://login.microsoftonline.com/<tenant-id>/oauth2/v2.0/token
EXTERNAL_API_CLIENT_ID=
EXTERNAL_API_CLIENT_SECRET=
EXTERNAL_API_SCOPE=api://<external-api-client-id>/.default
```

## External API Flow

```text
API route
-> business service
-> ExternalApiService
-> external API
```

The external API URL and JWT settings are loaded through:

```text
config.json -> app/core/config.py -> ExternalApiService
```

`EXTERNAL_API_CLIENT_SECRET` is requested from KeyVault first when `keyvault.url` is configured. If KeyVault is unavailable or the secret is not found, the value from `config.json` or the environment is used.

The service uses the OAuth 2.0 Client Credentials flow to obtain an access token. The token is sent to the external API as:

```text
Authorization: Bearer <token>
```

For local environments using self-signed certificates, SSL verification can be disabled:

```json
"verify_ssl": false
```

Keep SSL verification enabled in production whenever possible.

For Windows authentication to local SQL Server Express, keep `trusted_connection` set to `true` in `config.json`.

The SQL connection flow is:

```text
KeyVault DATABASE_CONNECTION_STRING -> config.json database settings -> app/core/sqldbconnection.py -> repositories
```

Install the Microsoft ODBC Driver for SQL Server on the machine running the service. The default driver name is:

```text
ODBC Driver 17 for SQL Server
```

Local mode reads environment variables first. Deployed mode can read secrets from KeyVault through `Keyvault_library`.

## Dependencies

Install the service dependencies:

```bash
pip install -r requirements.txt
```

The service does not require internal custom libraries. It uses direct Python implementations for JWT validation, JSON logging, exception handling, PII masking, and KeyVault access.

## Docker

```bash
docker build -f project-name/Dockerfile -t project-name:local .
docker run --rm -p 8000:8000 --env-file .env project-name:local
```

## Kubernetes

Update `manifest.yaml` with:

- Container registry image
- Secret names
- Resource limits
- Namespace, if required

Then deploy:

```bash
kubectl apply -f manifest.yaml
```
