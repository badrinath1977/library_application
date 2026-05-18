const { randomUUID } = require("crypto");

function enterpriseLoggingMiddleware(logger, options = {}) {
  const headerName = (options.headerName || "x-correlation-id").toLowerCase();

  return function requestLogger(req, res, next) {
    const correlationId = req.headers[headerName] || randomUUID();
    const started = process.hrtime.bigint();
    req.correlationId = correlationId;
    res.setHeader(headerName, correlationId);

    logger.child({ correlationId, method: req.method, path: req.originalUrl }).info("request.started");

    res.on("finish", () => {
      const latencyMs = Number(process.hrtime.bigint() - started) / 1_000_000;
      logger.child({ correlationId }).info("request.completed", {
        method: req.method,
        path: req.originalUrl,
        statusCode: res.statusCode,
        latencyMs
      });
    });

    next();
  };
}

module.exports = { enterpriseLoggingMiddleware };
