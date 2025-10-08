from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import yaml

REQUIRED_KEYS = {"goal"}


def load_ai_file(path: str) -> Dict[str, Any]:
    """
    Load a .ai YAML file and enforce minimal schema requirements.
    """
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(path)

    data = yaml.safe_load(file_path.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ValueError(".ai file must contain a YAML mapping.")

    missing = REQUIRED_KEYS - data.keys()
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Missing required fields: {missing_list}")

    # Defaults
    data.setdefault("model", "local")
    data.setdefault("permissions", ["shell", "file_write"])
    data.setdefault("workdir", ".")

    return data
