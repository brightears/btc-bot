#!/usr/bin/env bash
set -euo pipefail

STATE_FILE="logs/state.json"
LOG_FILE="logs/funding_exec.log"

if [[ -f "$STATE_FILE" ]]; then
  python3 - <<'PY'
import json
from pathlib import Path
state_path = Path("logs/state.json")
state = json.loads(state_path.read_text())
mode = state.get("mode", "dry-run")
pos = state.get("position")
if pos:
    print(f"mode={mode} status=carry-open edge_bps={pos.get('edge_bps')} funding_eta={pos.get('funding_eta')}")
else:
    print(f"mode={mode} status=flat")
PY
else
  echo "No state recorded"
fi

if [[ -f "$LOG_FILE" ]]; then
  tail -n 5 "$LOG_FILE"
else
  echo "Log file missing"
fi
