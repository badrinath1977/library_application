from flask import Flask

from app_error_db_log import AppErrorLogger
from app_error_db_log.flask_integration import register_flask_error_handler

app = Flask(__name__)
logger = AppErrorLogger.from_config_file("config.json")
register_flask_error_handler(app, logger)


@app.get("/fail")
def fail() -> None:
    raise RuntimeError("Example failure")

