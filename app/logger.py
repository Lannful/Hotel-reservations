import logging
from datetime import UTC, datetime

from pythonjsonlogger import jsonlogger

from app.config import settings

logger = logging.getLogger("app")

# Предотвращаем дублирование обработчиков при повторных импортах
if not logger.handlers:
    logHandler = logging.StreamHandler()

    class CustomJsonFormatter(jsonlogger.JsonFormatter):
        def add_fields(self, log_record, record, message_dict):
            super(CustomJsonFormatter, self).add_fields(log_record, record, message_dict)
            if not log_record.get("timestamp"):
                now = datetime.now(UTC).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                log_record["timestamp"] = now
            if log_record.get("level"):
                log_record["level"] = log_record["level"].upper()
            else:
                log_record["level"] = record.levelname

    formatter = CustomJsonFormatter(
        "%(timestamp)s %(level)s %(message)s %(module)s %(funcName)s"
    )

    logHandler.setFormatter(formatter)
    logger.addHandler(logHandler)

# Преобразуем строковый уровень логирования в числовой
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logger.setLevel(log_level)