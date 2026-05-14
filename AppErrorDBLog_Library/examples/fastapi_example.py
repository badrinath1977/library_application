from fastapi import FastAPI

from app_error_db_log import AppErrorLogger
from app_error_db_log.fastapi_middleware import AppErrorDBLogMiddleware

logger = AppErrorLogger.from_config_file("config.json")
app = FastAPI()
app.add_middleware(AppErrorDBLogMiddleware, logger=logger)


@app.get("/fail")
def fail() -> None:
    raise RuntimeError("Example failure")

