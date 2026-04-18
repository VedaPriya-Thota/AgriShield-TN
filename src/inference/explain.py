"""
explain.py
==========
Grad-CAM visualisation + dynamic natural-language explanation engine.

Explanation is generated from two signals:
  1. Predicted disease class  – drives disease-specific clinical language
  2. Confidence score         – drives certainty framing and action urgency

Public API
──────────
  generate_gradcam(pil_image)
      → overlay (np.ndarray), predicted_class (str), confidence (float)

  generate_explanation(predicted_class, confidence)
      → ExplanationResult  (dataclass with all explanation fields)

  generate_gradcam_with_explanation(pil_image)
      → overlay, predicted_class, confidence, ExplanationResult
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np
import torch
from PIL import Image
from torchvision import transforms as T

from src.config.config import CHECKPOINT_DIR, IDX_TO_CLASS, IMAGE_SIZE
from src.models.disease_classifier import PaddyDiseaseClassifier


# ─────────────────────────────────────────────────────────────────────────────
#  Confidence thresholds
# ─────────────────────────────────────────────────────────────────────────────

_HIGH   = 0.70   # ≥ 70 % → high confidence
_MEDIUM = 0.40   # ≥ 40 % → medium confidence; below → low


def _confidence_tier(confidence: float) -> str:
    """Return 'high', 'medium', or 'low'."""
    if confidence >= _HIGH:
        return "high"
    if confidence >= _MEDIUM:
        return "medium"
    return "low"


# ─────────────────────────────────────────────────────────────────────────────
#  Disease knowledge base
# ─────────────────────────────────────────────────────────────────────────────
#
#  Each entry contains:
#    display_name   – human-readable label
#    short_desc     – one-sentence clinical description used in the headline
#    symptoms       – bullet-ready symptom list  (≤ 4 items)
#    cause          – pathogen / abiotic cause
#    spread         – transmission route
#    treatment      – primary recommended actions  (≤ 4 items)
#    urgency        – 'critical' | 'high' | 'moderate' | 'low'
#    cam_region     – typical Grad-CAM focus region description

_DISEASE_KB: Dict[str, Dict] = {
    "bacterial_leaf_blight": {
        "display_name": "Bacterial Leaf Blight",
        "short_desc":   "water-soaked lesions turning yellow-white along leaf margins",
        "symptoms": [
            "Water-soaked, greyish-green leaf margins that turn yellow then white",
            "Wilting of young leaves (kresek phase in seedlings)",
            "Ooze of milky-white bacterial exudate in humid conditions",
            "Leaf rolling and premature drying in severe cases",
        ],
        "cause":   "Xanthomonas oryzae pv. oryzae (bacterial)",
        "spread":  "wind-driven rain, irrigation water, and infected plant debris",
        "treatment": [
            "Drain standing water to reduce humidity immediately",
            "Apply copper-based bactericide (e.g., copper oxychloride)",
            "Remove and destroy severely infected tillers",
            "Avoid excessive nitrogen fertilisation",
        ],
        "urgency":     "critical",
        "cam_region":  "leaf margins and tips",
    },

    "bacterial_leaf_streak": {
        "display_name": "Bacterial Leaf Streak",
        "short_desc":   "narrow brown water-soaked streaks running between leaf veins",
        "symptoms": [
            "Translucent, water-soaked streaks between leaf veins",
            "Streaks turn brown-orange with yellow halos over time",
            "Bacterial exudate visible as dried yellowish beads on lesion surface",
            "Lesions confined between veins, unlike blight which spreads from margins",
        ],
        "cause":   "Xanthomonas oryzae pv. oryzicola (bacterial)",
        "spread":  "rain splash, wind, contaminated water, and mechanical contact",
        "treatment": [
            "Reduce leaf wetness by improving field drainage and air circulation",
            "Apply copper-based bactericide at early symptom stage",
            "Use disease-free certified seed for subsequent plantings",
            "Avoid overhead irrigation that prolongs leaf wetness",
        ],
        "urgency":     "high",
        "cam_region":  "inter-vein leaf tissue",
    },

    "bacterial_panicle_blight": {
        "display_name": "Bacterial Panicle Blight",
        "short_desc":   "sterile, chalky-white grains caused by bacterial infection at heading",
        "symptoms": [
            "Sterile or partially filled grains with chalky-white discolouration",
            "Panicle branches turning brown and rotting",
            "Florets remain open (gaping) after infection",
            "Distinct foul odour from infected panicles in humid weather",
        ],
        "cause":   "Burkholderia glumae and B. gladioli (bacterial)",
        "spread":  "seed-borne; spreads via warm, humid weather during heading",
        "treatment": [
            "Hot-water seed treatment (52 °C for 10 minutes) before sowing",
            "Avoid late planting that coincides with high humidity at heading",
            "Apply propiconazole or copper bactericide at boot stage",
            "Remove and burn infected panicles to reduce inoculum",
        ],
        "urgency":     "critical",
        "cam_region":  "panicle and grain clusters",
    },

    "blast": {
        "display_name": "Rice Blast",
        "short_desc":   "diamond-shaped lesions with grey centres causing severe yield loss",
        "symptoms": [
            "Diamond or spindle-shaped lesions with grey-white centres and brown borders",
            "Lesions on leaves, nodes, neck, and panicles (neck rot)",
            "White to grey powdery growth (spores) on lesion surface in humid conditions",
            "Neck blast causes panicle fall-over and total grain loss",
        ],
        "cause":   "Magnaporthe oryzae (fungal)",
        "spread":  "airborne conidia dispersed by wind; favoured by cool nights and leaf wetness",
        "treatment": [
            "Apply tricyclazole or isoprothiolane fungicide at first sign of lesions",
            "Reduce nitrogen application — excess N increases susceptibility",
            "Maintain adequate potassium levels in soil",
            "Plant blast-resistant varieties in high-risk fields",
        ],
        "urgency":     "critical",
        "cam_region":  "leaf blade lesion centres and neck nodes",
    },

    "brown_spot": {
        "display_name": "Brown Spot",
        "short_desc":   "circular brown lesions with yellow halos indicating nutrient stress",
        "symptoms": [
            "Circular to oval brown spots with grey or tan centres on leaves",
            "Yellow halo surrounding individual spots",
            "Spots on leaf sheaths, glumes, and grains (grain discolouration)",
            "Infected seeds appear brown and shrivelled",
        ],
        "cause":   "Bipolaris oryzae (fungal); often exacerbated by nutrient deficiency",
        "spread":  "seed-borne and airborne conidia; worsened by drought and low soil fertility",
        "treatment": [
            "Correct soil nutrient deficiencies (potassium, silicon) with targeted fertilisation",
            "Apply mancozeb or propiconazole fungicide at early symptom onset",
            "Use disease-free certified seed; treat seed with thiram before sowing",
            "Ensure adequate irrigation to avoid moisture stress",
        ],
        "urgency":     "moderate",
        "cam_region":  "leaf blade lesion spots",
    },

    "dead_heart": {
        "display_name": "Dead Heart",
        "short_desc":   "central shoot death caused by stem borer larval feeding",
        "symptoms": [
            "Central leaf whorl turns yellow then dries to form a 'dead heart'",
            "Dead central shoot pulls out easily from the tiller base",
            "Entry/exit holes visible at the base of the stem",
            "Unaffected surrounding tillers appear healthy",
        ],
        "cause":   "Stem borer larvae: Scirpophaga incertulas (yellow) or S. innotata (white)",
        "spread":  "adult moth egg masses on leaves; larvae bore into stems after hatching",
        "treatment": [
            "Apply carbofuran granules or chlorpyrifos at tillering stage",
            "Install pheromone traps to monitor and reduce adult moth populations",
            "Remove and destroy egg masses found on leaves",
            "Encourage natural predators (spiders, parasitic wasps) with reduced broad-spectrum pesticide use",
        ],
        "urgency":     "high",
        "cam_region":  "central shoot and stem base",
    },

    "downy_mildew": {
        "display_name": "Downy Mildew",
        "short_desc":   "pale yellow leaf patches with white downy growth on the underside",
        "symptoms": [
            "Pale yellow-green patches on the upper leaf surface",
            "White to grey cottony fungal growth on the lower leaf surface",
            "Leaves may curl or distort in early infection stages",
            "Systemic infection can cause stunting and reduced tillering",
        ],
        "cause":   "Sclerophthora macrospora (oomycete / water mould)",
        "spread":  "oospores in soil and water; favoured by standing water and cool temperatures",
        "treatment": [
            "Improve field drainage to reduce waterlogging and spore germination",
            "Apply metalaxyl + mancozeb (e.g., Ridomil Gold) at first symptoms",
            "Avoid flood irrigation during cool weather at early crop stages",
            "Use tolerant varieties and practice crop rotation",
        ],
        "urgency":     "moderate",
        "cam_region":  "pale upper-surface patches",
    },

    "hispa": {
        "display_name": "Rice Hispa",
        "short_desc":   "white parallel scraping marks from adult feeding and leaf-mining by larvae",
        "symptoms": [
            "White parallel streaks on leaves from adult beetle scraping the green surface",
            "Transparent, irregular blotches from larvae mining between leaf layers",
            "Heavily infested leaves turn white and wither",
            "Tiny dark-blue iridescent beetles visible on leaf surfaces",
        ],
        "cause":   "Dicladispa armigera (rice hispa beetle — insect)",
        "spread":  "adult beetles migrate from grassy edges; population peaks after transplanting",
        "treatment": [
            "Remove and destroy infested leaf tips containing larvae",
            "Apply chlorpyrifos or imidacloprid at economic threshold (≥1 beetle/hill)",
            "Avoid excessive nitrogen which promotes lush foliage attractive to beetles",
            "Clip infested leaves before spraying to maximise insecticide contact",
        ],
        "urgency":     "moderate",
        "cam_region":  "leaf surface scrape marks and mining blotches",
    },

    "normal": {
        "display_name": "Healthy Paddy",
        "short_desc":   "no disease symptoms detected — plant appears healthy",
        "symptoms": [
            "Uniform green leaf colour with no lesions or discolouration",
            "No visible pest damage or fungal growth",
            "Upright and vigorous plant posture",
            "Normal tillering and leaf development",
        ],
        "cause":   "N/A — no pathogen or stress detected",
        "spread":  "N/A",
        "treatment": [
            "Continue regular monitoring every 7–10 days",
            "Maintain balanced fertilisation schedule",
            "Ensure adequate but not excessive irrigation",
            "Scout for early disease signs at tillering and heading stages",
        ],
        "urgency":     "low",
        "cam_region":  "general leaf structure (no focal anomalies expected)",
    },

    "tungro": {
        "display_name": "Tungro Virus Disease",
        "short_desc":   "yellow-orange leaf discolouration and stunting caused by dual-virus infection",
        "symptoms": [
            "Yellow to orange-yellow discolouration starting from leaf tips",
            "Severe stunting and reduced tillering",
            "Shortened internodes and small, discoloured panicles",
            "Mottling or interveinal chlorosis on younger leaves",
        ],
        "cause":   "Rice tungro bacilliform virus (RTBV) + rice tungro spherical virus (RTSV)",
        "spread":  "green leafhopper (Nephotettix virescens) in a semi-persistent manner",
        "treatment": [
            "Control leafhopper vector with imidacloprid or buprofezin at transplanting",
            "Rogue out and destroy infected plants immediately to reduce inoculum source",
            "Plant tungro-resistant or -tolerant varieties (e.g., IR36, IR64)",
            "Synchronise planting with neighbouring farms to break leafhopper migration cycles",
        ],
        "urgency":     "critical",
        "cam_region":  "leaf tip chlorosis and discoloured younger leaves",
    },
}

# Fallback for any class not explicitly in the KB
_FALLBACK_ENTRY: Dict = {
    "display_name": "Unknown Condition",
    "short_desc":   "unrecognised condition — further expert inspection recommended",
    "symptoms":     ["Anomalous visual pattern detected"],
    "cause":        "Unknown",
    "spread":       "Unknown",
    "treatment":    ["Consult an agricultural specialist for in-field diagnosis"],
    "urgency":      "moderate",
    "cam_region":   "general leaf area",
}


# ─────────────────────────────────────────────────────────────────────────────
#  Confidence-tier language fragments
# ─────────────────────────────────────────────────────────────────────────────

_TIER_LANGUAGE: Dict[str, Dict[str, str]] = {
    "high": {
        "headline_prefix": "High-confidence detection of",
        "reliability":     "The model is highly confident in this prediction. The visual patterns strongly match known disease signatures.",
        "cam_note":        "Grad-CAM attention is tightly focused on the affected region, supporting a reliable diagnosis.",
        "action_urgency":  "Immediate action is recommended.",
    },
    "medium": {
        "headline_prefix": "Likely detection of",
        "reliability":     "The model has moderate confidence. The prediction is plausible but visual evidence may be partially ambiguous.",
        "cam_note":        "Grad-CAM highlights a region of interest, though attention may be spread across multiple areas.",
        "action_urgency":  "Consider field verification before applying treatment.",
    },
    "low": {
        "headline_prefix": "Possible indication of",
        "reliability":     "The model has low confidence. Lighting, image quality, or early-stage symptoms may be limiting detection accuracy.",
        "cam_note":        "Grad-CAM attention is diffuse, suggesting the model could not isolate a clear diagnostic feature.",
        "action_urgency":  "Manual in-field inspection by an agronomist is strongly advised before any intervention.",
    },
}

_URGENCY_BADGE: Dict[str, str] = {
    "critical": "CRITICAL — Act within 24–48 hours",
    "high":     "HIGH — Monitor daily and treat promptly",
    "moderate": "MODERATE — Schedule treatment this week",
    "low":      "LOW — Routine monitoring sufficient",
}


# ─────────────────────────────────────────────────────────────────────────────
#  ExplanationResult dataclass
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class ExplanationResult:
    """
    Structured explanation output.

    Attributes
    ----------
    predicted_class : raw class key (e.g. 'bacterial_leaf_blight')
    display_name    : human-readable disease name
    confidence      : float 0-1
    confidence_pct  : confidence as rounded percentage string (e.g. '87.3%')
    tier            : 'high' | 'medium' | 'low'
    headline        : one-sentence natural-language summary
    short_desc      : clinical one-line description of the condition
    cause           : pathogen / abiotic cause string
    spread          : transmission route string
    symptoms        : list of symptom strings
    treatment       : list of recommended action strings
    urgency         : 'critical' | 'high' | 'moderate' | 'low'
    urgency_label   : full urgency badge string
    reliability     : sentence about prediction confidence quality
    cam_note        : sentence linking Grad-CAM focus to the diagnosis
    action_urgency  : sentence framing how soon to act
    cam_region      : typical region description for Grad-CAM focus
    """
    predicted_class : str
    display_name    : str
    confidence      : float
    confidence_pct  : str
    tier            : str
    headline        : str
    short_desc      : str
    cause           : str
    spread          : str
    symptoms        : List[str]
    treatment       : List[str]
    urgency         : str
    urgency_label   : str
    reliability     : str
    cam_note        : str
    action_urgency  : str
    cam_region      : str


# ─────────────────────────────────────────────────────────────────────────────
#  Core explanation generator
# ─────────────────────────────────────────────────────────────────────────────

def generate_explanation(
    predicted_class: str,
    confidence: float,
) -> ExplanationResult:
    """
    Generate a dynamic, structured explanation for a prediction.

    Parameters
    ----------
    predicted_class : class key from IDX_TO_CLASS (e.g. 'blast')
    confidence      : softmax probability for the predicted class (0–1)

    Returns
    -------
    ExplanationResult with all explanation fields populated.
    """
    kb    = _DISEASE_KB.get(predicted_class, _FALLBACK_ENTRY)
    tier  = _confidence_tier(confidence)
    lang  = _TIER_LANGUAGE[tier]

    display_name  = kb["display_name"]
    confidence_pct = f"{round(confidence * 100, 1):.1f}%"

    headline = (
        lang["headline_prefix"]
        + " "
        + display_name
        + f" ({confidence_pct} confidence) — "
        + kb["short_desc"]
        + "."
    )

    return ExplanationResult(
        predicted_class = predicted_class,
        display_name    = display_name,
        confidence      = confidence,
        confidence_pct  = confidence_pct,
        tier            = tier,
        headline        = headline,
        short_desc      = kb["short_desc"],
        cause           = kb["cause"],
        spread          = kb["spread"],
        symptoms        = kb["symptoms"],
        treatment       = kb["treatment"],
        urgency         = kb["urgency"],
        urgency_label   = _URGENCY_BADGE[kb["urgency"]],
        reliability     = lang["reliability"],
        cam_note        = lang["cam_note"],
        action_urgency  = lang["action_urgency"],
        cam_region      = kb["cam_region"],
    )


# ─────────────────────────────────────────────────────────────────────────────
#  GradCAM
# ─────────────────────────────────────────────────────────────────────────────

class GradCAM:
    def __init__(self, model, target_layer):
        self.model        = model
        self.target_layer = target_layer
        self.gradients    = None
        self.activations  = None

        self.forward_hook  = target_layer.register_forward_hook(self.save_activation)
        self.backward_hook = target_layer.register_full_backward_hook(self.save_gradient)

    def save_activation(self, module, input, output):
        self.activations = output.detach()

    def save_gradient(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def remove_hooks(self):
        self.forward_hook.remove()
        self.backward_hook.remove()

    def generate(self, input_tensor, class_idx=None):
        self.model.zero_grad()
        output = self.model(input_tensor)

        if class_idx is None:
            class_idx = torch.argmax(output, dim=1).item()

        output[:, class_idx].backward()

        gradients  = self.gradients[0]    # [C, H, W]
        activations = self.activations[0] # [C, H, W]
        weights    = gradients.mean(dim=(1, 2))  # [C]

        cam = (weights[:, None, None] * activations).sum(dim=0)
        cam = torch.relu(cam).cpu().numpy()

        if cam.max() > 0:
            cam = cam / cam.max()

        return cam, class_idx


# ─────────────────────────────────────────────────────────────────────────────
#  Model helpers
# ─────────────────────────────────────────────────────────────────────────────

def get_device() -> torch.device:
    return torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(device: Optional[torch.device] = None) -> PaddyDiseaseClassifier:
    if device is None:
        device = get_device()

    checkpoint_path = CHECKPOINT_DIR / "best_disease_classifier.pth"
    if not checkpoint_path.exists():
        raise FileNotFoundError(
            f"Checkpoint not found: {checkpoint_path}. Please train the model first."
        )

    model = PaddyDiseaseClassifier(pretrained=False).to(device)
    state_dict = torch.load(checkpoint_path, map_location=device)
    model.load_state_dict(state_dict)
    model.eval()
    return model


def preprocess_pil_image(pil_image: Image.Image, device: torch.device) -> torch.Tensor:
    pil_image = pil_image.convert("RGB")
    preprocess = T.Compose([
        T.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        T.ToTensor(),
        T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    return preprocess(pil_image).unsqueeze(0).to(device)


def overlay_heatmap_on_image(
    original_image: Image.Image,
    cam: np.ndarray,
    alpha: float = 0.4,
) -> np.ndarray:
    original_np = np.array(original_image.convert("RGB"))
    original_np = cv2.resize(original_np, (IMAGE_SIZE, IMAGE_SIZE))

    heatmap = cv2.resize(cam, (IMAGE_SIZE, IMAGE_SIZE))
    heatmap = cv2.applyColorMap(np.uint8(255 * heatmap), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)

    return cv2.addWeighted(original_np, 1 - alpha, heatmap, alpha, 0)


# ─────────────────────────────────────────────────────────────────────────────
#  Public API
# ─────────────────────────────────────────────────────────────────────────────

def generate_gradcam(
    pil_image: Image.Image,
) -> Tuple[np.ndarray, str, float]:
    """
    Run Grad-CAM and return the overlay, class name, and confidence.

    Returns
    -------
    overlay          : np.ndarray [H, W, 3]  – heatmap blended with original
    predicted_class  : str                   – class key (e.g. 'blast')
    confidence       : float                 – softmax probability 0-1
    """
    device       = get_device()
    model        = load_model(device=device)
    input_tensor = preprocess_pil_image(pil_image, device=device)

    with torch.enable_grad():
        target_layer = model.encoder.feature_extractor[-1]
        gradcam      = GradCAM(model, target_layer)

        logits        = model(input_tensor)
        probabilities = torch.softmax(logits, dim=1)
        predicted_idx = torch.argmax(probabilities, dim=1).item()
        confidence    = probabilities[0, predicted_idx].item()

        cam, class_idx = gradcam.generate(input_tensor, class_idx=predicted_idx)
        gradcam.remove_hooks()

    overlay         = overlay_heatmap_on_image(pil_image, cam)
    predicted_class = IDX_TO_CLASS[class_idx]

    return overlay, predicted_class, confidence


def generate_gradcam_with_explanation(
    pil_image: Image.Image,
) -> Tuple[np.ndarray, str, float, ExplanationResult]:
    """
    Run Grad-CAM and generate a full dynamic explanation in one call.

    Returns
    -------
    overlay         : np.ndarray
    predicted_class : str
    confidence      : float
    explanation     : ExplanationResult
    """
    overlay, predicted_class, confidence = generate_gradcam(pil_image)
    explanation = generate_explanation(predicted_class, confidence)
    return overlay, predicted_class, confidence, explanation
