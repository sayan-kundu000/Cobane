import logging
import os
from logging.handlers import RotatingFileHandler

# Log directories layout configurations
LOG_DIR = "logs"
LOG_CATEGORIES = ["app", "security", "ai", "analysis", "database", "tasks", "api"]

for category in LOG_CATEGORIES:
    os.makedirs(os.path.join(LOG_DIR, category), exist_ok=True)

# Standard log output pattern
LOG_FORMAT = "%(asctime)s [%(levelname)s] [%(name)s] [ReqID: %(request_id)s] %(message)s"


class RequestIDFilter(logging.Filter):
    """Logging filter that injects request_id from ContextVar into record tags."""

    def filter(self, record):
        from app.core.responses import request_id_context

        record.request_id = request_id_context.get()
        return True


def configure_logger(name: str, log_file_path: str, level=logging.INFO) -> logging.Logger:
    """Configures a logger with standard formatting and rotating file handlers."""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    # Avoid duplicate handlers
    if not logger.handlers:
        formatter = logging.Formatter(LOG_FORMAT)

        # Stream console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.addFilter(RequestIDFilter())
        logger.addHandler(console_handler)

        # Rotating File handler (5 MB size rotation threshold, maximum 5 backups)
        file_handler = RotatingFileHandler(log_file_path, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(RequestIDFilter())
        logger.addHandler(file_handler)

    return logger


app_logger = configure_logger("cobane.app", os.path.join(LOG_DIR, "app", "app.log"))
api_logger = configure_logger("cobane.api", os.path.join(LOG_DIR, "api", "api.log"))
security_logger = configure_logger("cobane.security", os.path.join(LOG_DIR, "security", "security.log"))
ai_logger = configure_logger("cobane.ai", os.path.join(LOG_DIR, "ai", "ai.log"))
analysis_logger = configure_logger("cobane.analysis", os.path.join(LOG_DIR, "analysis", "analysis.log"))
database_logger = configure_logger("cobane.database", os.path.join(LOG_DIR, "database", "database.log"))
tasks_logger = configure_logger("cobane.tasks", os.path.join(LOG_DIR, "tasks", "tasks.log"))
