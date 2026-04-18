"""
Weather risk assessment for AgriShield-TN.

Uses the OpenMeteo API (free, no API key required) to fetch current weather
and 3-day forecast for a Tamil Nadu district, then maps conditions to a
disease-spread risk level.

Public API
----------
get_weather_risk(district, disease) -> dict
"""

import json
import logging
from urllib.request import urlopen
from urllib.error import URLError

logger = logging.getLogger(__name__)

# ── Tamil Nadu district coordinates ──────────────────────────────────────────

DISTRICTS: dict[str, tuple[float, float]] = {
    "Ariyalur":         (11.14,  79.08),
    "Chengalpattu":     (12.69,  79.98),
    "Chennai":          (13.08,  80.27),
    "Coimbatore":       (11.02,  76.96),
    "Cuddalore":        (11.75,  79.77),
    "Dharmapuri":       (12.13,  78.16),
    "Dindigul":         (10.36,  77.98),
    "Erode":            (11.34,  77.73),
    "Kallakurichi":     (11.74,  78.96),
    "Kancheepuram":     (12.84,  79.70),
    "Karur":            (10.96,  78.08),
    "Krishnagiri":      (12.52,  78.21),
    "Madurai":          ( 9.93,  78.12),
    "Mayiladuthurai":   (11.10,  79.65),
    "Nagapattinam":     (10.77,  79.84),
    "Namakkal":         (11.22,  78.17),
    "Nilgiris":         (11.41,  76.69),
    "Perambalur":       (11.23,  78.88),
    "Pudukkottai":      (10.38,  78.82),
    "Ramanathapuram":   ( 9.37,  78.83),
    "Ranipet":          (12.92,  79.33),
    "Salem":            (11.66,  78.15),
    "Sivaganga":        ( 9.84,  78.48),
    "Tenkasi":          ( 8.96,  77.31),
    "Thanjavur":        (10.79,  79.14),
    "Theni":            (10.01,  77.48),
    "Thoothukudi":      ( 8.76,  78.14),
    "Tiruchirappalli":  (10.79,  78.70),
    "Tirunelveli":      ( 8.73,  77.70),
    "Tirupathur":       (12.49,  78.57),
    "Tiruppur":         (11.11,  77.34),
    "Tiruvallur":       (13.14,  79.91),
    "Tiruvannamalai":   (12.23,  79.07),
    "Tiruvarur":        (10.77,  79.64),
    "Vellore":          (12.92,  79.13),
    "Viluppuram":       (11.94,  79.49),
    "Virudhunagar":     ( 9.58,  77.96),
}

# ── Disease → weather risk rules ──────────────────────────────────────────────
# Each entry defines which conditions raise the spread risk.
# Keys: humidity_threshold, rain_worsens, heat_worsens, cold_worsens

_DISEASE_RISK_RULES: dict[str, dict] = {
    "blast": {
        "humidity_threshold": 80,
        "rain_worsens": True,
        "heat_worsens": False,
        "cold_worsens": True,        # blast favours cool nights
        "risk_note": "Blast spreads rapidly in cool, humid, and rainy conditions.",
    },
    "bacterial_leaf_blight": {
        "humidity_threshold": 75,
        "rain_worsens": True,
        "heat_worsens": True,
        "cold_worsens": False,
        "risk_note": "Bacterial blight worsens with flooding, warm temperatures, and heavy rain.",
    },
    "bacterial_leaf_streak": {
        "humidity_threshold": 75,
        "rain_worsens": True,
        "heat_worsens": False,
        "cold_worsens": False,
        "risk_note": "Rain splash is the main spread mechanism for bacterial leaf streak.",
    },
    "bacterial_panicle_blight": {
        "humidity_threshold": 70,
        "rain_worsens": False,
        "heat_worsens": True,        # high temps favour Burkholderia glumae
        "cold_worsens": False,
        "risk_note": "Panicle blight worsens under high temperature and humidity at flowering.",
    },
    "brown_spot": {
        "humidity_threshold": 70,
        "rain_worsens": False,
        "heat_worsens": True,
        "cold_worsens": False,
        "risk_note": "Brown spot worsens in drought-stressed, hot, and nutrient-deficient crops.",
    },
    "tungro": {
        "humidity_threshold": 70,
        "rain_worsens": False,
        "heat_worsens": True,        # leafhoppers more active in warm weather
        "cold_worsens": False,
        "risk_note": "Tungro spread depends on leafhopper activity, which increases in warm conditions.",
    },
    "hispa": {
        "humidity_threshold": 65,
        "rain_worsens": False,
        "heat_worsens": True,
        "cold_worsens": False,
        "risk_note": "Hispa beetles are more active and multiply faster in warm, humid weather.",
    },
    "dead_heart": {
        "humidity_threshold": 70,
        "rain_worsens": False,
        "heat_worsens": True,
        "cold_worsens": False,
        "risk_note": "Stem borer moths are more active and lay more eggs in warm conditions.",
    },
    "downy_mildew": {
        "humidity_threshold": 80,
        "rain_worsens": True,
        "heat_worsens": False,
        "cold_worsens": True,
        "risk_note": "Downy mildew thrives in wet, cool conditions with poor drainage.",
    },
    "normal": {
        "humidity_threshold": 90,
        "rain_worsens": False,
        "heat_worsens": False,
        "cold_worsens": False,
        "risk_note": "No disease detected — continue monitoring during high-humidity periods.",
    },
}

