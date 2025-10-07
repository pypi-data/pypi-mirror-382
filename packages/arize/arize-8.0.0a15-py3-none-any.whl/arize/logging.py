from __future__ import annotations

import json
import logging
import os
import sys
from typing import Any, Dict, Iterable, Mapping

from arize.config import _parse_bool
from arize.constants.config import (
    DEFAULT_LOG_ENABLE,
    DEFAULT_LOG_LEVEL,
    DEFAULT_LOG_STRUCTURED,
    ENV_LOG_ENABLE,
    ENV_LOG_LEVEL,
    ENV_LOG_STRUCTURED,
)

_LEVEL_MAP = {
    "CRITICAL": logging.CRITICAL,
    "ERROR": logging.ERROR,
    "WARN": logging.WARNING,
    "WARNING": logging.WARNING,
    "INFO": logging.INFO,
    "DEBUG": logging.DEBUG,
    "NOTSET": logging.NOTSET,
}


class CtxAdapter(logging.LoggerAdapter):
    """LoggerAdapter that merges bound context with per-call extras safely."""

    def process(self, msg, kwargs):
        call_extra = _coerce_mapping(kwargs.pop("extra", None))
        bound_extra = _coerce_mapping(self.extra)
        merged = (
            {**bound_extra, **call_extra}
            if (bound_extra or call_extra)
            else None
        )
        if merged:
            kwargs["extra"] = merged
        return msg, kwargs

    def with_extra(self, **more) -> CtxAdapter:
        """Return a copy of this adapter with additional bound extras."""
        base = _coerce_mapping(self.extra)
        base.update(_coerce_mapping(more))
        return type(self)(self.logger, base)

    def without_extra(self) -> CtxAdapter:
        """Return a copy of this adapter with *no* bound extras."""
        return type(self)(self.logger, None)


class CustomLogFormatter(logging.Formatter):
    grey = "\x1b[38;21m"
    blue = "\x1b[38;5;39m"
    yellow = "\x1b[33m"
    red = "\x1b[38;5;196m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    GREY = "\x1b[38;21m"
    BLUE = "\x1b[38;5;39m"
    YELLOW = "\x1b[33m"
    RED = "\x1b[38;5;196m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    COLORS = {
        logging.DEBUG: BLUE,
        logging.INFO: GREY,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def __init__(self, fmt: str):
        super().__init__(fmt=fmt)

    def format(self, record: logging.LogRecord) -> str:
        # Build the base message without any color.
        base = super().format(record)

        # Collect non-standard extras
        extras = {
            k: v
            for k, v in record.__dict__.items()
            if k not in _STANDARD_RECORD_KEYS
        }

        if extras:
            # Append extras in kv form
            extras_str = " ".join(f"{k}={v!r}" for k, v in extras.items())
            base = f"{base} | {extras_str}"

        # Now color the entire line uniformly.
        color = self.COLORS.get(record.levelno, "")
        if color:
            return f"{color}{base}{self.RESET}"
        return base


class JsonFormatter(logging.Formatter):
    """Minimal JSON formatter (one JSON object per line)."""

    # fields to skip copying from record.__dict__
    _skip = {
        # "name",
        # "msg",
        # "args",
        # "levelname",
        # "levelno",
        # "pathname",
        # "filename",
        # "module",
        # "exc_info",
        # "exc_text",
        # "stack_info",
        # "lineno",
        # "funcName",
        # "created",
        # "msecs",
        # "relativeCreated",
        # "thread",
        # "threadName",
        # "processName",
        # "process",
    }

    def format(self, record: logging.LogRecord) -> str:
        payload: Dict[str, Any] = {
            # "time": self.formatTime(record, datefmt="%Y-%m-%dT%H:%M:%S%z"),
            # "logger": record.name,
            # "level": record.levelname,
            # "message": record.getMessage(),
        }

        # Include any LoggerAdapter/extra fields
        for k, v in record.__dict__.items():
            if k not in payload and k not in self._skip:
                payload[k] = v

        # Exception info, if present
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def _parse_level(val: str | None, default: int = logging.INFO) -> int:
    if not val:
        return default
    return _LEVEL_MAP.get(val.strip().upper(), default)


def auto_configure_from_env() -> None:
    """
    If ARIZE_LOG is truthy, configure logging for 'arize' once,
    using ARIZE_LOG_LEVEL and ARIZE_LOG_STRUCTURED if provided.
    Otherwise, do nothing (library stays quiet with NullHandler).
    """

    if not _parse_bool(os.getenv(ENV_LOG_ENABLE, DEFAULT_LOG_ENABLE)):
        return

    level = _parse_level(os.getenv(ENV_LOG_LEVEL, DEFAULT_LOG_LEVEL))
    structured = _parse_bool(
        os.getenv(ENV_LOG_STRUCTURED, DEFAULT_LOG_STRUCTURED)
    )
    configure_logging(level=level, structured=structured)


_STANDARD_RECORD_KEYS = {
    "name",
    "msg",
    "args",
    "levelname",
    "levelno",
    "pathname",
    "filename",
    "module",
    "exc_info",
    "exc_text",
    "stack_info",
    "lineno",
    "funcName",
    "created",
    "msecs",
    "relativeCreated",
    "thread",
    "threadName",
    "processName",
    "process",
    # asyncio
    "taskName",
    # always present in our payload already:
    "message",
    "asctime",
}


def get_truncation_warning_message(instance, limit) -> str:
    return (
        f"Attention: {instance} exceeding the {limit} character limit will be "
        "automatically truncated upon ingestion into the Arize platform. Should you require "
        "a higher limit, please reach out to our support team at support@arize.com"
    )


def configure_logging(
    level: int = logging.INFO,
    structured: bool = False,
) -> None:
    """
    Configure logging for the 'arize' logger.

    Args:
        level: logging level (e.g., logging.INFO, logging.DEBUG)
        to_stdout: attach a StreamHandler to stdout
        structured: if True, emit JSON logs; otherwise use color pretty logs
    """
    root = logging.getLogger("arize")
    root.setLevel(level)

    # Remove any existing handlers under 'arize'
    for h in root.handlers[:]:
        root.removeHandler(h)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    if structured:
        handler.setFormatter(JsonFormatter())
    else:
        fmt = "  %(name)s | %(levelname)s | %(message)s"
        handler.setFormatter(CustomLogFormatter(fmt))

    root.addHandler(handler)


def log_a_list(values: Iterable[Any] | None, join_word: str) -> str:
    if values is None:
        return ""
    list_of_str = list(values)
    if len(list_of_str) == 0:
        return ""
    if len(list_of_str) == 1:
        return list_of_str[0]
    return (
        f"{', '.join(map(str, list_of_str[:-1]))} {join_word} {list_of_str[-1]}"
    )


def get_arize_project_url(response: Any):
    if "realTimeIngestionUri" in json.loads(response.content.decode()):
        return json.loads(response.content.decode())["realTimeIngestionUri"]
    return ""


def _coerce_mapping(obj: Any) -> Dict[str, Any]:
    """Return a shallow dict copy if obj is a Mapping[str, Any], else {}."""
    if isinstance(obj, Mapping):
        # force keys to str to satisfy logging's expectation
        return {str(k): v for k, v in obj.items()}
    return {}
