"""
Story mapping layer for AgriShield-TN.

Converts technical diagnosis output (disease, severity, confidence, weather)
into a FarmerStory object ready for the UI to render — no layout logic here.

Public API
----------
build_story(disease, severity, confidence, weather, disease_name) -> FarmerStory
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

_CONFIDENCE_LOW_THRESHOLD = 0.55


@dataclass
class FarmerStory:
    # Visual identity
    plant_emoji: str
    plant_bg: str
    circle_emoji: str
    circle_bg: str
    # Narrative
    what_sub: str
    why_text: str
    wx_icon: str
    wx_icon2: str
    humidity_label: str
    weather_label: str
    actions: list   # list of (icon_html, label_str, bg1_css, bg2_css)
    tip_days: int
    # Severity-derived (computed by build_story)
    risk_cls: str
    risk_badge_cls: str
    risk_label: str
    risk_msg: str
    sad_leaf: str
    greeting: str
    greeting_sub: str
    tip_msg: str
    # Meta
    disease_name: str
    is_fallback: bool = False


# ── Per-disease visual + narrative content ────────────────────────────────────

_DISEASE_DATA: dict[str, dict] = {
    "blast": {
        "plant_emoji": "&#127806;&#128119;", "plant_bg": "#fef2f2",
        "circle_emoji": "&#128168;&#127807;", "circle_bg": "linear-gradient(135deg,#bfdbfe,#93c5fd)",
        "what_sub": "Your leaves are getting damaged spots and may begin to die off.",
        "why_text": "Fungal spores spread fast in humid, cool, and windy weather.",
        "wx_icon": "&#128168;", "wx_icon2": "&#127745;",
        "humidity_label": "High 78%", "weather_label": "Humid &amp; Windy",
        "actions": [
            ("&#128167;", "Drain extra water",       "#bfdbfe", "#60a5fa"),
            ("&#127807;", "Remove damaged leaves",   "#bbf7d0", "#4ade80"),
            ("&#129514;", "Spray fungicide today",   "#ede9fe", "#8b5cf6"),
            ("&#128683;", "Avoid fertilizer now",    "#fef3c7", "#fbbf24"),
        ],
        "tip_days": 3,
    },
    "bacterial_leaf_blight": {
        "plant_emoji": "&#127806;&#128128;", "plant_bg": "#fef9c3",
        "circle_emoji": "&#127783;&#127807;", "circle_bg": "linear-gradient(135deg,#bfdbfe,#60a5fa)",
        "what_sub": "The edges of your leaves are turning yellow and looking water-soaked.",
        "why_text": "Bacteria travel in flood water, rain splashes, and strong winds.",
        "wx_icon": "&#127783;", "wx_icon2": "&#128167;",
        "humidity_label": "High 82%", "weather_label": "Rainy &amp; Wet",
        "actions": [
            ("&#128167;", "Improve drainage",        "#bfdbfe", "#60a5fa"),
            ("&#127807;", "Remove infected leaves",  "#bbf7d0", "#4ade80"),
            ("&#129514;", "Spray copper bactericide","#ede9fe", "#8b5cf6"),
            ("&#128269;", "Monitor spread daily",    "#dcfce7", "#22c55e"),
        ],
        "tip_days": 2,
    },
    "bacterial_leaf_streak": {
        "plant_emoji": "&#127806;&#128117;", "plant_bg": "#fef3c7",
        "circle_emoji": "&#127807;&#128117;", "circle_bg": "linear-gradient(135deg,#fde68a,#fbbf24)",
        "what_sub": "Your leaves have brown lines running through them.",
        "why_text": "Bacteria enter through wounds and spread in wet and windy weather.",
        "wx_icon": "&#127783;", "wx_icon2": "&#128168;",
        "humidity_label": "High 75%", "weather_label": "Wet &amp; Windy",
        "actions": [
            ("&#127807;", "Remove streaked leaves",  "#bbf7d0", "#4ade80"),
            ("&#129514;", "Spray copper fungicide",  "#ede9fe", "#8b5cf6"),
            ("&#128167;", "Reduce leaf wetness",     "#bfdbfe", "#60a5fa"),
            ("&#128269;", "Check crop daily",        "#dcfce7", "#22c55e"),
        ],
        "tip_days": 4,
    },
    "bacterial_panicle_blight": {
        "plant_emoji": "&#127806;&#128128;", "plant_bg": "#fef2f2",
        "circle_emoji": "&#127806;&#128128;", "circle_bg": "linear-gradient(135deg,#fecaca,#f87171)",
        "what_sub": "Your grain heads are turning brown and not filling properly.",
        "why_text": "Bacteria attack panicles in hot and humid conditions at flowering.",
        "wx_icon": "&#9728;", "wx_icon2": "&#127783;",
        "humidity_label": "High 80%", "weather_label": "Hot &amp; Humid",
        "actions": [
            ("&#127807;", "Remove affected panicles","#bbf7d0", "#4ade80"),
            ("&#129514;", "Apply bactericide spray", "#ede9fe", "#8b5cf6"),
            ("&#128683;", "Stop excess nitrogen",    "#fef3c7", "#fbbf24"),
            ("&#128269;", "Monitor new panicles",    "#dcfce7", "#22c55e"),
        ],
        "tip_days": 3,
    },
    "brown_spot": {
        "plant_emoji": "&#127806;&#129304;", "plant_bg": "#fef9c3",
        "circle_emoji": "&#127807;&#128282;", "circle_bg": "linear-gradient(135deg,#fde68a,#d97706)",
        "what_sub": "Your leaves have brown spots with yellow rings around them.",
        "why_text": "Fungus thrives when nutrients are low and conditions stay wet.",
        "wx_icon": "&#127781;", "wx_icon2": "&#128167;",
        "humidity_label": "Moderate 68%", "weather_label": "Warm &amp; Damp",
        "actions": [
            ("&#127807;", "Remove spotted leaves",   "#bbf7d0", "#4ade80"),
            ("&#129514;", "Apply fungicide spray",   "#ede9fe", "#8b5cf6"),
            ("&#127803;", "Add balanced fertilizer", "#fef3c7", "#fbbf24"),
            ("&#128269;", "Monitor weekly",          "#dcfce7", "#22c55e"),
        ],
        "tip_days": 5,
    },
    "dead_heart": {
        "plant_emoji": "&#127806;&#128128;&#128027;", "plant_bg": "#fef2f2",
        "circle_emoji": "&#128027;&#127806;", "circle_bg": "linear-gradient(135deg,#fed7aa,#f97316)",
        "what_sub": "Some of your young shoots are drying out and not growing.",
        "why_text": "Stem borer insects are feeding inside the stems from the base.",
        "wx_icon": "&#127781;", "wx_icon2": "&#128027;",
        "humidity_label": "Moderate 65%", "weather_label": "Warm Conditions",
        "actions": [
            ("&#9889;",   "Remove dead tillers",     "#fee2e2", "#ef4444"),
            ("&#129514;", "Spray insecticide",       "#ede9fe", "#8b5cf6"),
            ("&#128167;", "Drain field briefly",     "#bfdbfe", "#60a5fa"),
            ("&#128269;", "Check for new damage",    "#dcfce7", "#22c55e"),
        ],
        "tip_days": 2,
    },
    "downy_mildew": {
        "plant_emoji": "&#127806;&#129300;", "plant_bg": "#f0f9ff",
        "circle_emoji": "&#127787;&#127807;", "circle_bg": "linear-gradient(135deg,#e0f2fe,#7dd3fc)",
        "what_sub": "Your leaves have a white or gray powdery coating on the underside.",
        "why_text": "Fungus thrives in cool, moist, and foggy weather conditions.",
        "wx_icon": "&#127787;", "wx_icon2": "&#128168;",
        "humidity_label": "Very High 88%", "weather_label": "Foggy &amp; Cool",
        "actions": [
            ("&#128167;", "Reduce leaf moisture",     "#bfdbfe", "#60a5fa"),
            ("&#127807;", "Remove affected leaves",   "#bbf7d0", "#4ade80"),
            ("&#129514;", "Spray metalaxyl fungicide","#ede9fe", "#8b5cf6"),
            ("&#128168;", "Improve air flow",         "#e0f9ff", "#38bdf8"),
        ],
        "tip_days": 3,
    },
    "hispa": {
        "plant_emoji": "&#127806;&#128027;", "plant_bg": "#fef9c3",
        "circle_emoji": "&#128027;&#127807;", "circle_bg": "linear-gradient(135deg,#fef08a,#eab308)",
        "what_sub": "Your leaves have tiny scratch-like marks and are turning pale.",
        "why_text": "Hispa beetles scrape and mine inside the leaf tissue.",
        "wx_icon": "&#9728;", "wx_icon2": "&#128027;",
        "humidity_label": "Moderate 70%", "weather_label": "Warm &amp; Dry",
        "actions": [
            ("&#9889;",   "Remove infested leaves",  "#fee2e2", "#ef4444"),
            ("&#129514;", "Spray insecticide",       "#ede9fe", "#8b5cf6"),
            ("&#128269;", "Inspect leaves daily",    "#dcfce7", "#22c55e"),
            ("&#127807;", "Thin dense crop areas",   "#bbf7d0", "#4ade80"),
        ],
        "tip_days": 3,
    },
    "tungro": {
        "plant_emoji": "&#127806;&#128184;&#128128;", "plant_bg": "#fef2f2",
        "circle_emoji": "&#127806;&#128184;", "circle_bg": "linear-gradient(135deg,#fde68a,#f97316)",
        "what_sub": "Your leaves are turning yellow-orange quickly — this spreads fast.",
        "why_text": "Virus spread by green leafhoppers — act immediately to stop it.",
        "wx_icon": "&#128027;", "wx_icon2": "&#128128;",
        "humidity_label": "Any Conditions", "weather_label": "Leafhoppers Active",
        "actions": [
            ("&#9889;",   "Remove infected plants",  "#fee2e2", "#ef4444"),
            ("&#129514;", "Spray insecticide now",   "#ede9fe", "#8b5cf6"),
            ("&#128683;", "No nitrogen fertilizer",  "#fef3c7", "#fbbf24"),
            ("&#128269;", "Monitor for leafhoppers", "#dcfce7", "#22c55e"),
        ],
        "tip_days": 1,
    },
    "normal": {
        "plant_emoji": "&#127806;&#127806;&#9989;", "plant_bg": "#f0fdf4",
        "circle_emoji": "&#9989;&#127807;", "circle_bg": "linear-gradient(135deg,#bbf7d0,#22c55e)",
        "what_sub": "No disease found. Your paddy crop looks healthy and strong!",
        "why_text": "Good crop management is keeping your paddy field healthy.",
        "wx_icon": "&#9728;", "wx_icon2": "&#127807;",
        "humidity_label": "Normal 60%", "weather_label": "Favorable",
        "actions": [
            ("&#128167;", "Maintain watering",        "#bfdbfe", "#60a5fa"),
            ("&#127803;", "Apply balanced nutrients", "#fef9c3", "#fbbf24"),
            ("&#128269;", "Inspect weekly",           "#dcfce7", "#22c55e"),
            ("&#127807;", "Keep crop spacing",        "#bbf7d0", "#4ade80"),
        ],
        "tip_days": 7,
    },
    "_default": {
        "plant_emoji": "&#127806;&#129300;", "plant_bg": "#f9fafb",
        "circle_emoji": "&#129300;&#127806;", "circle_bg": "linear-gradient(135deg,#e5e7eb,#9ca3af)",
        "what_sub": "Some unusual signs found on your leaves — keep monitoring closely.",
        "why_text": "Conditions may be favorable for disease development in your area.",
        "wx_icon": "&#127780;", "wx_icon2": "&#127807;",
        "humidity_label": "Unknown", "weather_label": "Monitor Closely",
        "actions": [
            ("&#128269;", "Monitor crop daily",      "#dcfce7", "#22c55e"),
            ("&#127807;", "Remove damaged leaves",   "#bbf7d0", "#4ade80"),
            ("&#129514;", "Consult an expert",       "#ede9fe", "#8b5cf6"),
            ("&#128683;", "Avoid excess fertilizer", "#fef3c7", "#fbbf24"),
        ],
        "tip_days": 3,
    },
}


# ── Per-severity urgency + UI copy ────────────────────────────────────────────

_SEVERITY_STORY: dict[str, dict] = {
    "CRITICAL": {
        "risk_cls":       "sc-risk--high",
        "risk_badge_cls": "sc-risk-badge--high",
        "risk_label":     "&#9888;&#65039; High Risk",
        "risk_msg":       "This can spread fast if we don&#39;t take action today.",
        "sad_leaf":       "&#128148;&#127807;",
        "greeting":       "Vanakkam! &#128075; Your crop needs urgent attention.",
        "greeting_sub":   "I found <strong>{dn}</strong> &mdash; act immediately to stop the spread.",
        "tip_msg":        "Check your field again in {tip_days} days and repeat these steps urgently.",
    },
    "HIGH": {
        "risk_cls":       "sc-risk--high",
        "risk_badge_cls": "sc-risk-badge--high",
        "risk_label":     "&#9888;&#65039; High Risk",
        "risk_msg":       "This can spread fast if we don&#39;t take action today.",
        "sad_leaf":       "&#128148;&#127807;",
        "greeting":       "Vanakkam! &#128075; Your crop needs attention.",
        "greeting_sub":   "I found <strong>{dn}</strong> &mdash; follow the steps below.",
        "tip_msg":        "Check your field again in {tip_days} days and repeat these steps.",
    },
    "MODERATE": {
        "risk_cls":       "sc-risk--mod",
        "risk_badge_cls": "sc-risk-badge--mod",
        "risk_label":     "&#9888;&#65039; Moderate Risk",
        "risk_msg":       "Treatment now will prevent this from spreading further.",
        "sad_leaf":       "&#128528;&#127807;",
        "greeting":       "Vanakkam! &#128075; Your crop needs some care.",
        "greeting_sub":   "I found early signs of <strong>{dn}</strong>. Let me help.",
        "tip_msg":        "Check your field again in {tip_days} days and follow up.",
    },
    "LOW": {
        "risk_cls":       "sc-risk--low",
        "risk_badge_cls": "sc-risk-badge--low",
        "risk_label":     "&#9989; Low Risk",
        "risk_msg":       "Your crop looks mostly healthy. Keep monitoring it.",
        "sad_leaf":       "&#128516;&#127807;",
        "greeting":       "Vanakkam! &#128075; Great news about your crop.",
        "greeting_sub":   "<strong>{dn}</strong> detected &mdash; crop is in good shape.",
        "tip_msg":        "Check your field again in {tip_days} days. Keep it up!",
    },
    "NONE": {
        "risk_cls":       "sc-risk--low",
        "risk_badge_cls": "sc-risk-badge--low",
        "risk_label":     "&#9989; Low Risk",
        "risk_msg":       "Your crop looks mostly healthy. Keep monitoring it.",
        "sad_leaf":       "&#128516;&#127807;",
        "greeting":       "Vanakkam! &#128075; Great news about your crop.",
        "greeting_sub":   "<strong>{dn}</strong> detected &mdash; crop is in good shape.",
        "tip_msg":        "Check your field again in {tip_days} days. Keep it up!",
    },
}

_DEFAULT_SEVERITY = _SEVERITY_STORY["MODERATE"]


# ── Public API ────────────────────────────────────────────────────────────────

def build_story(
    disease: str,
    severity: str,
    confidence: float,
    weather: Optional[dict] = None,
    disease_name: str = "",
) -> FarmerStory:
    """
    Build a FarmerStory from AI diagnosis output.

    Parameters
    ----------
    disease : str
        Machine-readable key (e.g. "blast", "bacterial_leaf_blight", "normal").
    severity : str
        Severity level from AgriInsight ("CRITICAL", "HIGH", "MODERATE", "LOW", "NONE").
    confidence : float
        Model confidence in [0, 1].  Values below 0.55 set is_fallback=True.
    weather : dict, optional
        Result from get_weather_risk(); may be None or {"available": False}.
    disease_name : str, optional
        Human-readable disease name — falls back to title-cased disease key.
    """
    d_data = _DISEASE_DATA.get(disease, _DISEASE_DATA["_default"])
    s_data = _SEVERITY_STORY.get(severity, _DEFAULT_SEVERITY)

    dn       = disease_name or disease.replace("_", " ").title()
    tip_days = d_data["tip_days"]

    return FarmerStory(
        plant_emoji   = d_data["plant_emoji"],
        plant_bg      = d_data["plant_bg"],
        circle_emoji  = d_data["circle_emoji"],
        circle_bg     = d_data["circle_bg"],
        what_sub      = d_data["what_sub"],
        why_text      = d_data["why_text"],
        wx_icon       = d_data["wx_icon"],
        wx_icon2      = d_data["wx_icon2"],
        humidity_label= d_data["humidity_label"],
        weather_label = d_data["weather_label"],
        actions       = d_data["actions"],
        tip_days      = tip_days,
        risk_cls      = s_data["risk_cls"],
        risk_badge_cls= s_data["risk_badge_cls"],
        risk_label    = s_data["risk_label"],
        risk_msg      = s_data["risk_msg"],
        sad_leaf      = s_data["sad_leaf"],
        greeting      = s_data["greeting"],
        greeting_sub  = s_data["greeting_sub"].format(dn=dn),
        tip_msg       = s_data["tip_msg"].format(tip_days=tip_days),
        disease_name  = dn,
        is_fallback   = confidence < _CONFIDENCE_LOW_THRESHOLD,
    )
