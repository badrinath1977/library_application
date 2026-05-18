# Enterprise Logging Library

Production-grade reusable Python logging framework for structured logs, correlation tracing, sensitive data protection, async dispatch, rolling files, and pluggable centralized logging transports.

## Install

```bash
pip install enterprise-logging-library
pip install enterprise-logging-library[yaml]
```

## Quick Start

```python
from enterprise_logging import get_logger, initialize_logger, request_context, shutdown

initialize_logger("logging.json")
logger = get_logger("orders.service")

with request_context(correlation_id="corr-123", tenantId="tenant-a"):
    logger.info("order.created", {"orderId": "o-100", "apiKey": "secret"})

shutdown()
```

## Public API

- `initialize_logger(config, overrides=None)`
- `get_logger(module_name=None)`
- `logger.trace/debug/info/warn/error/fatal(message, data?)`
- `logger.error(message, error_or_data?, data?)`
- `logger.child(context)`
- `with_correlation_id(id)`
- `set_log_level(level)`
- `flush()`
- `shutdown()`
- `register_transport(name, factory)`

Messages may be strings or lazy callables. Lazy messages are not evaluated when the level is disabled.

## Features

- Levels: `TRACE`, `DEBUG`, `INFO`, `WARN`, `ERROR`, `FATAL`
- Formats: JSON, plain text, colorized pretty console
- Outputs: console, rolling file, multiple simultaneous outputs
- Future transports: ELK, Splunk, Datadog, CloudWatch, OpenTelemetry, Kafka
- Config sources: JSON, YAML, environment variables, runtime overrides
- Metadata: app, environment, service, module, host, process, thread, version, custom values
- Async-safe correlation via `contextvars`
- Recursive immutable masking with circular reference safety
- Serialization-safe exception logging with nested causes and stack traces
- Custom transports, formatters, serializers, and masking rules

## Configuration

See [examples/config/logging.json](examples/config/logging.json) and [docs/configuration.md](docs/configuration.md).

Environment variables use the `LOGGING_` prefix:

```bash
LOGGING_LEVEL=DEBUG
LOGGING_APPLICATION=billing-platform
LOGGING_ENVIRONMENT=production
LOGGING_SERVICE=payments-api
LOGGING_ASYNC_ENABLED=true
LOGGING_MASKING_ENABLED=true
```

## Architecture

```text
application code
  -> enterprise_logging facade
  -> Logger
  -> SafeSerializer -> SensitiveDataMasker
  -> LogRecord
  -> Formatter
  -> Transport
  -> Console / Rolling File / Custom Provider
```

Clean architecture modules:

- `core`: public logger, records, contracts, dispatcher
- `config`: schema, validation, loaders, env overrides
- `formatter`: JSON, text, pretty
- `transport`: console, rolling file, async dispatcher, provider registry
- `context`: async-safe correlation and request context
- `masking`: sensitive data protection
- `serializers`: safe object and exception serialization
- `middleware`: ASGI and WSGI request logging
- `adapters`: HTTP/API helpers
- `examples`, `tests`, `docs`

## Production Defaults

Use JSON logs to stdout in containers, include correlation IDs at ingress, enable masking, keep async mode enabled, and call `shutdown()` during graceful termination so buffers are flushed.

## Verification

```bash
pytest
ruff check .
mypy enterprise_logging
```
