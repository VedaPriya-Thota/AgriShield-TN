"""
AI image generation layer for AgriShield-TN.

Provider order: OpenAI DALL-E 3 → Replicate Flux Schnell → None (static fallback).

Each generated image is:
  1. Resized to 512 × 512 JPEG (via PIL, already in requirements)
  2. Saved to app/assets/gen_cache/{md5_hash}.jpg (persists across restarts)
  3. Returned as a base64 data URI so HTML <img src="..."> works without URL expiry

Cache lookup on every call: disk hit → instant, no API charge.

Required .env keys (add whichever provider you have):
  OPENAI_API_KEY        – for DALL-E 3
  REPLICATE_API_TOKEN   – for Flux Schnell (free tier available)

Public API
----------
generate_farmer_image(mood)           -> str | None   (base64 data URI)
generate_crop_image(crop_state)       -> str | None
generate_weather_image(weather_state) -> str | None
generate_action_image(action_label)   -> str | None

Prompt builders (also public — useful for debugging / prompt inspection):
  build_farmer_prompt(mood)
  build_crop_prompt(crop_state)
  build_weather_prompt(weather_state)
  build_action_prompt(action_label)
"""

from __future__ import annotations

import base64
import hashlib
import io
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Disk cache ────────────────────────────────────────────────────────────────
# Stored alongside the existing farmer_ai.png so the app already owns this tree.
_CACHE_DIR = Path(__file__).resolve().parent.parent.parent / "app" / "assets" / "gen_cache"


def _ensure_cache_dir() -> None:
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_path(prompt: str) -> Path:
    key = hashlib.md5(prompt.encode()).hexdigest()[:20]
    return _CACHE_DIR / f"{key}.jpg"


def _load_cached(prompt: str) -> Optional[str]:
    p = _cache_path(prompt)
    if p.exists():
        try:
            return _to_data_uri(p.read_bytes())
        except Exception:
            pass
    return None


def _save_to_cache(prompt: str, img_bytes: bytes) -> None:
    _ensure_cache_dir()
    try:
        _cache_path(prompt).write_bytes(img_bytes)
    except Exception as e:
        logger.debug("Cache write failed: %s", e)


def _to_data_uri(img_bytes: bytes) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode()


def _compress(img_bytes: bytes, size: int = 512) -> bytes:
    """Resize to square JPEG and compress. Returns original bytes on PIL failure."""
    try:
        from PIL import Image
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        img = img.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=82, optimize=True)
        return buf.getvalue()
    except Exception as e:
        logger.debug("Compress failed, using original: %s", e)
        return img_bytes


# ── Style anchor ─────────────────────────────────────────────────────────────
# Appended to every prompt so all images share the same visual language.
_STYLE = (
    "flat 2D illustration, soft lime-green and cream color palette, "
    "minimalistic clean design, warm friendly mood, "
    "Tamil Nadu paddy rice farm setting, consistent warm top-left lighting, "
    "vector art style, no text, no labels, no watermarks, "
    "UI illustration suitable for a mobile agricultural app"
)


# ── Prompt builders ───────────────────────────────────────────────────────────

def build_farmer_prompt(mood: str) -> str:
    """Build a DALL-E / diffusion prompt for a Tamil farmer in the given mood."""
    _FARMER = {
        "calm": (
            "A friendly Tamil Nadu farmer man standing in a lush green paddy rice field, "
            "warm smile, relaxed posture, wearing white dhoti and simple blue shirt, "
            "straw hat in hand, golden morning sunlight, healthy crop behind him"
        ),
        "thinking": (
            "A Tamil Nadu farmer man in a paddy field with a thoughtful concerned expression, "
            "leaning slightly forward, examining a rice leaf closely, hand near chin, "
            "wearing white dhoti and blue shirt, soft overcast light"
        ),
        "concerned": (
            "A worried Tamil Nadu farmer man urgently inspecting diseased rice crop, "
            "leaning forward, pointing at leaf damage with serious expression, "
            "wearing white dhoti and blue shirt, slightly dramatic warm light to convey urgency"
        ),
    }
    desc = _FARMER.get(mood, _FARMER["calm"])
    return f"{desc}, {_STYLE}"


