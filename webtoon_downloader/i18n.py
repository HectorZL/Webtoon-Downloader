import json
import locale
import os
from typing import Any

class I18nManager:
    def __init__(self):
        self.locales_dir = os.path.join(os.path.dirname(__file__), "locales")
        self.default_locale = "en"
        self.current_locale = self._detect_locale()
        self.translations = self._load_translations(self.current_locale)

    def _detect_locale(self) -> str:
        try:
            loc, _ = locale.getdefaultlocale()
            if loc and loc.startswith("es"):
                return "es"
        except Exception:
            pass
        return self.default_locale

    def _load_translations(self, lang: str) -> dict[str, str]:
        file_path = os.path.join(self.locales_dir, f"{lang}.json")
        if not os.path.exists(file_path):
            file_path = os.path.join(self.locales_dir, f"{self.default_locale}.json")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def t(self, key: str, **kwargs: Any) -> str:
        text = self.translations.get(key, key)
        if kwargs:
            try:
                return text.format(**kwargs)
            except (KeyError, ValueError):
                return text
        return text

    def set_locale(self, lang: str):
        """Manually override the locale."""
        if lang in ["en", "es"]:
            self.current_locale = lang
            self.translations = self._load_translations(lang)

# Global instance
manager = I18nManager()
t = manager.t
