"""Telegram notification helper."""

from __future__ import annotations

import logging
import os
from typing import Optional

import requests


class TelegramNotifier:
    def __init__(self, token: Optional[str], chat_id: Optional[str], logger: logging.Logger) -> None:
        self._token = token
        self._chat_id = chat_id
        self._logger = logger.getChild("telegram") if hasattr(logger, "getChild") else logger

    @property
    def enabled(self) -> bool:
        return bool(self._token and self._chat_id)

    def send_message(self, text: str, parse_mode: Optional[str] = None) -> None:
        if not self.enabled:
            self._logger.debug("Telegram notifier disabled; skipping message")
            return
        url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        payload = {"chat_id": self._chat_id, "text": text}
        if parse_mode:
            payload["parse_mode"] = parse_mode
        try:
            response = requests.post(url, timeout=10, json=payload)
            response.raise_for_status()
            self._logger.info("Sent Telegram alert")
        except requests.RequestException as exc:
            self._logger.warning("Telegram send failed: %s", exc)

    def status_template(self, state: dict) -> str:
        mode = state.get("mode", "dry-run")
        position = state.get("position")
        if not position:
            return f"Mode: {mode}\nStatus: Flat"
        funding_eta = position.get("funding_eta") or "unknown"
        return (
            f"Mode: {mode}\nStatus: Carry active\n"
            f"Edge bps: {position.get('edge_bps')}\n"
            f"Funding ETA: {funding_eta}"
        )

    def handle_status(self, state_path: str) -> None:
        if not self.enabled:
            return
        try:
            import json

            if not os.path.exists(state_path):
                self.send_message("No state recorded yet.")
                return
            with open(state_path, "r", encoding="utf-8") as fh:
                state = json.load(fh)
            self.send_message(self.status_template(state))
        except (OSError, ValueError) as exc:
            self._logger.warning("Failed to process Telegram status request: %s", exc)