def build_crop_prompt(crop_state: str) -> str:
    """Build a prompt for a rice leaf/plant showing the given disease state."""
    _CROP = {
        "healthy": (
            "Close-up of vibrant healthy paddy rice leaves, "
            "fresh lime-green with water droplets, lush growth, "
            "soft morning light, clean and pristine"
        ),
        "mild": (
            "Close-up of paddy rice leaf showing very early disease signs, "
            "mostly green with a few tiny brown specks just starting to appear, "
            "early stage, still mostly healthy"
        ),
        "infected": (
            "Close-up of paddy rice leaf with moderate disease damage, "
            "brownish-orange lesions with yellow halos on a green leaf, "
            "clear disease patches visible"
        ),
        "severe": (
            "Close-up of severely damaged paddy rice leaf, "
            "large dark brown and black lesions, wilting edges, "
            "significant yellowing and decay, disease at advanced stage"
        ),
    }
    desc = _CROP.get(crop_state, _CROP["mild"])
    return f"{desc}, {_STYLE}"


def build_weather_prompt(weather_state: str) -> str:
    """Build a prompt for a paddy field landscape showing weather conditions."""
    _WEATHER = {
        "sunny": (
            "Bright sunny Tamil Nadu paddy field landscape, "
            "golden sunlight pouring over green rice plants, clear blue sky, "
            "dry warm atmosphere, vivid and cheerful"
        ),
        "cloudy": (
            "Overcast sky above Tamil Nadu paddy rice fields, "
            "soft diffuse grey-white clouds, even cool lighting, "
            "green rice plants swaying gently"
        ),
        "humid": (
            "Humid misty morning over paddy rice field, "
            "visible moisture in the air, soft hazy atmospheric glow, "
            "dense green rice crop, morning dew on leaves"
        ),
        "rainy": (
            "Gentle rain falling on Tamil Nadu paddy field, "
            "water droplets splashing on green rice leaves, "
            "small puddles between rows, soft grey rainy sky"
        ),
        "foggy": (
            "Foggy cool early morning over paddy rice field, "
            "low white mist drifting across rows of rice plants, "
            "silhouettes of rice stalks, mysterious cool atmosphere"
        ),
    }
    desc = _WEATHER.get(weather_state, _WEATHER["cloudy"])
    return f"{desc}, {_STYLE}"


def build_action_prompt(action_label: str) -> str:
    """Build a prompt for an agricultural action step illustration."""
    lower = action_label.lower()
    if any(w in lower for w in ("drain", "water", "flood", "irrigat")):
        desc = (
            "Tamil Nadu farmer opening irrigation channel in paddy field, "
            "water flowing through a drainage ditch, focused purposeful work"
        )
    elif any(w in lower for w in ("spray", "fungicide", "pesticide", "insecticid", "bactericid")):
        desc = (
            "Farmer spraying crop protection chemical on paddy rice plants "
            "using a hand-pump sprayer, fine mist over green leaves, morning light"
        )
    elif any(w in lower for w in ("monitor", "inspect", "check", "watch", "survey")):
        desc = (
            "Farmer carefully inspecting rice crop leaves up close, "
            "attentive observation, hand gently holding a rice stalk, focused expression"
        )
    elif any(w in lower for w in ("remov", "cut", "uproot", "dispos", "eliminat", "harvest")):
        desc = (
            "Farmer carefully removing diseased rice plant parts by hand, "
            "placing damaged leaves into a basket, careful and deliberate"
        )
    elif any(w in lower for w in ("fertilizer", "nutrient", "feed")):
        desc = (
            "Farmer scattering fertilizer granules around base of rice plants, "
            "nurturing the soil, crop rows visible in background"
        )
    else:
        desc = (
            "Tamil Nadu farmer attentively working in a healthy paddy field, "
            "caring for rice crop with focused purpose"
        )
    return f"{desc}, {_STYLE}"


