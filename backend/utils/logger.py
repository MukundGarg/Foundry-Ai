"""
Logging setup.

- Development: human-readable stdout with timestamps
- Production (APP_ENV=production): JSON structured logs for log aggregators
"""

import logging
import sys
import json
import os
from datetime import datetime, timezone


class _JsonFormatter(logging.Formatter):
    """Emit one JSON object per log line — compatible with Datadog, CloudWatch, etc."""

    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


class _HumanFormatter(logging.Formatter):
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        env = os.getenv("APP_ENV", "development")
        handler.setFormatter(
            _JsonFormatter() if env == "production" else _HumanFormatter()
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
