from enterprise_logging import get_logger, initialize_logger, request_context, shutdown

initialize_logger("examples/config/logging.json")
logger = get_logger("orders.repository")

with request_context(correlation_id="corr-123", tenantId="tenant-a"):
    logger.info("order.created", {"orderId": "o-100", "apiKey": "should-not-leak"})
    try:
        raise RuntimeError("database timeout")
    except RuntimeError as exc:
        logger.error("order.persist.failed", exc, {"orderId": "o-100"})

shutdown()