# ── .env loader ───────────────────────────────────────────────────────────────

def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
        p = Path(__file__).resolve()
        for _ in range(6):
            p = p.parent
            if (p / ".env").exists():
                # override=True so .env values win over stale system env vars
                load_dotenv(p / ".env", override=True)
                return
    except ImportError:
        pass


_load_dotenv()


# ── Provider: OpenAI DALL-E 3 ─────────────────────────────────────────────────

def _openai_generate(prompt: str) -> Optional[bytes]:
    """
    Call DALL-E 3 with response_format='b64_json' to get raw image bytes.
    Returns None if OPENAI_API_KEY is absent, package is missing, or call fails.
    """
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
            response_format="b64_json",
        )
        b64 = response.data[0].b64_json
        return base64.b64decode(b64) if b64 else None
    except ImportError:
        logger.warning("openai not installed — run: pip install openai>=1.0.0")
        return None
    except Exception as e:
        logger.warning("DALL-E 3 generation failed: %s", e)
        return None


# ── Provider: Replicate Flux Schnell ─────────────────────────────────────────

def _replicate_generate(prompt: str) -> Optional[bytes]:
    """
    Call Flux Schnell on Replicate, download the returned image URL.
    Returns None if REPLICATE_API_TOKEN is absent, package is missing, or fails.
    """
    api_token = os.environ.get("REPLICATE_API_TOKEN", "").strip()
    if not api_token:
        return None
    try:
        import replicate
        import urllib.request
        os.environ["REPLICATE_API_TOKEN"] = api_token
        output = replicate.run(
            "black-forest-labs/flux-schnell",
            input={
                "prompt": prompt,
                "width": 512,
                "height": 512,
                "num_outputs": 1,
                "num_inference_steps": 4,
                "output_format": "jpg",
            },
        )
        if not output:
            return None
        img_url = output[0] if isinstance(output[0], str) else str(output[0])
        with urllib.request.urlopen(img_url, timeout=20) as resp:
            return resp.read()
    except ImportError:
        logger.warning("replicate not installed — run: pip install replicate>=0.25.0")
        return None
    except Exception as e:
        logger.warning("Replicate generation failed: %s", e)
        return None


# ── Core dispatcher ───────────────────────────────────────────────────────────

def generate_image(prompt: str, resize: int = 512) -> Optional[str]:
    """
    Generate an image for the prompt.

    Flow: disk cache → OpenAI → Replicate → None (caller uses static fallback).
    On success: image is resized, cached to disk, returned as base64 data URI.
    Never raises.
    """
    # 1. Disk cache
    cached = _load_cached(prompt)
    if cached:
        return cached

    # 2. Try OpenAI DALL-E 3
    raw = _openai_generate(prompt)

    # 3. Fall back to Replicate Flux Schnell
    if raw is None:
        raw = _replicate_generate(prompt)

    # 4. Both providers unavailable / failed
    if raw is None:
        return None

    # 5. Compress, cache, return
    compressed = _compress(raw, size=resize)
    _save_to_cache(prompt, compressed)
    return _to_data_uri(compressed)


# ── Public convenience wrappers ───────────────────────────────────────────────

def generate_farmer_image(mood: str) -> Optional[str]:
    return generate_image(build_farmer_prompt(mood))


def generate_crop_image(crop_state: str) -> Optional[str]:
    return generate_image(build_crop_prompt(crop_state))


def generate_weather_image(weather_state: str) -> Optional[str]:
    return generate_image(build_weather_prompt(weather_state))


def generate_action_image(action_label: str) -> Optional[str]:
    return generate_image(build_action_prompt(action_label))