_DEFAULT_RULES = {
    "humidity_threshold": 75,
    "rain_worsens": True,
    "heat_worsens": False,
    "cold_worsens": False,
    "risk_note": "Monitor weather conditions closely — high humidity increases disease spread risk.",
}


def _fetch_weather(lat: float, lon: float) -> dict | None:
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation"
        f"&daily=precipitation_sum,temperature_2m_max,temperature_2m_min"
        f"&forecast_days=3"
        f"&timezone=Asia%2FKolkata"
    )
    try:
        with urlopen(url, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except (URLError, Exception) as e:
        logger.warning("OpenMeteo fetch failed: %s", e)
        return None


def _compute_risk(weather: dict, rules: dict) -> tuple[str, str, list[str]]:
    """
    Returns (risk_level, risk_label, risk_reasons).
    risk_level: "LOW" | "MODERATE" | "HIGH"
    """
    try:
        current   = weather.get("current", {})
        daily     = weather.get("daily", {})
        humidity  = current.get("relative_humidity_2m", 60)
        temp      = current.get("temperature_2m", 28)
        rain_now  = current.get("precipitation", 0)
        rain_3day = sum(daily.get("precipitation_sum", [0, 0, 0])[:3])
        temp_max  = max(daily.get("temperature_2m_max", [temp])[:3])
    except Exception:
        return "MODERATE", "Moderate Risk", ["Unable to assess — weather data incomplete"]

    risk_score = 0
    reasons: list[str] = []

    if humidity >= rules["humidity_threshold"]:
        risk_score += 2
        reasons.append(f"High humidity ({humidity}%) favours disease spread")

    if rules["rain_worsens"] and (rain_now > 0 or rain_3day > 10):
        risk_score += 2
        reasons.append(f"Rain forecast ({rain_3day:.0f} mm over 3 days) worsens spread")

    if rules["heat_worsens"] and temp_max > 33:
        risk_score += 1
        reasons.append(f"High temperatures ({temp_max:.0f}°C) accelerate disease progression")

    if rules["cold_worsens"] and temp < 24:
        risk_score += 1
        reasons.append(f"Cool temperatures ({temp:.0f}°C) favour this pathogen")

    if risk_score >= 4:
        return "HIGH", "High Spread Risk", reasons
    if risk_score >= 2:
        return "MODERATE", "Moderate Risk", reasons
    return "LOW", "Low Risk", reasons


def get_weather_risk(district: str, disease: str) -> dict:
    """
    Fetch weather for a district and compute disease spread risk.

    Returns a dict with keys:
        district, lat, lon, temp, humidity, rain_now, rain_3day,
        risk_level ("LOW"|"MODERATE"|"HIGH"|"UNAVAILABLE"),
        risk_label, risk_reasons (list[str]), risk_note (str), available (bool)
    """
    coords = DISTRICTS.get(district)
    if coords is None:
        return {"available": False, "risk_level": "UNAVAILABLE"}

    lat, lon = coords
    rules    = _DISEASE_RISK_RULES.get(
        disease.lower().replace(" ", "_").replace("-", "_"),
        _DEFAULT_RULES,
    )

    weather = _fetch_weather(lat, lon)
    if weather is None:
        return {
            "available": False,
            "district": district,
            "risk_level": "UNAVAILABLE",
            "risk_note": rules["risk_note"],
        }

    try:
        current  = weather.get("current", {})
        daily    = weather.get("daily", {})
        temp     = current.get("temperature_2m", "--")
        humidity = current.get("relative_humidity_2m", "--")
        rain_now = current.get("precipitation", 0)
        rain_3d  = sum(daily.get("precipitation_sum", [0, 0, 0])[:3])
        temp_max = max(daily.get("temperature_2m_max", [temp])[:3]) if daily else temp
        temp_min = min(daily.get("temperature_2m_min", [temp])[:3]) if daily else temp
    except Exception:
        return {"available": False, "risk_level": "UNAVAILABLE"}

    risk_level, risk_label, risk_reasons = _compute_risk(weather, rules)

    return {
        "available":    True,
        "district":     district,
        "lat":          lat,
        "lon":          lon,
        "temp":         temp,
        "temp_max":     temp_max,
        "temp_min":     temp_min,
        "humidity":     humidity,
        "rain_now":     rain_now,
        "rain_3day":    rain_3d,
        "risk_level":   risk_level,
        "risk_label":   risk_label,
        "risk_reasons": risk_reasons,
        "risk_note":    rules["risk_note"],
    }
