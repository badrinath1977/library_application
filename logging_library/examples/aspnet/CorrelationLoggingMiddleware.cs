using System.Diagnostics;

public sealed class CorrelationLoggingMiddleware
{
    private const string HeaderName = "X-Correlation-ID";
    private readonly RequestDelegate _next;
    private readonly ILogger<CorrelationLoggingMiddleware> _logger;

    public CorrelationLoggingMiddleware(RequestDelegate next, ILogger<CorrelationLoggingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers.TryGetValue(HeaderName, out var existing)
            ? existing.ToString()
            : Guid.NewGuid().ToString();

        context.Response.Headers[HeaderName] = correlationId;
        using var scope = _logger.BeginScope(new Dictionary<string, object>
        {
            ["CorrelationId"] = correlationId,
            ["Path"] = context.Request.Path.ToString(),
            ["Method"] = context.Request.Method
        });

        var stopwatch = Stopwatch.StartNew();
        _logger.LogInformation("request.started");
        try
        {
            await _next(context);
            _logger.LogInformation(
                "request.completed statusCode={StatusCode} latencyMs={LatencyMs}",
                context.Response.StatusCode,
                stopwatch.Elapsed.TotalMilliseconds);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "request.failed latencyMs={LatencyMs}", stopwatch.Elapsed.TotalMilliseconds);
            throw;
        }
    }
}
