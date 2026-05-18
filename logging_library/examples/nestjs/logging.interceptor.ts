import {
  CallHandler,
  ExecutionContext,
  Injectable,
  NestInterceptor,
} from "@nestjs/common";
import { randomUUID } from "crypto";
import { Observable, tap } from "rxjs";

@Injectable()
export class EnterpriseLoggingInterceptor implements NestInterceptor {
  constructor(private readonly logger: any) {}

  intercept(context: ExecutionContext, next: CallHandler): Observable<unknown> {
    const http = context.switchToHttp();
    const request = http.getRequest();
    const response = http.getResponse();
    const correlationId = request.headers["x-correlation-id"] || randomUUID();
    const started = process.hrtime.bigint();

    request.correlationId = correlationId;
    response.setHeader("x-correlation-id", correlationId);
    this.logger.child({ correlationId, method: request.method, path: request.url }).info("request.started");

    return next.handle().pipe(
      tap(() => {
        const latencyMs = Number(process.hrtime.bigint() - started) / 1_000_000;
        this.logger.child({ correlationId }).info("request.completed", {
          method: request.method,
          path: request.url,
          statusCode: response.statusCode,
          latencyMs,
        });
      }),
    );
  }
}
