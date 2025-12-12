import json
from typing import Dict, Tuple

from config import DATA_FILE


def _default_payload() -> Dict[str, object]:
    return {
        "vehicles": [],
        "dealer_transactions": [],
        "wages": [],
        "income_expenses": [],
        "stock": [],
    }


def _with_defaults(payload: Dict[str, object]) -> Dict[str, object]:
    """Ensure all expected keys exist in the payload."""

    template = _default_payload()
    for key, default_value in template.items():
        payload.setdefault(key, default_value)
    return payload


def load_data() -> Tuple[Dict[str, object], bool]:
    """Return stored data and whether a repair/default was applied."""

    if not DATA_FILE.exists():
        return _default_payload(), True

    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            loaded = json.load(f)
    except (json.JSONDecodeError, OSError):
        # Corrupted or unreadable file: fall back to an empty payload
        return _default_payload(), True

    if not isinstance(loaded, dict):
        return _default_payload(), True

    return _with_defaults(loaded), False


def save_data(payload: Dict[str, object]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(_with_defaults(payload), f, ensure_ascii=False, indent=2)
