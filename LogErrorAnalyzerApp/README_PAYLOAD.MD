# API Request Payloads

This file contains example request payloads for the LogErrorAnalyzerApp API endpoints.

## Health

No request payload is required for the health endpoint.

Request:
```http
GET /health HTTP/1.1
Host: 127.0.0.1:8000
```

## Analyze Log

POST `/analyze-log`

Request body example:
```json
{
  "path": "sample_logs",
  "recursive": true,
  "call_llm": true,
  "create_ticket": true,
  "extensions": [
    ".txt",
    ".log"
  ]
}
```

Example curl command:
```bash
curl -X POST http://127.0.0.1:8000/analyze-log \
  -H "Content-Type: application/json" \
  -d '{
    "path": "sample_logs",
    "recursive": true,
    "call_llm": true,
    "create_ticket": true,
    "extensions": [".txt", ".log"]
  }'
```

Alternative single-file request:
```json
{
  "path": "sample_logs/node_error.txt",
  "recursive": false,
  "call_llm": true,
  "create_ticket": false
}
```

## Create Ticket

POST `/create-ticket`

Request body example:
```json
{
  "error_id": "REPLACE_WITH_ERROR_ID"
}
```

Example curl command:
```bash
curl -X POST http://127.0.0.1:8000/create-ticket \
  -H "Content-Type: application/json" \
  -d '{"error_id": "REPLACE_WITH_ERROR_ID"}'
```

## Get Error

GET `/errors/{error_id}`

No request body is required. Replace `{error_id}` with the ID returned from `/analyze-log`.

Example curl command:
```bash
curl http://127.0.0.1:8000/errors/REPLACE_WITH_ERROR_ID
```
