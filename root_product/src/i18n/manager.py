from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Tuple

from core.resources import get_resource_path

class I18nManager:
    """Load and serve translations with runtime switching."""

    def __init__(self, base_dir: Path | None = None) -> None:
        if base_dir is None:
            base_dir = get_resource_path("resources/i18n")
        self._base_dir = base_dir
        self._translations: Dict[str, Dict[str, str]] = {}
        self._language = "en"
        self.reload()

    def reload(self) -> None:
        self._translations = {}
        if not self._base_dir.exists():
            return
        for path in self._base_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            code = path.stem
            if isinstance(data, dict):
                self._translations[code] = data

    def available_languages(self) -> List[Tuple[str, str]]:
        result = []
        for code, data in sorted(self._translations.items()):
            name = data.get("language_name", code)
            result.append((code, name))
        return result

    def set_language(self, code: str) -> None:
        if code not in self._translations:
            self.reload()
        if code in self._translations:
            self._language = code

    def t(self, key: str) -> str:
        lang = self._translations.get(self._language, {})
        return lang.get(key, key)

    @property
    def language(self) -> str:
        return self._language
