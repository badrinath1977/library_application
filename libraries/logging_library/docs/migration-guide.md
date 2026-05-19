# Migration Guide

## From Python Standard Logging

Replace module loggers:

```python
logger = logging.getLogger(__name__)
```

with:

```python
logger = get_logger(__name__)
```

Move formatter, handler, level, and file settings into application configuration. Replace string interpolation with structured metadata:

```python
logger.info("order.created", {"orderId": order_id})
```

## From Print Debugging

Replace prints with named events and metadata. Use `DEBUG` for diagnostic details and keep `INFO` for business or lifecycle events.

## From Application-Specific Loggers

Register provider transports instead of embedding vendor SDK calls throughout application code. Keep logging calls vendor-neutral.
