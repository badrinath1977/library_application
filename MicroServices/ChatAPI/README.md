# ChatAPI

ChatAPI is a generic agentic orchestration microservice. It receives a UI chat request, loads runtime configuration from ConfigRegistryAPI, selects the correct downstream API, executes it, sends only verified downstream data to the configured LLM provider, and returns a clean response to the UI.

ChatAPI never connects to SQL Server and never reads `GenAI.AppConfig` directly.

## Flow

```text
UI
  -> ChatAPI
  -> ConfigRegistryAPI
  -> Downstream API
  -> LLM Provider
  -> ChatAPI
  -> UI
```

## Endpoints

- `GET /health`
- `GET /live`
- `GET /ready`
- `POST /api/chat`
- `POST /api/chat/stream`
- `GET /api/chat/history/{conversationId}`
- `POST /api/chat/feedback`

Swagger:

- `http://localhost:8010/docs`
- `http://localhost:8010/redoc`

## Setup

```powershell
cd C:\Projects\Python-Library\MicroServices\ChatAPI
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.sample .env
```

Start ConfigRegistryAPI first. For local testing, both services can use `AUTH_ENABLED=false`.

```powershell
python run_server.py
```

Health check:

```powershell
Invoke-WebRequest -UseBasicParsing http://localhost:8010/health
```

## Bootstrap Environment

Only bootstrap values live in `.env`:

```env
CONFIG_REGISTRY_BASE_URL=http://localhost:8000
CONFIG_REGISTRY_APPLICATION_NAME=ChatAPI
ENVIRONMENT_NAME=local
CONFIG_REGISTRY_BEARER_TOKEN=
AUTH_ENABLED=false
PORT=8010
```

All business behavior comes from ConfigRegistryAPI:

- `DEPARTMENT_APP_MAPPING`
- `API_REGISTRY`
- `LLM_CONFIG`
- `PROMPT_CONFIG`
- `AGENT_POLICY`
- `TOKEN_POLICY`
- `CACHE_POLICY`
- `AUTH_POLICY`

## Required ConfigRegistry Values

`DEPARTMENT_APP_MAPPING` is fetched using `CONFIG_REGISTRY_APPLICATION_NAME` and `ENVIRONMENT_NAME`.

Example `ConfigValue`:

```json
{
  "departments": {
    "HR": "HR-Agent-App",
    "FINANCE": "Finance-Agent-App"
  }
}
```

After the department resolves to an application name, ChatAPI loads the rest of the config using that application name.

### API_REGISTRY Example

```json
{
  "apis": [
    {
      "apiName": "search_absence",
      "intent": "absence_search",
      "intentKeywords": ["absence", "leave", "sick", "approved"],
      "baseUrl": "http://localhost:8020",
      "endpoint": "/api/absence/search",
      "method": "GET",
      "requiredParameters": ["personNumber", "startDateFrom", "startDateTo"],
      "parameterMapping": {
        "personNumber": "userId",
        "year": "year",
        "absenceType": {
          "values": {
            "sick": "Sick Time",
            "vacation": "Vacation"
          }
        },
        "approvalStatusCd": {
          "values": {
            "approved": "APPROVED",
            "pending": "PENDING"
          },
          "default": "APPROVED"
        }
      },
      "queryParameters": {
        "personNumber": "$personNumber",
        "absenceType": "$absenceType",
        "approvalStatusCd": "$approvalStatusCd",
        "startDateFrom": "$startDateFrom",
        "startDateTo": "$startDateTo"
      },
      "timeout": 30,
      "retryCount": 1,
      "requiresConfirmation": false,
      "tags": ["absence", "search"]
    }
  ]
}
```

### LLM_CONFIG Example

The current shared `llm_platform_library` supports the configured provider abstraction. Its local implementation includes `mock`; future providers can sit behind the same library facade.

```json
{
  "Provider": "mock",
  "DefaultModel": "mock-model",
  "LogLocation": "logs",
  "PromptFolder": "prompts",
  "Departments": {
    "HR": ["leave", "absence"]
  },
  "ModelPricing": {
    "mock-model": {
      "InputPer1KTokens": 0,
      "OutputPer1KTokens": 0
    }
  }
}
```

### PROMPT_CONFIG Example

```json
{
  "systemPrompt": "Use only verified downstream API response. Do not hallucinate. Do not invent dates, statuses, balances, names, or IDs. If data is missing, say it is unavailable. Do not expose chain-of-thought. Provide a concise professional response."
}
```

### AGENT_POLICY Example

```json
{
  "allowImmediateWrites": false,
  "requireConfirmationForMethods": ["POST", "PUT", "PATCH", "DELETE"]
}
```

## Chat Request

```bash
curl -X POST "http://localhost:8010/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "HR",
    "userId": "41556",
    "conversationId": "conv-001",
    "message": "Show me all my approved sick leaves for 2025"
  }'
```

## Streaming Request

```bash
curl -N -X POST "http://localhost:8010/api/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{
    "department": "HR",
    "userId": "41556",
    "conversationId": "conv-001",
    "message": "Summarize my leave history"
  }'
```

The streaming endpoint uses server-sent events. The request body does not include a stream flag.

## Conversation History

ChatAPI stores conversation memory internally by `conversationId`:

- recent message window
- compact summary
- previous extracted entities
- previous API execution context
- pending write actions

The UI should send only `conversationId`, not the full history.

## Write Safety

For `POST`, `PUT`, `PATCH`, and `DELETE`, ChatAPI returns `confirmation_required` unless policy allows immediate writes. Pending actions are stored internally and expire by TTL.

## Security

- JWT protects all non-health endpoints when `AUTH_ENABLED=true`.
- Raw secrets and PII are masked before logging.
- LLM prompts are not exposed unless internal debugging is deliberately enabled.
- Chain-of-thought is never returned.
- Downstream API endpoints and LLM provider/model are configuration-driven.

## Docker

```powershell
cd C:\Projects\Python-Library
docker build -f MicroServices/ChatAPI/Dockerfile -t chat-api .
docker run --rm -p 8010:8010 --env-file MicroServices/ChatAPI/.env chat-api
```

## Tests

```powershell
cd C:\Projects\Python-Library\MicroServices\ChatAPI
pytest
```

