from __future__ import annotations
import json
import logging
import sys
import time 
from typing import Any, Dict

class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        base: Dict[str, Any] = {
            "ts": round(time.time(), 3),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        # merge extras if present
        if hasattr(record, "__dict__"):
            extras = {
                k: v for k, v in record.__dict__.items()
                if k not in vars(logging.LogRecord("",0,"","", "", (), None))
                and k not in ("args", "msg")
            }
            if extras:
                base.update(extras)
        return json.dumps(base, ensure_ascii=False)

def setup_logging(level: str = "INFO") -> None:
    root = logging.getLogger()
    root.setLevel(level.upper())
    # remove existing handlers (avoid duplicates under uvicorn/gunicorn reloads)
    for h in list(root.handlers):
        root.removeHandler(h)
    h = logging.StreamHandler(sys.stdout)
    h.setFormatter(JsonFormatter())
    root.addHandler(h)

def get_logger(name: str = "app"):
    return logging.getLogger(name)

def log_event(logger: logging.Logger, **fields: Any) -> None:
    # convenience helper for structured logs
    logger.info("", extra=fields)
