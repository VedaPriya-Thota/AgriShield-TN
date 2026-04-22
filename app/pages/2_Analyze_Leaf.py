"""Diagnose · AI crop health assistant — card-based diagnosis flow."""
import sys
import tempfile
import time
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import base64 as _b64
import streamlit as st
from PIL import Image

from _shared import draw_scan, ui_divider, ui_error, ui_footer, inject_sidebar_brand, inject_header
from i18n import t, get_lang

st.session_state["_cur_page"] = "diagnose"
from src.inference.predict import predict_image
from src.inference.explain import generate_gradcam
from src.utils.visualization import get_top_k_predictions, format_class_name
from src.utils.weather import get_weather_risk, DISTRICTS
from src.llm.agri_insight import generate_agri_insight, AgriInsight

# ── Session state ─────────────────────────────────────────────────────────────
if "run_analysis" not in st.session_state:
    st.session_state["run_analysis"] = False
if "last_file_name" not in st.session_state:
    st.session_state["last_file_name"] = None

# ── Load farmer illustration (once, at page load) ─────────────────────────────
_farmer_path = _APP_DIR / "assets" / "farmer_ai.png"
if _farmer_path.exists():
    with open(str(_farmer_path), "rb") as _fp:
        _farmer_src = "data:image/png;base64," + _b64.b64encode(_fp.read()).decode()
else:
    _farmer_src = ""

