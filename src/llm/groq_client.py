"""
Groq API client wrapper for AgriShield-TN.

Provides a single reusable call function with:
- environment-based key loading (python-dotenv + os.environ)
- graceful failure (returns None on any error, never raises to caller)
- configurable model, tokens, and timeout
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Load .env if present (no-op when python-dotenv is absent) ────────────────
def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        # Search upward from this file for a .env
        candidate = Path(__file__).resolve()
        for _ in range(6):
            candidate = candidate.parent
            env_file = candidate / ".env"
            if env_file.exists():
                load_dotenv(env_file)
                return
    except ImportError:
        pass  # python-dotenv not installed — rely on shell env


_load_dotenv()

# ── Default model ─────────────────────────────────────────────────────────────
DEFAULT_MODEL  = "llama-3.1-8b-instant"
DEFAULT_TOKENS = 512
DEFAULT_TIMEOUT = 20  # seconds

# Cache the client across calls so we don't re-instantiate on every request
_client = None


def _get_client():
    """Return a cached Groq client, or None if key is missing / SDK unavailable."""
    global _client
    if _client is not None:
        return _client

    api_key = os.environ.get("GROQ_API_KEY", "").strip()
    if not api_key:
        logger.warning("GROQ_API_KEY is not set — Groq features will be disabled.")
        return None

    try:
        from groq import Groq
        _client = Groq(api_key=api_key)
        return _client
    except ImportError:
        logger.error("groq package is not installed. Run: pip install groq")
        return None
    except Exception as exc:
        logger.error("Failed to initialise Groq client: %s", exc)
        return None


def call_groq(
    user_prompt: str,
    system_prompt: str = "You are a helpful assistant.",
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_TOKENS,
    temperature: float = 0.4,
) -> Optional[str]:
    """
    Call the Groq chat completions API.

    Returns the assistant message content string, or None on any failure.
    Never raises — all exceptions are caught and logged.
    """
    client = _get_client()
    if client is None:
        return None

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        content = response.choices[0].message.content
        return content.strip() if content else None
    except Exception as exc:
        logger.error("Groq API call failed: %s", exc)
        return None


def is_groq_available() -> bool:
    """Quick check — returns True only if a working client can be created."""
    return _get_client() is not None
