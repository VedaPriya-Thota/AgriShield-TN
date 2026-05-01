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

# ── WMO weather interpretation codes ─────────────────────────────────────────
# Maps WMO code → (English description, HTML entity icon)
_WMO_CODE: dict[int, tuple[str, str]] = {
    0:  ("Clear sky",           "&#9728;&#65039;"),
    1:  ("Mainly clear",        "&#127780;&#65039;"),
    2:  ("Partly cloudy",       "&#9925;&#65039;"),
    3:  ("Overcast",            "&#9729;&#65039;"),
    45: ("Foggy",               "&#127787;&#65039;"),
    48: ("Icy fog",             "&#127787;&#65039;"),
    51: ("Light drizzle",       "&#127746;&#65039;"),
    53: ("Drizzle",             "&#127746;&#65039;"),
    55: ("Heavy drizzle",       "&#127783;&#65039;"),
    61: ("Light rain",          "&#127783;&#65039;"),
    63: ("Moderate rain",       "&#127783;&#65039;"),
    65: ("Heavy rain",          "&#127783;&#65039;"),
    71: ("Light snow",          "&#10052;&#65039;"),
    73: ("Snow",                "&#10052;&#65039;"),
    75: ("Heavy snow",          "&#10052;&#65039;"),
    77: ("Snow grains",         "&#10052;&#65039;"),
    80: ("Rain showers",        "&#127783;&#65039;"),
    81: ("Rain showers",        "&#127783;&#65039;"),
    82: ("Heavy showers",       "&#9928;&#65039;"),
    85: ("Snow showers",        "&#10052;&#65039;"),
    86: ("Heavy snow showers",  "&#10052;&#65039;"),
    95: ("Thunderstorm",        "&#9928;&#65039;"),
    96: ("Thunderstorm + hail", "&#9928;&#65039;"),
    99: ("Severe thunderstorm", "&#9928;&#65039;"),
}
_WMO_DEFAULT = ("Cloudy", "&#9729;&#65039;")


def _wmo_desc(code) -> tuple[str, str]:
    """Return (description, HTML icon entity) for a WMO weather interpretation code."""
    if code is None:
        return _WMO_DEFAULT
    return _WMO_CODE.get(int(code), _WMO_DEFAULT)


# ── Disease → weather risk rules ──────────────────────────────────────────────

