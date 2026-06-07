# Local Testing Guide

## 1. Activate the Virtual Environment

```powershell
cd C:\Projects\Python-Library\project-name
.\.venv\Scripts\Activate.ps1
```

## 2. Install Dependencies

Run this again whenever `requirements.txt` changes:

```powershell
python -m pip install -r requirements.txt
```

## 3. Configure Local Testing

Update `config.json`:

```json
{
  "app_env": "local",
  "route_name": "sample",
  "jwt": {
    "required": true,
    "audience": [
      "local-test-api",
      "api://213213213123"
    ],
    "issuer": [
      "local-test-issuer"
    ],
    "secret": "change-this-local-test-secret",
    "jwks_url": "",
    "algorithms": [
      "HS256",
      "RS256"
    ],
    "test_token_enabled": true,
    "test_token_expiry_seconds": 3600
  }
}
```

The requested test-token audience must appear in the configured `jwt.audience` array.

## 4. Start the Server

Use either command:

```powershell
python run_server.py
```

```powershell
python -m run_server
```

Do not use:

```powershell
python -m run_server.py
```

## 5. Open Swagger

```text
http://localhost:8000/api/sample/docs
```

The `sample` segment comes from `route_name` in `config.json`.

## 6. Create a Test JWT

Call:

```text
POST /api/sample/auth/test-token
```

Request:

```json
{
  "email": "singh.badrinath@gmail.com",
  "audience": "api://213213213123"
}
```

The generated HS256 token contains these claims:

```json
{
  "email": "singh.badrinath@gmail.com",
  "aud": "api://213213213123",
  "iss": "local-test-issuer"
}
```

No Azure app registration is required for this local test token.

## 7. Authorize Swagger

Copy `data.access_token` from the token response.

Send it to protected endpoints as:

```text
Authorization: Bearer <access_token>
```

## 8. Test Health Checks

```text
GET /api/sample/health/
GET /api/sample/health/db
```

The database health endpoint tests the SQL Server connection configured in `config.json`.

Default local SQL Server configuration:

```json
{
  "database": {
    "type": "sqlserver",
    "server": "localhost\\SQLEXPRESS",
    "database": "master",
    "driver": "ODBC Driver 17 for SQL Server",
    "trusted_connection": true,
    "trust_server_certificate": true,
    "connection_string": ""
  }
}
```

## 9. Test Customer CRUD

```text
POST   /api/sample/customer/
GET    /api/sample/customer/
GET    /api/sample/customer/{customer_id}
PUT    /api/sample/customer/{customer_id}
DELETE /api/sample/customer/{customer_id}
```

Create request:

```json
{
  "first_name": "Badrinath",
  "last_name": "Singh",
  "email": "singh.badrinath@gmail.com",
  "phone": "555-0100"
}
```

## 10. Test External API Integration

Enable and configure `external_api` in `config.json`.

Call:

```text
POST /api/sample/external
```

Request:

```json
{
  "payload": {
    "customer_id": 1,
    "action": "verify"
  }
}
```

The service obtains an OAuth access token using client credentials and sends:

```text
Authorization: Bearer <access_token>
```

For local self-signed certificates:

```json
"verify_ssl": false
```

Keep SSL verification enabled in production.

## Troubleshooting

Missing `httpx`:

```powershell
python -m pip install -r requirements.txt
```

Audience is not allowed:

Add the requested audience to `jwt.audience` in `config.json`, then restart the server.

PowerShell server restart:

```powershell
Ctrl+C
python -m run_server
```
