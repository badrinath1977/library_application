# Integration Guide

## Python ASGI

```python
from enterprise_logging.middleware import CorrelationASGIMiddleware

app = CorrelationASGIMiddleware(app)
```

Works with Starlette, FastAPI, and other ASGI frameworks.

## Python WSGI

```python
from enterprise_logging.middleware import CorrelationWSGIMiddleware

app = CorrelationWSGIMiddleware(app)
```

Works with Flask, Django WSGI deployments, and generic WSGI applications.

## Express.js, NestJS, Fastify, Spring Boot, ASP.NET

Examples are included under `examples/`. These snippets standardize correlation header propagation, request start/completion events, latency tracking, and status code capture.

## Generic REST Standard

- Read `X-Correlation-ID` or generate one.
- Add it to request scoped logging context.
- Return the same header in the response.
- Log `request.started` and `request.completed`.
- Log method, path, status code, latency, and sanitized error details.
