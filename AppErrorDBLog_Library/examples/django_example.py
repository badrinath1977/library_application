from app_error_db_log import AppErrorLogger
from app_error_db_log.django_middleware import AppErrorDBLogDjangoMiddleware

logger = AppErrorLogger.from_config_file("config.json")

# In production, wire this in Django settings MIDDLEWARE and inject the logger
# through your application factory or dependency container.
middleware = AppErrorDBLogDjangoMiddleware(lambda request: None, logger=logger)

