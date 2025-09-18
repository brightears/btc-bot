"""Logging utilities for the funding carry bot."""

from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

_LOGGER_NAME = "funding_exec"
_CONFIGURED = False


def configure_logging(level: str = "INFO") -> logging.Logger:
    """Configure a rotating file logger and return the root project logger."""
    global _CONFIGURED

    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "funding_exec.log"

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(level.upper())

    if _CONFIGURED:
        return logger

    logger.handlers.clear()

    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=5)
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(fmt)
    logger.addHandler(stream_handler)

    _CONFIGURED = True
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger, configuring the root logger if required."""
    if not _CONFIGURED:
        configure_logging()
    if name:
        return logging.getLogger(f"{_LOGGER_NAME}.{name}")
    return logging.getLogger(_LOGGER_NAME)
