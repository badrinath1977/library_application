from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.auth_middleware import jwt_auth_middleware
from app.api.middleware.correlation_middleware import correlation_id_middleware
from app.api.middleware.exception_middleware import handle_exception
from app.api.middleware.exception_middleware import exception_middleware
from app.api.middleware.logging_middleware import request_response_logging_middleware
from app.api.routes.auth_routes import router as auth_router
from app.api.routes.customer_routes import router as customer_router
from app.api.routes.health_routes import router as health_router
from app.api.routes.sample_routes import router as sample_router
from app.core.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.settings = settings
    yield


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.service_name,
        version=settings.api_version,
        docs_url=settings.swagger_docs_path,
        redoc_url=settings.swagger_redoc_path,
        openapi_url=settings.swagger_openapi_path,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )

    app.middleware("http")(exception_middleware)
    app.middleware("http")(request_response_logging_middleware)
    app.middleware("http")(jwt_auth_middleware)
    app.middleware("http")(correlation_id_middleware)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return handle_exception(
            request,
            exc,
            422,
            "VALIDATION_FAILED",
            "Validation failed",
            exc.errors(),
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return handle_exception(
            request,
            exc,
            exc.status_code,
            "HTTP_ERROR",
            str(exc.detail),
        )

    app.include_router(health_router, prefix=settings.service_base_path)
    app.include_router(auth_router, prefix=settings.service_base_path)
    app.include_router(sample_router, prefix=settings.service_base_path)
    app.include_router(customer_router, prefix=settings.service_base_path)
    return app


app = create_app()
