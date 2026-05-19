# Troubleshooting

## No Logs Appear

- Confirm `enabled=true`.
- Confirm the event level is greater than or equal to configured `level`.
- Call `flush()` or `shutdown()` when testing async mode.
- Validate output configuration.

## File Logs Are Missing

- Confirm `outputs[].type=file`.
- Confirm `path` is configured.
- Confirm the process has write access to the directory.

## Correlation ID Is Missing

- Ensure request middleware is installed at the application edge.
- Confirm async tasks are created inside the active request context.
- Confirm downstream services forward `X-Correlation-ID`.

## Sensitive Values Are Visible

- Add field names to `masking.sensitive_keys`.
- Add token patterns to `masking.sensitive_patterns`.
- Avoid logging raw bodies where schema is unknown.

## High Latency

- Keep async mode enabled.
- Increase `queue_size` and `batch_size`.
- Avoid huge payloads; use IDs and summaries.
- Prefer stdout collection for containers.
