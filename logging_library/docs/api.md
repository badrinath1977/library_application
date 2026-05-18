# API Documentation

## Initialization

```python
initialize_logger(config=None, overrides=None)
```

`config` can be a dictionary, JSON/YAML file path, `LoggerConfig`, or `None`.

## Logger Retrieval

```python
logger = get_logger("module.name")
```

The module name is included in every emitted record.

## Logging Methods

```python
logger.trace(message, data=None)
logger.debug(message, data=None)
logger.info(message, data=None)
logger.warn(message, data=None)
logger.error(message, error_or_data=None, data=None)
logger.fatal(message, error_or_data=None, data=None)
```

`message` may be a string or a zero-argument callable. `error` and `fatal` accept an exception as the second argument and optional metadata as the third argument.

## Child Loggers

```python
payment_logger = logger.child({"component": "payment-gateway"})
```

Child logger context is inherited into every record from that logger.

## Correlation

```python
with with_correlation_id("corr-123"):
    logger.info("event")
```

For request scoped values:

```python
with request_context(correlation_id="corr-123", tenantId="tenant-a"):
    logger.info("event")
```

## Runtime Controls

```python
set_log_level("DEBUG")
flush()
shutdown()
```

`flush()` blocks until queued records are written. `shutdown()` flushes and closes transports.
