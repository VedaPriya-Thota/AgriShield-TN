"""
Agri-insight generator for AgriShield-TN.

Takes a disease name + confidence score from the CNN model and generates
a structured, farmer-friendly advisory via the Groq LLM API.

Public API
----------
generate_agri_insight(disease, confidence) -> AgriInsight
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Optional, List

from src.llm.groq_client import call_groq

logger = logging.getLogger(__name__)

# ── Result dataclass ──────────────────────────────────────────────────────────

@dataclass
class AgriInsight:
    disease: str
    display_name: str
    confidence: float
    tier: str                        # "high" | "medium" | "low"
    severity: str                    # "NONE" | "LOW" | "MODERATE" | "HIGH" | "CRITICAL"
    summary: str                     # 1-2 sentence plain description
    cause: str                       # What causes this disease
    action: str                      # Immediate step (paragraph form, for AI advisory block)
    prevention: str                  # How to prevent recurrence
    immediate_actions: List[str]     # Priority-ordered checklist items (3-5 short bullets)
    confidence_note: str             # Confidence-aware framing sentence
    plain_summary: str               # Simple, jargon-free 1-2 sentence version for farmers
    source: str = "groq"             # "groq" | "fallback"
    error: Optional[str] = None


# ── Confidence tier ───────────────────────────────────────────────────────────

def _tier(confidence: float) -> str:
    if confidence >= 0.70:
        return "high"
    if confidence >= 0.40:
        return "medium"
    return "low"


# ── Prompt builder ────────────────────────────────────────────────────────────

_SYSTEM = (
    "You are an expert agronomist specialising in paddy (rice) crop diseases "
    "in Tamil Nadu, India. You provide practical, jargon-free advice that small "
    "and marginal farmers can understand and act on immediately. "
    "You are cautious: you never overclaim, always recommend consulting a "
    "certified agronomist for treatment decisions, and acknowledge uncertainty "
    "when the AI confidence is low. "
    "Respond ONLY with a valid JSON object — no markdown fences, no preamble."
)

_CONFIDENCE_GUIDANCE = {
    "high":   "The AI model has high confidence (≥70%) in this prediction. You may be direct and specific in your advice.",
    "medium": "The AI model has moderate confidence (40-70%). Recommend the farmer verify the diagnosis before acting.",
    "low":    "The AI model has low confidence (<40%). Emphasise that this result is uncertain and that expert inspection is strongly recommended.",
}


def _build_prompt(disease: str, confidence: float, tier: str) -> str:
    pct = confidence * 100
    confidence_instruction = _CONFIDENCE_GUIDANCE[tier]

    return f"""
A paddy leaf image was analysed by an AI disease classifier.

Result:
- Predicted disease: {disease}
- Model confidence: {pct:.1f}%
- Confidence level: {tier}

{confidence_instruction}

Please generate a structured agricultural advisory for a paddy farmer in Tamil Nadu.
Return a JSON object with exactly these keys:

{{
  "summary": "<1-2 sentences describing what this disease is and its impact on paddy crops>",
  "cause": "<1 sentence explaining the main cause or pathogen responsible>",
  "action": "<1-2 sentences of the most important immediate action the farmer should take>",
  "prevention": "<1-2 sentences on how to prevent this disease in future seasons>",
  "confidence_note": "<1 sentence reflecting the confidence level — direct if high, cautious if medium, strongly uncertain if low>",
  "plain_summary": "<1-2 sentences in very simple language a farmer with no technical background can immediately understand, explaining what is wrong with the crop and why it matters>"
}}

