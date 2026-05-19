# AbsenceAPI

AbsenceAPI exposes employee absence search data to ChatAPI. It is a stored-procedure-only FastAPI service that calls `GenAI.sp_SearchEmployeeAbsence`.

It does not use inline data access, ORM table mapping, or direct table reads.

## Endpoints

- `GET /health`
- `GET /live`
- `GET /ready`
- `POST /api/absence/search`

Swagger:

- `http://localhost:8020/docs`
- `http://localhost:8020/redoc`

## Setup

```powershell
cd C:\Projects\Python-Library\MicroServices\AbsenceAPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.sample .env
python run_server.py
```

For local testing, `.env.sample` starts with `AUTH_ENABLED=false`. For secured environments, set `AUTH_ENABLED=true` and configure JWKS or a static public key.

## SQL Server

Default connection:

```text
DRIVER={ODBC Driver 17 for SQL Server};SERVER=localhost\SQLEXPRESS;DATABASE=genai_db;Trusted_Connection=yes;TrustServerCertificate=yes;
```

Only this stored procedure is called:

```text
GenAI.sp_SearchEmployeeAbsence
```

## Search Example

```bash
curl -X POST "http://localhost:8020/api/absence/search" \
  -H "Content-Type: application/json" \
  -d '{
    "personNumber": "41556",
    "personId": null,
    "personAbsenceEntryId": null,
    "absenceType": "Sick Time",
    "absenceTypeId": null,
    "absencePatternCd": null,
    "absenceStatusCd": null,
    "approvalStatusCd": "APPROVED",
    "absenceDispStatus": null,
    "startDateFrom": "2025-01-01",
    "startDateTo": "2025-12-31",
    "endDateFrom": null,
    "endDateTo": null,
    "submittedDateFrom": null,
    "submittedDateTo": null,
    "creationDateFrom": null,
    "creationDateTo": null,
    "lastUpdateDateFrom": null,
    "lastUpdateDateTo": null,
    "approvalDateFrom": null,
    "approvalDateTo": null,
    "durationMin": null,
    "durationMax": null,
    "unitOfMeasure": null,
    "commentsKeyword": null,
    "employer": null,
    "legalEntityId": null,
    "legislationCode": null,
    "absenceEntryBasicFlag": null,
    "employeeShiftFlag": null,
    "singleDayFlag": null,
    "openEndedFlag": null,
    "absenceUpdatableFlag": null,
    "createdBy": null,
    "lastUpdatedBy": null,
    "objectVersionNumber": null,
    "pageNumber": 1,
    "pageSize": 20,
    "sortColumn": "startDate",
    "sortDirection": "DESC"
  }'
```

## ChatAPI API_REGISTRY Metadata

Register this API in ConfigRegistryAPI for ChatAPI discovery:

```json
{
  "apiName": "search_absence",
  "intent": "absence_search",
  "intentKeywords": ["absence", "leave", "sick", "approved"],
  "baseUrl": "http://localhost:8020",
  "endpoint": "/api/absence/search",
  "method": "POST",
  "requiredParameters": ["personNumber", "startDateFrom", "startDateTo"],
  "parameterMapping": {
    "personNumber": "userId",
    "year": "year",
    "absenceType": {
      "values": {
        "sick": "Sick Time"
      }
    },
    "approvalStatusCd": {
      "values": {
        "approved": "APPROVED"
      },
      "default": "APPROVED"
    }
  },
  "requestBodyTemplate": {
    "personNumber": "$personNumber",
    "absenceType": "$absenceType",
    "approvalStatusCd": "$approvalStatusCd",
    "startDateFrom": "$startDateFrom",
    "startDateTo": "$startDateTo",
    "pageNumber": 1,
    "pageSize": 20,
    "sortColumn": "startDate",
    "sortDirection": "DESC"
  },
  "requiresConfirmation": false,
  "tags": ["absence", "search"]
}
```

## Security and Logging

- JWT protects `/api/absence/search` when enabled.
- Health endpoints are anonymous.
- PII fields are masked before structured logs.
- Technical exceptions are logged through `AppErrorDBLog_Library` fallback logging.
- Internal SQL errors are not exposed to clients.

## Docker

```powershell
cd C:\Projects\Python-Library
docker build -f MicroServices/AbsenceAPI/Dockerfile -t absence-api .
docker run --rm -p 8020:8020 --env-file MicroServices/AbsenceAPI/.env absence-api
```

Windows Authentication from Linux containers requires a domain identity strategy. For local development, running directly on Windows is usually simpler.

## Tests

```powershell
cd C:\Projects\Python-Library\MicroServices\AbsenceAPI
pytest
```

