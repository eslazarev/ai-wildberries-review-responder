from __future__ import annotations

import json
import sys
from typing import Any, Dict

from loguru import logger as loguru_logger

LoggerType = Any


def _serialize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "timestamp": record["time"].isoformat(),
        "level": record["level"].name,
        "message": record["message"],
        "module": record["module"],
        "function": record["function"],
        "line": record["line"],
        "extra": record["extra"],
    }


def _json_sink(message: Any) -> None:
    payload = _serialize_record(message.record)
    serialized = json.dumps(payload, ensure_ascii=False, default=str)
    sys.stdout.write(serialized + "\n")


def init_logger() -> LoggerType:
    """
    Initialize and return the shared Loguru logger.

    Reconfigures the global logger to write to stdout so entrypoints can bind it once.
    """
    loguru_logger.remove()
    loguru_logger.add(
        _json_sink,
        enqueue=False,
        backtrace=False,
        diagnose=False,
    )
    return loguru_logger
