#!/usr/bin/env python3
"""Emit a quick snapshot of runtime config without secrets."""

from __future__ import annotations

import json
import os
from pathlib import Path

import yaml


def main() -> None:
    cfg_path = Path("config.yaml")
    config = yaml.safe_load(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}

    state_path = Path("logs/state.json")
    state = {}
    if state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            state = {"error": "invalid-json"}

    snapshot = {
        "mode": state.get("mode", "unknown"),
        "position_open": bool(state.get("position")),
        "symbol": config.get("symbol"),
        "loop_seconds": config.get("loop_seconds"),
        "threshold_bps": config.get("threshold_bps"),
        "maker_only": config.get("maker_only"),
        "live_flag_env": os.getenv("LIVE_TRADING", "NO") in {"YES", "TRUE", "1"},
    }
    print(json.dumps(snapshot, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
