const fp = require("fastify-plugin");
const { randomUUID } = require("crypto");

module.exports = fp(async function enterpriseLoggingPlugin(fastify, options) {
  const logger = options.logger;
  const headerName = (options.headerName || "x-correlation-id").toLowerCase();

  fastify.addHook("onRequest", async (request, reply) => {
    const correlationId = request.headers[headerName] || randomUUID();
    request.correlationId = correlationId;
    request.startedAt = process.hrtime.bigint();
    reply.header(headerName, correlationId);
    logger.child({ correlationId, method: request.method, path: request.url }).info("request.started");
  });

  fastify.addHook("onResponse", async (request, reply) => {
    const latencyMs = Number(process.hrtime.bigint() - request.startedAt) / 1_000_000;
    logger.child({ correlationId: request.correlationId }).info("request.completed", {
      method: request.method,
      path: request.url,
      statusCode: reply.statusCode,
      latencyMs
    });
  });
});
