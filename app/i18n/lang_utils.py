"""
lang_utils.py
=============
Core multilingual helper for AgriShield-TN.

Functions
---------
  t(key, **kwargs)   → fetch translated string for the current session language.
                       Falls back to English if the key is missing in the target language.
                       Supports {var} style placeholders via **kwargs.

  get_lang()         → return current ISO language code ("en" | "ta" | "hi")

  set_lang(code)     → set the session language and trigger a Streamlit rerun

  lang_label(code)   → return the native display name for a language code
"""

from __future__ import annotations
from typing import Any

import streamlit as st
from .translations import TRANSLATIONS

# ── Supported languages (code → native display name) ──────────────────────────
SUPPORTED_LANGS: dict[str, str] = {
    "en": "English",
    "ta": "தமிழ்",
    "hi": "हिन्दी",
}

_DEFAULT_LANG = "en"


def get_lang() -> str:
    """Return the currently selected ISO language code."""
    return st.session_state.get("lang", _DEFAULT_LANG)


def set_lang(code: str) -> None:
    """Set the session language and rerun the app to refresh all strings."""
    if code in SUPPORTED_LANGS:
        st.session_state["lang"] = code
        st.rerun()


def lang_label(code: str) -> str:
    """Return the native display name for a language code."""
    return SUPPORTED_LANGS.get(code, code)


def t(key: str, **kwargs: Any) -> str:
    """
    Look up a dot-separated translation key in the current language.

    Falls back to English if:
      - the language dict is missing the key
      - any intermediate key is missing

    Parameters
    ----------
    key    : dot-separated key string, e.g. "diagnose.start_button"
    kwargs : optional variables to format into the string, e.g. t("weather.temp", val=32)

    Returns
    -------
    Translated string (or the key itself if completely missing in both langs).
    """
    lang = get_lang()
    keys = key.split(".")

    def _walk(d: dict, path: list[str]) -> str | None:
        node = d
        for k in path:
            if not isinstance(node, dict):
                return None
            node = node.get(k)
            if node is None:
                return None
        return node if isinstance(node, str) else None

    # Try target language first
    result = _walk(TRANSLATIONS.get(lang, {}), keys)

    # Fall back to English
    if result is None:
        result = _walk(TRANSLATIONS.get(_DEFAULT_LANG, {}), keys)

    # Last resort: return the key itself so the UI never breaks
    if result is None:
        result = key

    # Apply format variables if supplied
    if kwargs:
        try:
            result = result.format(**kwargs)
        except (KeyError, ValueError):
            pass  # return as-is if formatting fails

    return result
