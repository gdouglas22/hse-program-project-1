from __future__ import annotations

from pathlib import Path
import sys


def get_resource_path(relative_path: str) -> Path:
    """Return an absolute path to a resource for both source and frozen builds."""
    if getattr(sys, "_MEIPASS", None):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parents[1]
    return base / relative_path
