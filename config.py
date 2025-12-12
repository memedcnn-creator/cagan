import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _resolve_data_file() -> Path:
    """Return the JSON dosya yolu, çevre değişkeni ile özelleştirilebilir."""

    override = os.environ.get("WORKSHOP_DATA_FILE")
    if override:
        return Path(override).expanduser().resolve()
    return BASE_DIR / "workshop_data.json"


DATA_FILE = _resolve_data_file()

DEFAULT_VEHICLE_STATUS = [
    "Atölyede",
    "Teslim Edildi",
]
