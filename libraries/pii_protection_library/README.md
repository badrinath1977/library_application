# PII Protection Library

`pii_protection` is a production-ready Python 3.11+ library for protecting personally identifiable information before sending payloads to an LLM and restoring approved values afterward.

## Overview

The library is config-driven, JSONPath-based, regex-validated, and action-oriented. Parent applications provide a JSON configuration that tells the library where PII lives and how each value should be transformed.

## Why This Library Exists

LLM workflows should not send raw PII to model providers. This library lets applications tokenize, mask, redact, hash, drop, or encrypt sensitive values before LLM processing, then restore reversible placeholders only when policy allows it.

## Architecture

```text
Ingestor / Parent Application
  -> pii_protection.protect()
  -> protected payload
  -> LLM processing
  -> pii_protection.restore()
  -> final payload with approved PII restored
```

Core modules:

- `models.py`: Pydantic config, context, result, and mapping models
- `config_loader.py`: JSON config loading and validation
- `scanner.py`: JSONPath scanning with `jsonpath-ng`
- `validators.py`: regex validation
- `processors/`: action implementations
- `store/`: mapping store contracts and in-memory store
- `crypto/`: key provider and AES-GCM support
- `audit.py`: audit logging protocol and no-op implementation
- `service.py`: orchestration and public service methods

## Installation

```bash
pip install pii-protection
```

For local development:

```bash
pip install -e ".[dev,fastapi]"
```

## Quick Start

```python
from pii_protection import protect, restore

config = {
    "application": "loan-service",
    "version": "1.0",
    "restorePolicy": {
        "enabled": True,
        "allowedRoles": ["PII_ADMIN"],
        "requireReason": True,
        "audit": True,
    },
    "keyConfig": {"keyProvider": "ENV", "key1Ref": "PII_KEY_1", "key2Ref": "PII_KEY_2"},
    "rules": [
        {
            "name": "email",
            "jsonPath": "$.customer.email",
            "type": "EMAIL",
            "regex": "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
            "action": {"type": "TOKENIZE", "restore": True},
        }
    ],
}

context = {
    "correlationId": "corr-123",
    "roles": {"PII_ADMIN"},
    "reason": "support case",
}

protected = protect({"customer": {"email": "badri@gmail.com"}}, config, context)
restored = restore("Email {{PII_EMAIL_001}}", protected.correlation_id, config, context)
```

## Protect Example

Input:

```json
{
  "customer": {
    "name": "Badri Singh",
    "email": "badri@gmail.com",
    "phone": "9876543210"
  }
}
```

Protected:

```json
{
  "customer": {
    "name": "{{PII_NAME_001}}",
    "email": "{{PII_EMAIL_001}}",
    "phone": "{{PII_PHONE_001}}"
  }
}
```

## Restore Example

LLM output:

```text
Customer {{PII_NAME_001}} can be contacted at {{PII_EMAIL_001}}
```

Restored:

```text
Customer Badri Singh can be contacted at badri@gmail.com
```

## Full Config Schema

```json
{
  "application": "loan-service",
  "version": "1.0",
  "restorePolicy": {
    "enabled": true,
    "allowedRoles": ["PII_ADMIN", "SUPPORT_L2"],
    "requireReason": true,
    "audit": true
  },
  "keyConfig": {
    "keyProvider": "ENV",
    "key1Ref": "PII_KEY_1",
    "key2Ref": "PII_KEY_2"
  },
  "rules": [
    {
      "name": "customer-name",
      "jsonPath": "$.customer.name",
      "type": "NAME",
      "regex": "^[A-Za-z .'-]{2,100}$",
      "action": {
        "type": "TOKENIZE",
        "restore": true,
        "params": {
          "tokenFormat": "{{PII_${type}_${sequence}}}"
        }
      }
    },
    {
      "name": "email",
      "jsonPath": "$.customer.email",
      "type": "EMAIL",
      "regex": "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
      "action": {
        "type": "TOKENIZE",
        "restore": true
      }
    },
    {
      "name": "phone",
      "jsonPath": "$.customer.phone",
      "type": "PHONE",
      "regex": "^[0-9]{10}$",
      "action": {
        "type": "TOKENIZE",
        "restore": true
      }
    },
    {
      "name": "ssn",
      "jsonPath": "$.customer.ssn",
      "type": "SSN",
      "regex": "^(?!000|666)[0-9]{3}-?(?!00)[0-9]{2}-?(?!0000)[0-9]{4}$",
      "action": {
        "type": "TOKENIZE",
        "restore": true
      }
    },
    {
      "name": "password",
      "jsonPath": "$.credentials.password",
      "type": "PASSWORD",
      "regex": "^.*$",
      "action": {
        "type": "DROP",
        "restore": false
      }
    },
    {
      "name": "api-key",
      "jsonPath": "$.headers.apiKey",
      "type": "API_KEY",
      "regex": "^.*$",
      "action": {
        "type": "REDACT",
        "restore": false
      }
    }
  ]
}
```

## Supported PII Types

`NAME`, `FIRST_NAME`, `LAST_NAME`, `EMAIL`, `PHONE`, `SSN`, `PAN`, `AADHAAR`, `PASSPORT`, `DRIVER_LICENSE`, `CREDIT_CARD`, `DEBIT_CARD`, `BANK_ACCOUNT`, `IBAN`, `IP_ADDRESS`, `MAC_ADDRESS`, `DOB`, `ADDRESS`, `ZIP_CODE`, `USERNAME`, `PASSWORD`, `API_KEY`, `ACCESS_TOKEN`, `REFRESH_TOKEN`, `FREE_TEXT`, `CUSTOM`.

