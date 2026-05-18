# Configuration Guide

Configuration can come from dictionaries, JSON files, YAML files, environment variables, and runtime overrides.

## Example

```json
{
  "enabled": true,
  "level": "INFO",
  "format": "json",
  "outputs": [
    { "type": "console", "format": "json" },
    {
      "type": "file",
      "path": "logs/app.log",
      "rolling_policy": {
        "max_bytes": 10485760,
        "backup_count": 5,
        "compression": true
      }
    }
  ],
  "metadata": {
    "application": "billing-platform",
    "environment": "production",
    "service": "payments-api",
    "version": "1.0.0"
  },
  "masking": {
    "enabled": true,
    "mask": "***MASKED***"
  },
  "async": {
    "enabled": true,
    "queue_size": 10000,
    "batch_size": 100,
    "flush_interval_seconds": 1
  }
}
```

## Provider Gateway Output

```json
{
  "type": "opentelemetry",
  "format": "json",
  "options": {
    "endpoint": "https://collector.example.com/v1/logs",
    "timeout_seconds": 2,
    "headers": {
      "authorization": "Bearer ${TOKEN}"
    }
  }
}
```

Provider headers are masked when logged as metadata by application code, but configuration files should still be stored in a secret-safe configuration system.

## Environment Variables

- `LOGGING_ENABLED`
- `LOGGING_LEVEL`
- `LOGGING_FORMAT`
- `LOGGING_APPLICATION`
- `LOGGING_ENVIRONMENT`
- `LOGGING_SERVICE`
- `LOGGING_VERSION`
- `LOGGING_ASYNC_ENABLED`
- `LOGGING_ASYNC_QUEUE_SIZE`
- `LOGGING_ASYNC_BATCH_SIZE`
- `LOGGING_MASKING_ENABLED`
- `LOGGING_MASK_VALUE`
- `LOGGING_SANITIZE_NEWLINES`

## Runtime Overrides

```python
initialize_logger("logging.json", overrides={"level": "DEBUG"})
```

Runtime overrides have the highest precedence.
