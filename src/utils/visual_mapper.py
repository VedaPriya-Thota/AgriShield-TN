"""
Dynamic visual mapping layer for AgriShield-TN.

Converts diagnosis output (severity, weather) into a VisualState object that
tells the UI which CSS classes, emoji visuals, and image assets to render.
No layout logic here — only the decision engine and asset dictionaries.

Public API
----------
build_visual_state(severity, weather, fstory) -> VisualState
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# ── Asset dictionaries ────────────────────────────────────────────────────────
# These are the single source of truth for which visual to use per state.
# The UI reads from these; it never decides itself.

FARMER_IMAGES: dict[str, dict] = {
    "calm": {
        "local_path":  "farmer_ai.png",   # relative to app/assets/
        "emoji":       "&#128119;&#127996;&#128516;",
        "css_class":   "sg-farmer--calm",
        "pulse_color": "#bbf7d0",
        "label":       "Crop looks good!",
    },
    "thinking": {
        "local_path":  "farmer_ai.png",
        "emoji":       "&#128119;&#127996;&#129300;",
        "css_class":   "sg-farmer--thinking",
        "pulse_color": "#fde68a",
        "label":       "Some concerns — checking…",
    },
    "concerned": {
        "local_path":  "farmer_ai.png",
        "emoji":       "&#128119;&#127996;&#128552;",
        "css_class":   "sg-farmer--concerned",
        "pulse_color": "#fecaca",
        "label":       "Act now — crop needs help!",
    },
}

# Crop images: Unsplash IDs already used elsewhere in this codebase.
CROP_IMAGES: dict[str, dict] = {
    "healthy": {
        "unsplash_id": "1574943320219-553eb213f72d",
        "emoji":       "&#127806;&#9989;&#127807;",
        "css_class":   "vmap-crop--healthy",
        "accent":      "#16a34a",
        "label":       "Healthy paddy",
    },
    "mild": {
        "unsplash_id": "1560493236-bb5cdcfe5da8",
        "emoji":       "&#127806;&#128994;&#127807;",
        "css_class":   "vmap-crop--mild",
        "accent":      "#d97706",
        "label":       "Early signs detected",
    },
    "infected": {
        "unsplash_id": "1560493236-bb5cdcfe5da8",
        "emoji":       "&#127806;&#128992;&#127807;",
        "css_class":   "vmap-crop--infected",
        "accent":      "#ea580c",
        "label":       "Disease detected",
    },
    "severe": {
        "unsplash_id": "1536054009244-c43bb5f1c1ac",
        "emoji":       "&#127806;&#128308;&#127807;",
        "css_class":   "vmap-crop--severe",
        "accent":      "#dc2626",
        "label":       "Severe damage",
    },
}

WEATHER_IMAGES: dict[str, dict] = {
    "sunny": {
        "unsplash_id": "1500382017468-9049fed747ef",
        "emoji":       "&#9728;&#65039;",
        "css_class":   "vmap-wx--sunny",
        "gradient":    "linear-gradient(135deg,#fef9c3,#fef08a)",
        "label":       "Sunny & dry",
    },
    "cloudy": {
        "unsplash_id": "1574943320219-553eb213f72d",
        "emoji":       "&#9925;&#65039;",
        "css_class":   "vmap-wx--cloudy",
        "gradient":    "linear-gradient(135deg,#f1f5f9,#e2e8f0)",
        "label":       "Partly cloudy",
    },
    "humid": {
        "unsplash_id": "1518495973542-4542adad0130",
        "emoji":       "&#127787;&#65039;",
        "css_class":   "vmap-wx--humid",
        "gradient":    "linear-gradient(135deg,#ecfdf5,#bbf7d0)",
        "label":       "Humid & warm",
    },
    "rainy": {
        "unsplash_id": "1587131782738-de30ea91a542",
        "emoji":       "&#127783;&#65039;",
        "css_class":   "vmap-wx--rainy",
        "gradient":    "linear-gradient(135deg,#eff6ff,#bfdbfe)",
        "label":       "Rainy conditions",
    },
    "foggy": {
        "unsplash_id": "1518495973542-4542adad0130",
        "emoji":       "&#127787;&#65039;",
        "css_class":   "vmap-wx--foggy",
        "gradient":    "linear-gradient(135deg,#f8fafc,#e2e8f0)",
        "label":       "Foggy & cool",
    },
}

_UNSPLASH_BASE = "https://images.unsplash.com/photo-"
_IMG_PARAMS    = "?w=400&q=70&auto=format&fit=crop"


def unsplash_url(photo_id: str) -> str:
    return f"{_UNSPLASH_BASE}{photo_id}{_IMG_PARAMS}"


# ── VisualState dataclass ─────────────────────────────────────────────────────

@dataclass
class VisualState:
    # Decision outputs (the "why" behind each visual choice)
    farmer_mood:   str   # "calm" | "thinking" | "concerned"
    crop_state:    str   # "healthy" | "mild" | "infected" | "severe"
    weather_state: str   # "sunny" | "cloudy" | "humid" | "rainy" | "foggy"

    # CSS modifier classes — apply to existing HTML containers (additive, no redesign)
    farmer_css_class:  str   # e.g. "sg-farmer--concerned"
    crop_css_class:    str   # e.g. "vmap-crop--severe"  → on story-card--d1
    weather_css_class: str   # e.g. "vmap-wx--rainy"     → on sw-icon

    # Emoji visuals — used in farmer fallback and state indicators
    farmer_emoji:  str
    crop_emoji:    str
    weather_emoji: str

    # Resolved image URLs
    farmer_img_local: str   # path relative to app/assets/ (e.g. "farmer_ai.png")
    crop_img_url:     str   # full Unsplash URL for crop thumbnail
    weather_img_url:  str   # full Unsplash URL for weather bg

    # Atmosphere
    pulse_color:      str   # hex for mood-based glow/pulse ring
    weather_gradient: str   # CSS gradient for atmospheric bg (informational)

    # Human-readable labels (accessibility / tooltips)
    farmer_label:  str
    crop_label:    str
    weather_label: str


# ── Decision rules ────────────────────────────────────────────────────────────

def _farmer_mood(severity: str) -> str:
    if severity in ("HIGH", "CRITICAL"):
        return "concerned"
    if severity == "MODERATE":
        return "thinking"
    return "calm"


def _crop_state(severity: str) -> str:
    if severity in ("HIGH", "CRITICAL"):
        return "severe"
    if severity == "MODERATE":
        return "infected"
    if severity == "LOW":
        return "mild"
    return "healthy"  # NONE


def _weather_state(weather: Optional[dict]) -> str:
    if not weather or not weather.get("available"):
        return "cloudy"

    humidity  = weather.get("humidity", 60)
    rain_3day = weather.get("rain_3day", 0)
    rain_now  = weather.get("rain_now",  0)
    condition = weather.get("condition", "").lower()

    if "fog" in condition:
        return "foggy"

    if (
        "rain" in condition
        or "shower" in condition
        or "drizzle" in condition
        or "storm" in condition
    ) and (rain_now > 0.5 or rain_3day > 10):
        return "rainy"

    if humidity >= 80 or rain_3day > 15:
        return "humid"

    if humidity >= 65 or "cloud" in condition or "overcast" in condition:
        return "cloudy"

    return "sunny"


# ── Public API ────────────────────────────────────────────────────────────────

def build_visual_state(
    severity: str,
    weather: Optional[dict] = None,
    fstory=None,  # FarmerStory — reserved for future cross-referencing
) -> VisualState:
    """
    Build a VisualState from AI diagnosis severity + live weather.

    Parameters
    ----------
    severity : str
        AgriInsight severity: "CRITICAL", "HIGH", "MODERATE", "LOW", "NONE".
    weather : dict, optional
        Return value from get_weather_risk(). May be None or {"available": False}.
    fstory : FarmerStory, optional
        Passed through for future cross-referencing; not used yet.
    """
    mood    = _farmer_mood(severity)
    crop_st = _crop_state(severity)
    wx_st   = _weather_state(weather)

    f_cfg = FARMER_IMAGES.get(mood,    FARMER_IMAGES["calm"])
    c_cfg = CROP_IMAGES.get(crop_st,   CROP_IMAGES["mild"])
    w_cfg = WEATHER_IMAGES.get(wx_st,  WEATHER_IMAGES["cloudy"])

    return VisualState(
        farmer_mood   = mood,
        crop_state    = crop_st,
        weather_state = wx_st,

        farmer_css_class  = f_cfg["css_class"],
        crop_css_class    = c_cfg["css_class"],
        weather_css_class = w_cfg["css_class"],

        farmer_emoji  = f_cfg["emoji"],
        crop_emoji    = c_cfg["emoji"],
        weather_emoji = w_cfg["emoji"],

        farmer_img_local  = f_cfg["local_path"],
        crop_img_url      = unsplash_url(c_cfg["unsplash_id"]),
        weather_img_url   = unsplash_url(w_cfg["unsplash_id"]),

        pulse_color       = f_cfg["pulse_color"],
        weather_gradient  = w_cfg["gradient"],

        farmer_label  = f_cfg["label"],
        crop_label    = c_cfg["label"],
        weather_label = w_cfg["label"],
    )