## Regex Examples

```json
{
  "EMAIL": "^[A-Za-z0-9+_.-]+@[A-Za-z0-9.-]+$",
  "PHONE": "^[0-9]{10}$",
  "SSN": "^(?!000|666)[0-9]{3}-?(?!00)[0-9]{2}-?(?!0000)[0-9]{4}$",
  "ZIP_CODE": "^[0-9]{5}(-[0-9]{4})?$",
  "IP_ADDRESS": "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)(\\.|$)){4}$"
}
```

## Action Types

- `MASK`: replace value with a fixed mask
- `PARTIAL_MASK`: preserve selected leading/trailing characters
- `REDACT`: replace with semantic label
- `DROP`: remove the JSON field
- `HASH`: deterministic HMAC-SHA256
- `TOKENIZE`: reversible LLM-safe placeholder
- `ENCRYPT`: AES-GCM encrypted value
- `FORMAT_PRESERVING_TOKENIZE`: reversible fake-looking value

## Action Comparison Table

| Action | Reversible | LLM Safe | Use Case |
|---|---|---|---|
| MASK | No | Yes | Hide value permanently |
| PARTIAL_MASK | No | Partial | Display/debug |
| REDACT | No | Yes | Logs |
| DROP | No | Yes | Remove secrets |
| HASH | No | Yes | Matching/dedup |
| TOKENIZE | Yes | Yes | Best for LLM |
| ENCRYPT | Yes | Yes, but not ideal for LLM text | Secure storage |
| FORMAT_PRESERVING_TOKENIZE | Yes | Yes | Structured fake values |

## Recommended Action By PII Type

- Names, email, phone, address, DOB: `TOKENIZE`
- Passwords, API keys, access tokens, refresh tokens: `DROP` or `REDACT`
- SSN, PAN, Aadhaar, passport, driver license: `TOKENIZE` or `ENCRYPT`
- Credit/debit cards, bank accounts, IBAN: `TOKENIZE`, `ENCRYPT`, or `HASH`
- IP/MAC address: `TOKENIZE` or `HASH`
- Free text: `TOKENIZE` for known paths; pair with upstream entity detection for unstructured text

## LLM Workflow

For LLM workflows, `TOKENIZE` is preferred because the LLM can preserve placeholders and the library can restore them afterward.

Example:

```text
badri@gmail.com -> {{PII_EMAIL_001}}
```

Do not send raw PII to the LLM.

## Restore Policy

Restore is controlled by:

- `restorePolicy.enabled`
- `restorePolicy.allowedRoles`
- `restorePolicy.requireReason`
- per-action `restore`

Restore fails if the caller lacks an allowed role or a required reason.

## Key Management

`HASH` and `ENCRYPT` use keys from `keyConfig`.

The built-in `EnvKeyProvider` reads:

- `key1Ref` for AES-GCM encryption material
- `key1Ref + key2Ref` for HMAC key derivation

Do not hardcode secrets. In production, inject a custom key provider backed by KMS, Vault, or your cloud secrets manager.

## Mapping Store

`TOKENIZE` and format-preserving tokenization save mappings by `correlation_id`. The built-in `InMemoryPiiMappingStore` is intended for local development and single-process tests.

Production applications should provide a secure external mapping store with TTL support.

## Audit Logging

The `AuditLogger` protocol receives safe metadata only:

- event name
- correlation/request/user context
- counts and rule metadata

Audit details must never contain raw PII.

## FastAPI Sample

See [examples/fastapi/app.py](examples/fastapi/app.py).

Run:

```bash
pip install -e ".[fastapi]"
uvicorn examples.fastapi.app:app --reload
```

Endpoints:

- `POST /pii/protect`
- `POST /pii/restore`

## Error Handling

Common exceptions:

- `PiiConfigError`
- `PiiValidationError`
- `PiiRestoreDeniedError`
- `PiiMappingNotFoundError`
- `PiiCryptoError`

## Extension Guide

Add a new action by implementing `PiiActionProcessor` and registering it in `PiiActionProcessorFactory`. Add a custom mapping store by implementing `PiiMappingStore`. Add a secure key source by implementing `KeyProvider`.

## How Parent Applications Should Use It

1. Load app-specific config at startup.
2. Inject a production mapping store and audit logger.
3. Call `protect()` before LLM calls.
4. Pass only protected payloads to LLMs.
5. Call `restore()` only after authorization checks.
6. Retain correlation IDs for the workflow lifecycle.

## Best Practices

- Prefer `TOKENIZE` for LLM workflows.
- Use `DROP` for secrets that should never be restored.
- Keep restore roles narrow.
- Require a restore reason in production.
- Use short TTLs for mappings.
- Keep raw PII out of logs, traces, metrics, and audit payloads.
- Validate issuer/application-level authorization before restore.

## Limitations

- JSONPath scanning is config-driven; unconfigured PII paths are not transformed.
- Built-in memory store is not distributed or durable.
- Format-preserving tokenization is deterministic per process only for simple formats.
- Free-text entity detection is out of scope for this package.

## Future Enhancements

- Built-in Vault/KMS mapping stores
- Structured secret manager key providers
- Entity detection for unstructured free text
- Streaming payload support
- OpenTelemetry audit integration

## Pytest Usage

```bash
pip install -e ".[dev]"
pytest
```