_DISEASE_RISK_RULES: dict[str, dict] = {
    "blast": {
        "humidity_threshold": 80,
        "rain_worsens": True,
        "heat_worsens": False,
        "cold_worsens": True,
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
        "heat_worsens": True,
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
        "heat_worsens": True,
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
    """Fetch current weather + 3-day forecast from Open-Meteo (no API key needed)."""
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,precipitation,"
        f"windspeed_10m,cloudcover,weathercode"
        f"&daily=precipitation_sum,temperature_2m_max,temperature_2m_min,weathercode"
        f"&forecast_days=3"
        f"&timezone=Asia%2FKolkata"
    )
    try:
        with urlopen(url, timeout=6) as resp:
            return json.loads(resp.read().decode())
    except (URLError, Exception) as e:
        logger.warning("OpenMeteo fetch failed: %s", e)
        return None


def _compute_risk(weather: dict, rules: dict) -> tuple[str, str, list[str]]:
    """
    Compute spread risk from raw weather data + disease rules.
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


def _weather_farmer_story(wx: dict, risk_level: str) -> tuple[str, str]:
    """
    Convert live weather data + risk level into a farmer-friendly headline + story.
    Returns (headline, story) both as plain strings (HTML safe, no markup).
    """
    humidity  = wx.get("humidity", 60)
    rain_3day = wx.get("rain_3day", 0)
    rain_now  = wx.get("rain_now", 0)
    temp      = wx.get("temp", 28)

    is_raining = rain_now > 0.1 or rain_3day > 5
    is_humid   = humidity >= 75
    is_hot     = temp >= 33
    is_cool    = temp <= 23

    if risk_level == "HIGH":
        if is_raining:
            return (
                "&#9888;&#65039; Rain detected &mdash; spread risk is HIGH",
                f"Rain and high humidity ({humidity}%) in your area are helping this disease spread faster. Take action today.",
            )
        if is_humid:
            return (
                "&#9888;&#65039; High humidity &mdash; disease spreading conditions",
                f"Humidity is {humidity}% in your area. These damp conditions are actively favouring this disease right now.",
            )
        if is_hot:
            return (
                "&#9888;&#65039; Hot weather &mdash; disease may worsen quickly",
                f"High temperatures ({temp:.0f}&#176;C) in your area are increasing disease activity. Monitor every day.",
            )
        if is_cool:
            return (
                "&#9888;&#65039; Cool and moist &mdash; disease is very active",
                f"The cool, damp conditions ({temp:.0f}&#176;C) are ideal for this disease to spread quickly.",
            )
        return (
            "&#9888;&#65039; Weather is worsening this problem",
            "Current weather conditions in your area are increasing the spread risk. Act without delay.",
        )

    if risk_level == "MODERATE":
        if is_humid:
            return (
                "&#128064; Humid weather &mdash; watch your crop carefully",
                f"Humidity is {humidity}% in your area. These conditions can encourage further spread if ignored.",
            )
        if is_raining:
            return (
                "&#128064; Some rain in the forecast &mdash; stay alert",
                f"Light rainfall expected in your area ({rain_3day:.0f}mm / 3 days). Monitor your crop closely.",
            )
        return (
            "&#128064; Moderate conditions &mdash; stay alert",
            "Weather in your area is not critical right now, but keep monitoring your crop closely.",
        )

    # LOW risk
    if not is_raining and humidity < 70:
        return (
            "&#10003; Dry weather today &mdash; spread risk is low",
            f"Dry conditions ({humidity}% humidity, minimal rain) in your area are not helping this disease spread.",
        )
    return (
        "&#10003; Weather is favourable right now",
        "Current weather conditions are not significantly increasing the disease spread risk in your area.",
    )


def get_weather_risk(district: str, disease: str) -> dict:
    """
    Fetch live weather for a Tamil Nadu district and compute disease spread risk.

    Returns a dict with keys:
        district, lat, lon,
        temp, temp_max, temp_min, humidity, rain_now, rain_3day,
        wind_kmh, cloud_pct, condition (str), condition_icon (HTML entity),
        risk_level ("LOW"|"MODERATE"|"HIGH"|"UNAVAILABLE"),
        risk_label, risk_reasons (list[str]), risk_note (str),
        farmer_headline (str), farmer_story (str),
        available (bool)
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
            "available":  False,
            "district":   district,
            "risk_level": "UNAVAILABLE",
            "risk_note":  rules["risk_note"],
        }

    try:
        current     = weather.get("current", {})
        daily       = weather.get("daily", {})
        temp        = current.get("temperature_2m", "--")
        humidity    = current.get("relative_humidity_2m", "--")
        rain_now    = current.get("precipitation", 0)
        rain_3d     = sum(daily.get("precipitation_sum", [0, 0, 0])[:3])
        temp_max    = max(daily.get("temperature_2m_max", [temp])[:3]) if daily else temp
        temp_min    = min(daily.get("temperature_2m_min", [temp])[:3]) if daily else temp
        wind_kmh    = current.get("windspeed_10m", 0)
        cloud_pct   = current.get("cloudcover", 50)
        weathercode = current.get("weathercode")
        cond_desc, cond_icon = _wmo_desc(weathercode)
    except Exception:
        return {"available": False, "risk_level": "UNAVAILABLE"}

    risk_level, risk_label, risk_reasons = _compute_risk(weather, rules)

    result: dict = {
        "available":       True,
        "district":        district,
        "lat":             lat,
        "lon":             lon,
        "temp":            temp,
        "temp_max":        temp_max,
        "temp_min":        temp_min,
        "humidity":        humidity,
        "rain_now":        rain_now,
        "rain_3day":       rain_3d,
        "wind_kmh":        wind_kmh,
        "cloud_pct":       cloud_pct,
        "condition":       cond_desc,
        "condition_icon":  cond_icon,
        "risk_level":      risk_level,
        "risk_label":      risk_label,
        "risk_reasons":    risk_reasons,
        "risk_note":       rules["risk_note"],
    }

    headline, story = _weather_farmer_story(result, risk_level)
    result["farmer_headline"] = headline
    result["farmer_story"]    = story

    return result