Requirements:
- Use simple language suitable for farmers with no technical background.
- Be specific to paddy / rice crops, not generic crop advice.
- Do not recommend specific chemical names unless widely known (e.g., Bordeaux mixture).
- Keep each value concise (max 60 words per field).
- Do not include markdown or extra keys — pure JSON only.
""".strip()


# ── Static fallback knowledge base ────────────────────────────────────────────

_FALLBACK: dict[str, dict] = {
    "bacterial_leaf_blight": {
        "severity": "HIGH",
        "summary":    "Bacterial Leaf Blight is a serious paddy disease causing yellowing and wilting of leaves, which can significantly reduce grain yield.",
        "cause":      "Caused by the bacterium Xanthomonas oryzae pv. oryzae, which spreads through infected water, wind, and contact.",
        "action":     "Remove and destroy infected plant material. Avoid overhead irrigation and improve field drainage immediately.",
        "prevention": "Use disease-resistant varieties and treat seeds before planting. Avoid excessive nitrogen fertilisation.",
        "immediate_actions": [
            "Stop flood irrigation immediately — drain excess water",
            "Remove and burn infected leaves and tillers",
            "Do not apply more nitrogen fertiliser this season",
            "Increase spacing between plants to improve airflow",
            "Consult your local agricultural officer for copper-based spray",
        ],
        "plain_summary": "Your paddy leaves are turning yellow and dying from a bacterial infection. If not controlled quickly, it can destroy your entire crop.",
    },
    "bacterial_leaf_streak": {
        "severity": "MODERATE",
        "summary":    "Bacterial Leaf Streak produces narrow brown streaks on leaves, reducing the plant's ability to photosynthesise.",
        "cause":      "Caused by Xanthomonas oryzae pv. oryzicola, spread by rain splash and wind.",
        "action":     "Improve field drainage and reduce plant density to improve air circulation.",
        "prevention": "Use certified disease-free seeds and avoid injury to plants during field operations.",
        "immediate_actions": [
            "Improve drainage in waterlogged areas of the field",
            "Reduce plant crowding where possible",
            "Avoid working in the field when leaves are wet — spreads bacteria",
            "Monitor daily for spread to new plants",
        ],
        "plain_summary": "Your paddy leaves have narrow brown streaks caused by bacteria spread through rain. It slows crop growth but can be managed if caught early.",
    },
    "bacterial_panicle_blight": {
        "severity": "HIGH",
        "summary":    "Bacterial Panicle Blight causes unfilled or discoloured grains at the panicle stage, directly reducing harvest.",
        "cause":      "Caused by Burkholderia glumae bacteria, favoured by high temperatures and humid conditions.",
        "action":     "Harvest as early as possible to limit further grain damage. Remove affected panicles from the field.",
        "prevention": "Avoid excessive nitrogen application and maintain good field sanitation between seasons.",
        "immediate_actions": [
            "Harvest affected sections of the field as early as possible",
            "Remove and destroy damaged panicles — do not leave in the field",
            "Reduce nitrogen application in remaining crop",
            "Avoid water stress — maintain consistent irrigation",
        ],
        "plain_summary": "Your rice grains are not forming properly due to a bacterial disease in the panicles. This directly reduces your harvest — act quickly.",
    },
    "blast": {
        "severity": "CRITICAL",
        "summary":    "Rice Blast is the most destructive paddy disease, causing diamond-shaped lesions on leaves that can kill entire plants.",
        "cause":      "Caused by the fungus Magnaporthe oryzae, which spreads rapidly under cool, humid, and windy conditions.",
        "action":     "Apply a recommended fungicide (e.g., Tricyclazole) at the first sign of leaf lesions. Avoid excessive nitrogen fertiliser.",
        "prevention": "Plant blast-resistant varieties and maintain field hygiene by removing crop debris after harvest.",
        "immediate_actions": [
            "Apply Tricyclazole fungicide (2g per litre of water) immediately",
            "Remove and burn heavily infected leaves today",
            "Stop applying nitrogen fertiliser — it worsens blast spread",
            "Avoid overhead irrigation for at least 5 days",
            "Check neighbouring fields and alert other farmers",
        ],
        "plain_summary": "Your paddy has Rice Blast — the most dangerous paddy disease. The diamond-shaped spots on leaves will spread fast in cool and wet weather. Act today.",
    },
    "brown_spot": {
        "severity": "MODERATE",
        "summary":    "Brown Spot causes round brown lesions on leaves and grains, reducing photosynthesis and grain quality.",
        "cause":      "Caused by the fungus Bipolaris oryzae, often occurring in nutrient-deficient or drought-stressed crops.",
        "action":     "Apply potassium fertiliser if deficiency is suspected. Ensure adequate and uniform irrigation.",
        "prevention": "Use healthy, certified seeds and apply balanced fertilisation, particularly potassium and silicon.",
        "immediate_actions": [
            "Apply potassium (MOP) fertiliser if soil is deficient",
            "Ensure fields are getting uniform, consistent irrigation",
            "Avoid drought stress — this disease thrives when plants are weak",
            "Apply a fungicide spray if more than 25% of leaves are affected",
        ],
        "plain_summary": "Your paddy leaves have brown spots caused by a fungus that attacks weak, nutrient-starved plants. Improving soil nutrition usually helps control it.",
    },
    "dead_heart": {
        "severity": "MODERATE",
        "summary":    "Dead Heart is caused by stem borer insects and results in the death of the central shoot, leaving a hollow brown stem.",
        "cause":      "The larvae of rice stem borers (Scirpophaga spp.) tunnel into stems and cut off nutrient supply.",
        "action":     "Remove and destroy affected tillers immediately. Set light traps to monitor adult moth activity.",
        "prevention": "Avoid dense planting. Use pheromone traps and encourage natural predators of stem borers.",
        "immediate_actions": [
            "Pull out and destroy all dead heart tillers you can see",
            "Set up light traps at night to catch adult moths",
            "Install pheromone traps to monitor stem borer activity",
            "Avoid excess nitrogen which attracts stem borers",
            "Consider biological control — release Trichogramma parasitoids",
        ],
        "plain_summary": "Small insects (stem borers) have bored into your paddy stems and are killing the centre shoot. You can see the dead centre surrounded by healthy leaves.",
    },
    "downy_mildew": {
        "severity": "MODERATE",
        "summary":    "Downy Mildew causes pale green or yellow patches on leaves with a white fungal growth on the underside.",
        "cause":      "Caused by oomycete pathogens that thrive in cool, wet, and humid conditions.",
        "action":     "Improve field drainage. Remove heavily infected plants from the field.",
        "prevention": "Avoid over-irrigation and maintain adequate plant spacing for airflow.",
        "immediate_actions": [
            "Improve drainage — this disease thrives in wet, waterlogged soil",
            "Remove and destroy the most heavily infected plants",
            "Increase spacing between remaining plants for better airflow",
            "Avoid watering in the evening — wet nights worsen the disease",
        ],
        "plain_summary": "Your paddy leaves have yellow patches and a white coating underneath, caused by a fungus that loves wet, humid conditions. Improving drainage usually helps.",
    },
    "hispa": {
        "severity": "LOW",
        "summary":    "Hispa is a paddy pest that causes white, parallel streaks on leaves as both adults and larvae scrape leaf tissue.",
        "cause":      "Caused by the rice hispa beetle (Dicladispa armigera), which is active during the vegetative stage.",
        "action":     "Clip and destroy the tips of damaged leaves. Avoid excessive nitrogen application which attracts hispa.",
        "prevention": "Monitor crops regularly and use light traps. Encourage natural enemies such as predatory insects.",
        "immediate_actions": [
            "Clip and remove the tips of white-streaked leaves",
            "Reduce nitrogen fertiliser — excess nitrogen attracts hispa beetles",
            "Set up light traps at night to catch adult beetles",
            "Avoid spraying water on leaves — this spreads larvae",
        ],
        "plain_summary": "Small beetles (hispa) are scraping the surface of your paddy leaves, leaving white streaks. The damage looks bad but this pest is usually manageable.",
    },
    "tungro": {
        "severity": "CRITICAL",
        "summary":    "Tungro is a serious viral disease causing yellow-orange discolouration, stunted growth, and significant yield loss.",
        "cause":      "Caused by two viruses (RTBV and RTSV) transmitted by the green leafhopper insect.",
        "action":     "Remove and destroy all infected plants immediately to prevent the leafhopper spreading the virus further.",
        "prevention": "Plant resistant varieties, avoid late planting, and control leafhopper populations with recommended insecticides.",
        "immediate_actions": [
            "Immediately uproot and destroy ALL infected plants — burn them",
            "Apply insecticide to kill leafhoppers before they spread the virus",
            "Do not transplant from infected nurseries to new fields",
            "Alert neighbouring farmers — tungro spreads fast through leafhoppers",
            "Report to your local agricultural office immediately",
        ],
        "plain_summary": "Your paddy has Tungro virus — leaves are turning yellow-orange and plants are stunted. It spreads through tiny insects (leafhoppers) and can devastate the entire crop.",
    },
    "normal": {
        "severity": "NONE",
        "summary":    "The leaf appears healthy with no signs of disease detected by the model.",
        "cause":      "No pathogen detected.",
        "action":     "Continue regular crop monitoring. Maintain good agronomic practices including balanced irrigation and fertilisation.",
        "prevention": "Keep monitoring at weekly intervals, especially during humid periods when disease risk increases.",
        "immediate_actions": [
            "Continue weekly field monitoring",
            "Maintain balanced fertilisation schedule",
            "Ensure consistent irrigation — avoid drought stress",
            "Watch for early signs of pest activity",
        ],
        "plain_summary": "Good news — your paddy leaf looks healthy! Keep monitoring your crop weekly and maintain your current farming practices.",
    },
}

_DEFAULT_FALLBACK = {
    "severity": "MODERATE",
    "summary":    "The AI model has detected a potential paddy disease condition.",
    "cause":      "Specific cause information is not available for this prediction.",
    "action":     "Consult a local agricultural extension officer for a physical crop inspection and accurate diagnosis.",
    "prevention": "Practise good field hygiene, use certified seeds, and monitor crops regularly throughout the season.",
    "immediate_actions": [
        "Do not ignore the symptoms — monitor the field closely",
        "Contact your local agricultural extension officer",
        "Take more photos of affected plants for expert review",
        "Isolate the affected area if possible",
    ],
    "plain_summary": "The AI found something unusual with your paddy leaf. Get an expert to look at it before deciding on any treatment.",
}


def _make_fallback(disease: str, confidence: float, tier: str) -> AgriInsight:
    key = disease.lower().replace(" ", "_").replace("-", "_")
    kb  = _FALLBACK.get(key, _DEFAULT_FALLBACK)

    if tier == "high":
        conf_note = f"The AI model is highly confident ({confidence*100:.0f}%) in this prediction — but always consult a certified agronomist before applying any treatment."
    elif tier == "medium":
        conf_note = f"The AI model has moderate confidence ({confidence*100:.0f}%). Consider verifying this result with a field inspection before taking action."
    else:
        conf_note = f"The AI model has low confidence ({confidence*100:.0f}%). This result is uncertain — please seek expert agronomic advice before acting."

    return AgriInsight(
        disease=disease,
        display_name=disease.replace("_", " ").title(),
        confidence=confidence,
        tier=tier,
        severity=kb.get("severity", "MODERATE"),
        summary=kb["summary"],
        cause=kb["cause"],
        action=kb["action"],
        prevention=kb["prevention"],
        immediate_actions=kb.get("immediate_actions", _DEFAULT_FALLBACK["immediate_actions"]),
        confidence_note=conf_note,
        plain_summary=kb.get("plain_summary", kb["summary"]),
        source="fallback",
    )


# ── JSON parser ───────────────────────────────────────────────────────────────

_REQUIRED_KEYS = {"summary", "cause", "action", "prevention", "confidence_note"}


def _parse_response(raw: str) -> Optional[dict]:
    text = re.sub(r"```(?:json)?", "", raw).strip()

    try:
        data = json.loads(text)
        if _REQUIRED_KEYS.issubset(data.keys()):
            return data
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            data = json.loads(match.group())
            if _REQUIRED_KEYS.issubset(data.keys()):
                return data
        except json.JSONDecodeError:
            pass

    return None


# ── Public function ───────────────────────────────────────────────────────────

def generate_agri_insight(
    disease: str,
    confidence: float,
) -> AgriInsight:
    """
    Generate a structured agricultural advisory for a disease prediction.
    Always returns an AgriInsight — uses Groq if available, otherwise falls
    back to the static knowledge base. Never raises.
    """
    tier    = _tier(confidence)
    display = disease.replace("_", " ").title()
    key     = disease.lower().replace(" ", "_").replace("-", "_")
    kb      = _FALLBACK.get(key, _DEFAULT_FALLBACK)

    try:
        prompt = _build_prompt(disease, confidence, tier)
        raw    = call_groq(user_prompt=prompt, system_prompt=_SYSTEM, max_tokens=700)

        if raw is None:
            return _make_fallback(disease, confidence, tier)

        parsed = _parse_response(raw)
        if parsed is None:
            logger.warning("Could not parse Groq response — using fallback.")
            return _make_fallback(disease, confidence, tier)

        return AgriInsight(
            disease=disease,
            display_name=display,
            confidence=confidence,
            tier=tier,
            severity=kb.get("severity", "MODERATE"),
            summary=parsed.get("summary", ""),
            cause=parsed.get("cause", ""),
            action=parsed.get("action", ""),
            prevention=parsed.get("prevention", ""),
            immediate_actions=kb.get("immediate_actions", _DEFAULT_FALLBACK["immediate_actions"]),
            confidence_note=parsed.get("confidence_note", ""),
            plain_summary=parsed.get("plain_summary", parsed.get("summary", "")),
            source="groq",
        )

    except Exception as exc:
        logger.error("Unexpected error in generate_agri_insight: %s", exc)
        return _make_fallback(disease, confidence, tier)
