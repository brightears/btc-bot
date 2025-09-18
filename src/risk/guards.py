"""Risk guardrails for the funding executor."""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Iterable


def kill_switch_engaged(kill_file: str = ".kill") -> bool:
    if os.getenv("KILL", "0").strip().upper() in {"1", "TRUE", "YES"}:
        return True
    return Path(kill_file).exists()


def enforce_symbol_whitelist(symbol: str, whitelist: Iterable[str]) -> bool:
    return symbol in set(whitelist)


def enforce_notional_cap(notional: float, cap: float) -> bool:
    return notional <= cap


def ensure_maker_only(logger: logging.Logger, maker_only: bool) -> None:
    if not maker_only:
        logger.warning("Maker-only mode disabled; crossing the spread may incur additional costs")
