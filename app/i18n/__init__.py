"""
AgriShield-TN internationalisation package.

Public API
----------
from i18n import t, get_lang, set_lang, SUPPORTED_LANGS

    t("diagnose.start_button")          → translated string in current language
    t("weather.temp_label", val="32")   → supports {var} placeholders
    get_lang()                          → "en" | "ta" | "hi"
    set_lang("ta")                      → sets session state + reruns
    SUPPORTED_LANGS                     → {"en": "English", "ta": "தமிழ்", ...}
"""

from .lang_utils import t, get_lang, set_lang, lang_label, SUPPORTED_LANGS

__all__ = ["t", "get_lang", "set_lang", "lang_label", "SUPPORTED_LANGS"]