# ── Animated welcoming header ─────────────────────────────────────────────────
_farmer_img_html = (
    f'<img src="{_farmer_src}" class="diag-welcome-farmer-img" alt="farmer" />'
    if _farmer_src else
    '<span style="font-size:5rem;animation:farmerBob 3s ease-in-out infinite;display:block;">&#128119;&#127996;</span>'
)
st.markdown(
    '<div class="diag-welcome">'
    '<div class="diag-welcome-text">'
    '<div class="diag-welcome-badge">'
    '<span class="diag-welcome-badge-dot"></span>'
    '&#127806; AGRISHIELD-TN &middot; AI CROP DOCTOR'
    '</div>'
    '<div class="diag-welcome-greeting">Vanakkam! &#128075;</div>'
    f'<div class="diag-welcome-sub">{t("diagnose.page_title")}</div>'
    '<div class="diag-welcome-ta">இலை படம் பதிவேற்றுக &middot; AI நோய் கண்டறியும்</div>'
    '<div class="diag-welcome-rice">'
    '<span>&#127806;</span><span>&#127806;</span><span>&#127806;</span><span>&#127806;</span>'
    '</div>'
    '</div>'
    f'<div class="diag-welcome-farmer">{_farmer_img_html}</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Step flow strip ───────────────────────────────────────────────────────────
st.markdown(
    '<div class="diag-steps-strip">'
    '<div class="diag-step-item diag-step-item--active">'
    '<div class="diag-step-circle">1</div>'
    '<div class="diag-step-text">இலை படம்<br><small>Upload Leaf</small></div>'
    '</div>'
    '<div class="diag-step-connector"></div>'
    '<div class="diag-step-item">'
    '<div class="diag-step-circle">2</div>'
    '<div class="diag-step-text">மாவட்டம்<br><small>Select District</small></div>'
    '</div>'
    '<div class="diag-step-connector"></div>'
    '<div class="diag-step-item">'
    '<div class="diag-step-circle">3</div>'
    '<div class="diag-step-text">பகுப்பாய்வு<br><small>Get Diagnosis</small></div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# ── Two-panel input layout ────────────────────────────────────────────────────
col_up, col_det = st.columns([6, 4], gap="large")

with col_up:
    _card_cls = "diag-upload-card diag-upload-card--filled" if st.session_state.get("_has_upload") else "diag-upload-card"
    st.markdown(f'<div class="{_card_cls}">', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "leaf", type=["jpg", "jpeg", "png"], label_visibility="collapsed",
        key="leaf_uploader",
    )

    if uploaded_file is not None:
        img_preview = Image.open(uploaded_file)
        uploaded_file.seek(0)
        st.session_state["_has_upload"] = True
        st.markdown('<div class="diag-preview-wrap">', unsafe_allow_html=True)
        st.image(img_preview, use_container_width=True)
        st.markdown(
            f'<div class="diag-preview-badge">&#10003; {uploaded_file.name}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.session_state["_has_upload"] = False

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div class="diag-examples-strip">'
        '<div class="diag-ex-label">&#128247; Example leaf photos</div>'
        '<div class="diag-ex-photos">'
        '<div class="diag-ex-photo" style="background-image:url(https://images.unsplash.com/photo-1560493236-bb5cdcfe5da8?w=120&q=70&fit=crop)">'
        '<span class="diag-ex-badge diag-ex-badge--bad">Diseased</span></div>'
        '<div class="diag-ex-photo" style="background-image:url(https://images.unsplash.com/photo-1518495973542-4542adad0130?w=120&q=70&fit=crop)">'
        '<span class="diag-ex-badge diag-ex-badge--bad">Affected</span></div>'
        '<div class="diag-ex-photo" style="background-image:url(https://images.unsplash.com/photo-1534208750935-d3523516e85a?w=120&q=70&fit=crop)">'
        '<span class="diag-ex-badge diag-ex-badge--good">Healthy</span></div>'
        '</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="diag-tip">'
        f'{t("diagnose.tip")}'
        '</div>',
        unsafe_allow_html=True,
    )

    if uploaded_file is not None and uploaded_file.name != st.session_state["last_file_name"]:
        st.session_state["run_analysis"] = False
        st.session_state["last_file_name"] = uploaded_file.name

with col_det:
    st.markdown(
        '<div class="diag-field-header" style="background-image:url(https://images.unsplash.com/photo-1574943320219-553eb213f72d?w=400&q=70&auto=format&fit=crop)">'
        '<div class="diag-field-header-overlay">&#127806; Paddy Field &middot; Tamil Nadu</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Status indicator
    if uploaded_file is None:
        st.markdown(
            '<div class="diag-status-card">'
            '<div class="diag-pulse-ring"><div class="diag-pulse-inner">&#128247;</div></div>'
            f'<div class="diag-status-lbl">{t("diagnose.awaiting")}</div>'
            f'<div class="diag-status-sub">{t("diagnose.awaiting_sub")}</div>'
            '<div class="diag-status-ta">இலை படம் பதிவேற்றவும்</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="diag-status-card diag-status-card--ready">'
            '<div class="diag-ready-ring"><div class="diag-ready-inner">&#10003;</div></div>'
            f'<div class="diag-status-lbl diag-status-lbl--ready">{t("diagnose.image_ready")}</div>'
            f'<div class="diag-status-sub">{t("diagnose.image_ready_sub")}</div>'
            '<div class="diag-status-ta">படம் தயாராக உள்ளது ✓</div>'
            '</div>',
            unsafe_allow_html=True,
        )

    # District selector
    st.markdown(
        '<div class="diag-det-card">'
        '<div class="diag-det-label">&#128205; '
        f'{t("diagnose.district_label")}'
        '<span class="diag-det-ta"> · மாவட்டம்</span>'
        '</div>',
        unsafe_allow_html=True,
    )
    district = st.selectbox(
        "district",
        options=[t("diagnose.select_district")] + sorted(DISTRICTS.keys()),
        index=0,
        label_visibility="collapsed",
        help=t("diagnose.tip"),
    )
    st.markdown(
        '<div class="diag-info-box">'
        f'{t("diagnose.crop_label")} <strong>{t("diagnose.crop_name")}</strong><br>'
        f'{t("diagnose.model_label")} <strong>{t("diagnose.model_name")}</strong><br>'
        f'{t("diagnose.classes_label")} <strong>{t("diagnose.classes_val")}</strong>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # CTA inside the right column
    st.markdown('<div class="diag-cta-wrap">', unsafe_allow_html=True)
    clicked = st.button(
        t("diagnose.start_button"),
        use_container_width=True,
        disabled=(uploaded_file is None),
        key="start_diag_btn",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if clicked:
        st.session_state["run_analysis"] = True
        st.rerun()

    if uploaded_file is None:
        st.markdown(
            '<div style="text-align:center;font-size:.77rem;color:#9ca3af;margin-top:4px;">'
            f'{t("diagnose.upload_to_enable")}</div>',
            unsafe_allow_html=True,
        )

# ── Diagnostic parameters strip ───────────────────────────────────────────────
st.markdown('<div class="diag-params-strip">', unsafe_allow_html=True)
_PARAMS = [
    ("&#127806;", "10",       t("diagnose.classes_label")),
    ("&#128205;", "38",       t("common.models_ready")),
    ("&#128293;", "Grad-CAM", t("diagnose.gradcam_title")),
    ("&#9889;",   "&lt;2s",   t("common.instant")),
]
p1, p2, p3, p4 = st.columns(4, gap="small")
for pcol, (icon, val, lbl) in zip([p1, p2, p3, p4], _PARAMS):
    with pcol:
        st.markdown(
            f'<div class="diag-param-card">'
            f'<div class="diag-param-icon">{icon}</div>'
            f'<div class="diag-param-val">{val}</div>'
            f'<div class="diag-param-lbl">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
st.markdown('</div>', unsafe_allow_html=True)

# ── Module-level action helpers ──────────────────────────────────────────────
_ACTION_MAP = [
    (["drain","flood","water","irrigat","standing water"],
     "&#128167;","wtdn-badge--today","TODAY","நீர் வடிகால்",
     "1559827260-dc66d52bef19","linear-gradient(135deg,#0c2a3a,#1e4d6b)"),
    (["crowd","spac","densit","plant distance","thin"],
     "&#127807;","wtdn-badge--week","THIS WEEK","பயிர் இடைவெளி",
     "1574943320219-553eb213f72d","linear-gradient(135deg,#0c2a0c,#1e5a1e)"),
    (["wet","leaf","touch","moist","dew","humid"],
     "&#127811;","wtdn-badge--wet","WHEN WET","ஈர இலைகள்",
     "1500382017468-9049fed747ef","linear-gradient(135deg,#0c1a3a,#1e3060)"),
    (["monitor","inspect","check","watch","survey","daily","spread"],
     "&#128269;","wtdn-badge--daily","DAILY","கண்காணி",
     "1622383563227-04401ab4e5ea","linear-gradient(135deg,#0c2a10,#1a5020)"),
    (["spray","fungicide","pesticide","chemic","insecticid","bactericid","apply"],
     "&#129514;","wtdn-badge--directed","AS DIRECTED","மருந்து தெளி",
     "1587131782738-de30ea91a542","linear-gradient(135deg,#1a1040,#2e1a70)"),
    (["remov","dispos","harvest","uproot","cut","destroy","eliminat"],
     "&#9889;","wtdn-badge--now","IMMEDIATELY","உடனே அகற்று",
     "1536054009244-c43bb5f1c1ac","linear-gradient(135deg,#3a0c0c,#6b1e1e)"),
]

# ── Disease story data (disease → visual story content) ─────────────────────
_DISEASE_STORY_MAP = {
    "blast": {
        "plant_emoji": "&#127806;&#128119;", "plant_bg": "#fef2f2",
        "circle_emoji": "&#128168;&#127807;", "circle_bg": "linear-gradient(135deg,#bfdbfe,#93c5fd)",
        "what_sub": "Gray diamond-shaped spots with brown borders found on your leaves.",
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
        "what_sub": "Yellow water-soaked edges spreading along your leaf borders.",
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
        "what_sub": "Narrow brown streaks running along the veins of your leaves.",
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
        "what_sub": "Panicle grains turning brown and shriveling on your crop.",
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
        "what_sub": "Round brown spots with yellow halos on your leaves.",
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
        "what_sub": "Central tiller shoots are drying out and dying in your crop.",
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
        "what_sub": "White or gray fuzzy growth on the underside of your leaves.",
        "why_text": "Fungus thrives in cool, moist, and foggy weather conditions.",
        "wx_icon": "&#127787;", "wx_icon2": "&#128168;",
        "humidity_label": "Very High 88%", "weather_label": "Foggy &amp; Cool",
        "actions": [
            ("&#128167;", "Reduce leaf moisture",    "#bfdbfe", "#60a5fa"),
            ("&#127807;", "Remove affected leaves",  "#bbf7d0", "#4ade80"),
            ("&#129514;", "Spray metalaxyl fungicide","#ede9fe","#8b5cf6"),
            ("&#128168;", "Improve air flow",        "#e0f9ff", "#38bdf8"),
        ],
        "tip_days": 3,
    },
    "hispa": {
        "plant_emoji": "&#127806;&#128027;", "plant_bg": "#fef9c3",
        "circle_emoji": "&#128027;&#127807;", "circle_bg": "linear-gradient(135deg,#fef08a,#eab308)",
        "what_sub": "Tiny white or brown scratch marks running across your leaves.",
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
        "what_sub": "Leaves turning yellow-orange from tip to base rapidly.",
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
        "what_sub": "No signs of disease detected. Your crop looks healthy!",
        "why_text": "Good crop management is keeping your paddy field healthy.",
        "wx_icon": "&#9728;", "wx_icon2": "&#127807;",
        "humidity_label": "Normal 60%", "weather_label": "Favorable",
        "actions": [
            ("&#128167;", "Maintain watering",       "#bfdbfe", "#60a5fa"),
            ("&#127803;", "Apply balanced nutrients","#fef9c3", "#fbbf24"),
            ("&#128269;", "Inspect weekly",          "#dcfce7", "#22c55e"),
            ("&#127807;", "Keep crop spacing",       "#bbf7d0", "#4ade80"),
        ],
        "tip_days": 7,
    },
    "_default": {
        "plant_emoji": "&#127806;&#129300;", "plant_bg": "#f9fafb",
        "circle_emoji": "&#129300;&#127806;", "circle_bg": "linear-gradient(135deg,#e5e7eb,#9ca3af)",
        "what_sub": "Unusual signs detected on your crop leaves.",
        "why_text": "Conditions may be favorable for disease development in your area.",
        "wx_icon": "&#127780;", "wx_icon2": "&#127807;",
        "humidity_label": "Unknown", "weather_label": "Monitor Closely",
        "actions": [
            ("&#128269;", "Monitor crop daily",       "#dcfce7", "#22c55e"),
            ("&#127807;", "Remove damaged leaves",    "#bbf7d0", "#4ade80"),
            ("&#129514;", "Consult an expert",        "#ede9fe", "#8b5cf6"),
            ("&#128683;", "Avoid excess fertilizer",  "#fef3c7", "#fbbf24"),
        ],
        "tip_days": 3,
    },
}


def _classify_action(text: str):
    lower = text.lower()
    for kws, icon, badge_cls, badge_lbl, ta_lbl, uns_id, fallback_grad in _ACTION_MAP:
        if any(k in lower for k in kws):
            return icon, badge_cls, badge_lbl, ta_lbl, uns_id, fallback_grad
    return "&#127806;","wtdn-badge--daily","DAILY","கவனமாக இரு","1500382017468-9049fed747ef","linear-gradient(135deg,#062010,#103820)"

def _short_title(text: str, max_words: int = 4) -> str:
    words = text.split()
    raw = " ".join(words[:max_words])
    return raw.rstrip(".,;:") + ("…" if len(words) > max_words else "")


# ── Analysis pipeline ─────────────────────────────────────────────────────────
if uploaded_file is not None and st.session_state.get("run_analysis"):

    uploaded_file.seek(0)
    image = Image.open(uploaded_file).convert("RGB")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        image.save(tmp.name)
        temp_path = tmp.name

    try:
        ui_divider()
        st.markdown(
            f'<div class="ds-lbl">{t("diagnose.running_ai")}</div>',
            unsafe_allow_html=True,
        )

        scan_slot = st.empty()
        draw_scan(scan_slot, 0,  5);  time.sleep(0.35)
        draw_scan(scan_slot, 1, 18);  time.sleep(0.30)
        draw_scan(scan_slot, 2, 34);  time.sleep(0.25)
        draw_scan(scan_slot, 3, 50)
        predicted_class, confidence, class_probabilities = predict_image(temp_path)
        top_predictions = get_top_k_predictions(class_probabilities, k=3)
        draw_scan(scan_slot, 4, 78)
        gradcam_overlay, gradcam_class, gradcam_confidence = generate_gradcam(image)
        draw_scan(scan_slot, 5, 95);  time.sleep(0.18)
        draw_scan(scan_slot, 6, 100); time.sleep(0.22)
        scan_slot.empty()

        pct          = confidence * 100
        disease_name = format_class_name(predicted_class)

        SEV_STYLE = {
            "CRITICAL": ("#7f1d1d", "#dc2626", "#fef2f2", "#fecaca", "&#128308;"),
            "HIGH":     ("#92400e", "#d97706", "#fffbeb", "#fde68a", "&#128992;"),
            "MODERATE": ("#1e40af", "#2563eb", "#eff6ff", "#dbeafe", "&#129000;"),
            "LOW":      ("#14532d", "#16a34a", "#f0fdf4", "#bbf7d0", "&#128994;"),
            "NONE":     ("#14532d", "#16a34a", "#f0fdf4", "#bbf7d0", "&#9989;"),
        }

        insight_slot = st.empty()
        insight_slot.markdown(
            '<div style="text-align:center;padding:12px;color:#6b7280;font-size:.85rem;">'
            f'{t("diagnose.generating_adv")}</div>',
            unsafe_allow_html=True,
        )
        insight: AgriInsight = generate_agri_insight(predicted_class, confidence, lang=get_lang())
        insight_slot.empty()

        sev = insight.severity
        sev_text_col, sev_accent, sev_bg_col, sev_border_col, sev_icon = SEV_STYLE.get(
            sev, SEV_STYLE["MODERATE"]
        )

        # ── Save results to session_state for Action Plan page ────────────────
        selected_district = district if district != t("diagnose.select_district") else None
        if selected_district:
            with st.spinner(t("common.loading")):
                wx = get_weather_risk(selected_district, predicted_class)
        else:
            wx = {"available": False}

        st.session_state.update({
            "diag_insight":        insight,
            "diag_disease_name":   disease_name,
            "diag_pct":            pct,
            "diag_sev":            sev,
            "diag_image":          image,
            "diag_gradcam":        gradcam_overlay,
            "diag_top_preds":      top_predictions,
            "diag_wx":             wx,
            "diag_district":       selected_district,
            "diag_predicted_class": predicted_class,
        })

        # ── STORY-BASED VISUAL RESULTS ────────────────────────────────────────
        import base64
        _story = _DISEASE_STORY_MAP.get(predicted_class, _DISEASE_STORY_MAP["_default"])

        # Risk display vars
        if sev in ("CRITICAL", "HIGH"):
            _risk_cls, _risk_badge_cls = "sc-risk--high", "sc-risk-badge--high"
            _risk_label = "&#9888;&#65039; High Risk"
            _risk_msg   = "This can spread fast if we don&#39;t take action today."
            _sad_leaf   = "&#128148;&#127807;"
            _greeting   = f"Vanakkam! &#128075; Your crop needs attention."
            _greeting_sub = f"I found <strong>{disease_name}</strong> &mdash; follow the steps below."
            _tip_msg    = f"Check your field again in {_story['tip_days']} days and repeat these steps."
        elif sev == "MODERATE":
            _risk_cls, _risk_badge_cls = "sc-risk--mod", "sc-risk-badge--mod"
            _risk_label = "&#9888;&#65039; Moderate Risk"
            _risk_msg   = "Treatment now will prevent this from spreading further."
            _sad_leaf   = "&#128528;&#127807;"
            _greeting   = f"Vanakkam! &#128075; Your crop needs some care."
            _greeting_sub = f"I found early signs of <strong>{disease_name}</strong>. Let me help."
            _tip_msg    = f"Check your field again in {_story['tip_days']} days and follow up."
        else:
            _risk_cls, _risk_badge_cls = "sc-risk--low", "sc-risk-badge--low"
            _risk_label = "&#9989; Low Risk"
            _risk_msg   = "Your crop looks mostly healthy. Keep monitoring it."
            _sad_leaf   = "&#128516;&#127807;"
            _greeting   = "Vanakkam! &#128075; Great news about your crop."
            _greeting_sub = f"<strong>{disease_name}</strong> detected &mdash; crop is in good shape."
            _tip_msg    = f"Check your field again in {_story['tip_days']} days. Keep it up!"

        # Farmer illustration
        _farmer_img_path = _APP_DIR / "assets" / "farmer_ai.png"
        if _farmer_img_path.exists():
            with open(str(_farmer_img_path), "rb") as _bf:
                _f64 = base64.b64encode(_bf.read()).decode()
            _farmer_el = f'<img src="data:image/png;base64,{_f64}" class="sg-farmer" />'
        else:
            _farmer_el = '<span class="sg-farmer-emoji">&#128119;&#127996;</span>'

        # 1. Greeting banner
        st.markdown(
            f'<div class="sg-banner">'
            f'<div class="sg-text">'
            f'<div class="sg-title">{_greeting}</div>'
            f'<div class="sg-sub">{_greeting_sub}</div>'
            f'</div>'
            f'{_farmer_el}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 2. What's happening
        st.markdown(
            f'<div class="story-card story-card--d1">'
            f'<div class="sc-illus">'
            f'<div class="sc-illus-plants" style="background:{_story["plant_bg"]};">'
            f'{_story["plant_emoji"]}'
            f'</div>'
            f'</div>'
            f'<div class="sc-body">'
            f'<div class="sc-title">What&#39;s happening in your crop?</div>'
            f'<div class="sc-sub">{_story["what_sub"]}</div>'
            f'<div class="sc-risk {_risk_cls}">'
            f'<span class="sc-risk-badge {_risk_badge_cls}">{_risk_label}</span>'
            f'<span class="sc-risk-text">{_risk_msg}</span>'
            f'</div>'
            f'</div>'
            f'<div class="sc-sad-leaf">{_sad_leaf}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 3. Why is this happening
        if wx.get("available") and isinstance(wx.get("humidity"), (int, float)):
            _hum_display = f"{int(wx['humidity'])}%"
            _wx_display  = wx.get("risk_label", _story["weather_label"])
        else:
            _hum_display = _story["humidity_label"]
            _wx_display  = _story["weather_label"]

        st.markdown(
            f'<div class="story-card story-card--d2">'
            f'<div class="sc-illus">'
            f'<div class="sc-illus-circle" style="background:{_story["circle_bg"]};">'
            f'{_story["circle_emoji"]}'
            f'</div>'
            f'</div>'
            f'<div class="sc-body">'
            f'<div class="sc-title">Why is this happening?</div>'
            f'<div class="sc-sub">{_story["why_text"]}</div>'
            f'<div class="sc-wx-row">'
            f'<div class="sc-wx-card">'
            f'<div class="sc-wx-icon">{_story["wx_icon"]}</div>'
            f'<div><div class="sc-wx-lbl">Humidity</div>'
            f'<div class="sc-wx-val">{_hum_display}</div></div>'
            f'</div>'
            f'<div class="sc-wx-card">'
            f'<div class="sc-wx-icon">{_story["wx_icon2"]}</div>'
            f'<div><div class="sc-wx-lbl">Condition</div>'
            f'<div class="sc-wx-val">{_wx_display}</div></div>'
            f'</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 4. Action cards
        st.markdown('<div class="sa-section-hd">What should you do now?</div>', unsafe_allow_html=True)
        st.markdown('<div class="sa-section-sub">Follow these simple steps to protect your crop.</div>', unsafe_allow_html=True)
        _sa_html = '<div class="sa-grid">'
        for _i, (_ico, _lbl, _bg1, _bg2) in enumerate(_story["actions"][:4], 1):
            _sa_html += (
                f'<div class="sa-card">'
                f'<div class="sa-header">'
                f'<div class="sa-num">{_i}</div>'
                f'<div class="sa-label">{_lbl}</div>'
                f'</div>'
                f'<div class="sa-illus" style="background:linear-gradient(135deg,{_bg1},{_bg2});">'
                f'<span style="font-size:2.8rem;">{_ico}</span>'
                f'<div class="sa-check">&#10003;</div>'
                f'</div>'
                f'</div>'
            )
        _sa_html += '</div>'
        st.markdown(_sa_html, unsafe_allow_html=True)

        # 5. Weather section
        if wx.get("available"):
            _wx_risk = wx.get("risk_level", "UNKNOWN")
            if _wx_risk == "HIGH":
                _sw_cls, _sw_icon, _sw_icon_cls = "sw-section--bad", "&#9928;&#65039;", "sw-icon--cloud"
                _sw_msg   = "Rain expected &#8212; this disease may spread faster. Act quickly!"
                _sw_badge = "&#9928;&#65039; Rainy &rarr; Spread risk is HIGH &#9888;&#65039;"
            elif _wx_risk == "MODERATE":
                _sw_cls, _sw_icon, _sw_icon_cls = "sw-section--mod", "&#127781;&#65039;", "sw-icon--cloud"
                _sw_msg   = "Humid conditions detected. Keep monitoring your crop closely."
                _sw_badge = "&#127781;&#65039; Humid &rarr; Monitor closely"
            else:
                _sw_cls, _sw_icon, _sw_icon_cls = "sw-section--good", "&#9728;&#65039;", "sw-icon--sun"
                _sw_msg   = "Good news! The weather is not helping this problem spread."
                _sw_badge = "&#9728;&#65039; Dry Weather &rarr; Spread is unlikely &#128578;"
        else:
            _sw_cls, _sw_icon, _sw_icon_cls = "sw-section--unk", "&#127780;&#65039;", "sw-icon--sun"
            _sw_msg   = "Weather data not available for your area. Stay vigilant."
            _sw_badge = "&#127780;&#65039; Unknown &rarr; Stay vigilant"

        st.markdown(
            f'<div class="sw-section {_sw_cls}">'
            f'<div class="sw-icon {_sw_icon_cls}">{_sw_icon}</div>'
            f'<div class="sw-content">'
            f'<div class="sw-title">How is the weather today?</div>'
            f'<div class="sw-msg">{_sw_msg}</div>'
            f'<div class="sw-badge">{_sw_badge}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 6. Tip banner
        st.markdown(
            f'<div class="story-tip">'
            f'<span class="st-tip-icon">&#128161;</span>'
            f'<span class="st-tip-text"><strong>Tip:</strong> {_tip_msg}</span>'
            f'<span class="st-tip-farmer">&#128119;&#127996;&#128077;</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


        # ── 5. EXPERT ADVISORY HIDDEN CONTENT ──────────────────────────────────
        ui_divider()
        with st.expander("🔬 View Detailed Expert Analysis", expanded=False):
            st.markdown(f"**Disease Overview:** {insight.summary}")
            st.markdown(f"**Causing Factors:** {insight.cause}")
            st.markdown(f"**Prevention Measures:** {insight.prevention}")

        # ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────
        ui_divider()
        with st.expander(f"&#128444;&#65039; {t('diagnose.gradcam_title')}", expanded=False):
            st.markdown(
                f'<p style="font-size:.82rem;color:#6b7280;margin:0 0 16px;">'
                f'{t("diagnose.gradcam_sub")}'
                '</p>',
                unsafe_allow_html=True,
            )
            img_col, heatmap_col = st.columns(2, gap="large")
            with img_col:
                st.markdown(
                    '<div class="ds-card"><div class="ds-card-hd">'
                    '<span style="width:8px;height:8px;border-radius:50%;background:#16a34a;display:inline-block;"></span>'
                    f'<span style="font-size:.78rem;font-weight:600;color:#374151;">{t("diagnose.original_image")}</span>'
                    '</div><div class="ds-card-bd">',
                    unsafe_allow_html=True,
                )
                st.image(image, use_container_width=True)
                st.markdown('</div></div>', unsafe_allow_html=True)

            with heatmap_col:
                st.markdown(
                    '<div class="ds-card"><div class="ds-card-hd">'
                    '<span style="width:8px;height:8px;border-radius:50%;background:#2563eb;display:inline-block;"></span>'
                    f'<span style="font-size:.78rem;font-weight:600;color:#374151;">{t("diagnose.gradcam_heatmap")}</span>'
                    '</div><div class="ds-card-bd">',
                    unsafe_allow_html=True,
                )
                st.image(gradcam_overlay, use_container_width=True)
                st.markdown('</div></div>', unsafe_allow_html=True)

            gc_pct = gradcam_confidence * 100
            st.markdown(
                f'<div style="background:#eff6ff;border:1px solid #dbeafe;border-radius:10px;padding:12px 16px;margin-top:12px;font-size:.8rem;color:#1d4ed8;">'
                f'&#128300; {t("diagnose.gradcam_note", pct=f"{gc_pct:.1f}")}'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── 5. TOP PREDICTIONS (expander) ─────────────────────────────────────
        with st.expander(f"&#128202; {t('diagnose.breakdown_title')}", expanded=False):
            st.markdown(
                f'<p style="font-size:.82rem;color:#6b7280;margin:0 0 16px;">{t("diagnose.breakdown_sub")}</p>',
                unsafe_allow_html=True,
            )
            RANK_COLORS = [
                ("#16a34a", "#f0fdf4", "#bbf7d0"),
                ("#d97706", "#fffbeb", "#fde68a"),
                ("#6b7280", "#f9fafb", "#e5e7eb"),
            ]
            MEDALS = ["&#129351;", "&#129352;", "&#129353;"]
            for i, (cls_name, prob) in enumerate(top_predictions):
                bar_pct = round(prob * 100, 1)
                name    = format_class_name(cls_name)
                color, bg, border = RANK_COLORS[i]
                st.markdown(
                    f'<div class="ds-card" style="padding:12px 16px;margin-bottom:8px;">'
                    f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:7px;">'
                    f'<span style="font-size:1rem;">{MEDALS[i]}</span>'
                    f'<span style="font-size:.9rem;font-weight:600;color:#111827;flex:1;">{name}</span>'
                    f'<span style="font-size:.8rem;font-weight:700;color:{color};background:{bg};border:1px solid {border};border-radius:999px;padding:2px 10px;">{bar_pct:.1f}%</span>'
                    f'</div>'
                    f'<div style="background:#f3f4f6;border-radius:999px;height:4px;">'
                    f'<div style="background:{color};border-radius:999px;height:4px;width:{bar_pct:.1f}%;"></div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

        # ── Action Plan CTA ────────────────────────────────────────────────────
        ui_divider()
        st.markdown(
            '<div style="text-align:center;margin:4px 0 4px;">'
            '<div style="font-size:.6rem;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:#16a34a;margin-bottom:6px;">&#127806; Your action plan is ready</div>'
            '<div style="font-size:.82rem;color:#6b7280;margin-bottom:16px;">Get detailed treatment steps, prevention measures, and expert guidance.</div>'
            '</div>',
            unsafe_allow_html=True,
        )
        _ap1, _ap2, _ap3 = st.columns([2, 3, 2])
        with _ap2:
            if st.button("⚡ View Full Action Plan", use_container_width=True, key="goto_action_plan"):
                st.switch_page("pages/3_What_To_Do.py")

        st.markdown(
            f'<div style="display:flex;align-items:flex-start;gap:8px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:10px 14px;margin-top:16px;">'
            '<span style="font-size:.85rem;flex-shrink:0;">&#9888;&#65039;</span>'
            f'<span style="font-size:.78rem;color:#9ca3af;line-height:1.55;">'
            f'{t("diagnose.disclaimer")}'
            '</span></div>',
            unsafe_allow_html=True,
        )

    except Exception as e:
        ui_error(str(e))

    finally:
        p = Path(temp_path)
        if p.exists():
            p.unlink()

st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)
ui_footer()
