# Best Practices

- Prefer JSON logs in production.
- Log to stdout/stderr in containers; let the platform collect logs.
- Use rolling files only for VM or bare-metal deployments.
- Never log raw request bodies unless explicitly approved and masked.
- Treat authorization, cookie, session, token, key, and secret fields as sensitive.
- Use stable event names such as `order.created` and `request.completed`.
- Put high-cardinality values in metadata, not in the message.
- Always propagate `X-Correlation-ID` across service boundaries.
- Use `logger.child()` for component-specific context.
- Call `flush()` before critical process exits and `shutdown()` during graceful termination.
- Keep `fail_fast=false` for application logs unless logs are compliance-critical.
