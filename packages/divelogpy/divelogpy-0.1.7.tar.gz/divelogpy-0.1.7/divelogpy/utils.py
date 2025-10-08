"""Shared helpers for decoding Shearwater Cloud exports."""

from __future__ import annotations

import json
from typing import Any, Dict


def load_json(value: Any) -> Dict[str, Any]:
    """Safely decode a JSON payload, returning an empty dict on failure."""
    if not isinstance(value, str) or not value:
        return {}
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return {}
