"""Storage helpers for AssessmentFlow."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict


def empty_store() -> Dict[str, Any]:
    return {
        "assessments": [],
        "sessions": [],
        "settings": {"daily_capacity_hours": 3.0},
    }


def load_data(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return empty_store()

    with path.open("r", encoding="utf-8") as handle:
        loaded = json.load(handle)

    if not isinstance(loaded, dict):
        raise ValueError("Data file must contain one JSON object.")

    loaded.setdefault("assessments", [])
    loaded.setdefault("sessions", [])
    loaded.setdefault("settings", {"daily_capacity_hours": 3.0})
    loaded["settings"].setdefault("daily_capacity_hours", 3.0)
    return loaded


def save_data(path: Path, data: Dict[str, Any]) -> None:
    """Save with an atomic replacement to reduce the chance of file corruption."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_suffix(path.suffix + ".tmp")
    with temp_path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    os.replace(temp_path, path)


def next_id(data: Dict[str, Any]) -> str:
    used = []
    for item in data.get("assessments", []):
        raw = str(item.get("id", ""))
        if raw.startswith("A") and raw[1:].isdigit():
            used.append(int(raw[1:]))
    return f"A{(max(used, default=0) + 1):03d}"
