"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI

from libraries.LogErrorAnalyzerApp.app.api.routes import router
from libraries.LogErrorAnalyzerApp.app.core.config import get_settings
from libraries.LogErrorAnalyzerApp.app.core.logging_config import configure_logging

settings = get_settings()
configure_logging(settings)

app = FastAPI(title=settings.app_name, version="0.1.0")
app.include_router(router)

