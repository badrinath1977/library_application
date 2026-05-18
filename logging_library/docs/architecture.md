# Architecture

The library is organized around stable contracts and replaceable adapters.

## Core Flow

```text
get_logger("module")
  -> Logger level check
  -> lazy message evaluation
  -> safe serialization
  -> recursive masking
  -> immutable LogRecord
  -> formatter per output
  -> transport emit
```

## Layers

- `core`: owns `Logger`, `LogRecord`, level semantics, and interface contracts.
- `config`: owns config loading, defaults, runtime validation, and environment overrides.
- `context`: owns correlation ID, request ID, and async-safe contextual data.
- `serializers`: converts arbitrary Python objects and errors into JSON-safe structures.
- `masking`: recursively redacts configured sensitive keys and token patterns.
- `formatter`: converts `LogRecord` to JSON, text, or pretty console output.
- `transport`: writes payloads to console, files, or registered provider adapters.
- `middleware`: provides request/response logging for ASGI and WSGI frameworks.
- `adapters`: contains helper functions for domain-specific integration patterns.

## Extensibility

Custom transports implement `emit(payload, record)`, `flush()`, and `close()`, then register with:

```python
register_transport("provider-name", factory)
```

Custom formatters implement `format(record) -> str`. Provider-specific transports should isolate network clients, authentication, retry policy, and backpressure in adapter modules.

Built-in provider names such as `elk`, `splunk`, `datadog`, `cloudwatch`, `opentelemetry`, and `kafka` use the generic HTTP provider transport and require `options.endpoint`. Teams that need native SDK behavior can register a provider-specific transport under the same name.

## Dependency Direction

High-level application code depends on the facade. Core code depends on contracts, not provider implementations. Transports and formatters are replaceable without changing application logging calls.
