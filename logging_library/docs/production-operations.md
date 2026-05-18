# DevOps and Production Operations

## Docker

Use stdout logging:

```dockerfile
ENV LOGGING_FORMAT=json
ENV LOGGING_LEVEL=INFO
ENV LOGGING_ASYNC_ENABLED=true
```

Run the application with graceful shutdown handling so `shutdown()` is called on `SIGTERM`.

## Kubernetes

- Emit JSON to stdout.
- Let the node agent or sidecar forward logs to ELK, Splunk, Datadog, CloudWatch, or OpenTelemetry.
- Include application, environment, service, version, pod, namespace, and correlation ID metadata.
- Avoid file logging inside containers unless a sidecar explicitly consumes the file.

## Centralized Logging

Provider adapters should handle authentication, retry, circuit breaking, and backpressure. Keep application code bound to `get_logger()` and `logger.info()` rather than provider SDKs.

## Rotation Strategy

For non-container deployments, use rolling files with size limits and backup counts. Enable compression when retention is longer than a few rotations.

## Observability

Use logs with metrics and traces. Correlation IDs connect logs across services; OpenTelemetry trace IDs can be added as custom context by middleware or tracing integrations.
