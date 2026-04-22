"""Field Guide · Disease Library — matches reference UI."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from _shared import ui_footer, inject_sidebar_brand, inject_header
from i18n import t

st.session_state["_cur_page"] = "field_guide"

# ── Page-scoped CSS ───────────────────────────────────────────────────────────
st.markdown(
    '<style>'
    '.dl-page{font-family:"Inter",-apple-system,sans-serif;}'

    # Header
    '.dl-h1{font-size:clamp(1.7rem,2.8vw,2.4rem);font-weight:900;color:#111827;'
    'letter-spacing:-.6px;margin:0 0 6px;}'
    '.dl-sub{font-size:.875rem;color:#6b7280;line-height:1.65;max-width:480px;margin:0 0 16px;}'

    # Tips banner
    '.dl-tips{background:#f8faf8;border:1px solid #e5e7eb;border-radius:14px;'
    'padding:13px 16px;display:flex;gap:12px;align-items:center;}'
    '.dl-tips-imgs{display:flex;gap:5px;flex-shrink:0;}'
    '.dl-tip-img{width:52px;height:38px;border-radius:7px;object-fit:cover;'
    'background:linear-gradient(135deg,#1a3a1a,#2d5a2d);}'
    '.dl-tips-text{font-size:.775rem;color:#4b5563;line-height:1.5;}'

    # Farmer illustration box
    '.dl-farmer-box{background:linear-gradient(135deg,#f0fdf4,#dcfce7);'
    'border:1px solid #bbf7d0;border-radius:18px;padding:20px 18px;'
    'display:flex;align-items:flex-end;justify-content:center;gap:12px;'
    'min-height:130px;position:relative;overflow:hidden;}'
    '.dl-farmer-fig{font-size:5rem;line-height:1;filter:drop-shadow(0 4px 12px rgba(0,0,0,.15));}'
    '.dl-farmer-plant{font-size:4rem;line-height:1;opacity:.85;}'

    # Section label
    '.dl-sec-label{font-size:.6rem;font-weight:700;letter-spacing:2.5px;'
    'text-transform:uppercase;color:#16a34a;margin-bottom:10px;}'

    # Filter row
    '.dl-filter-row{display:flex;align-items:center;gap:10px;margin-bottom:16px;}'

    # Disease cards
    '.dl-card{background:#fff;border:1.5px solid #e5e7eb;border-radius:14px;'
    'overflow:hidden;cursor:pointer;transition:all .18s ease;margin-bottom:12px;}'
    '.dl-card:hover{border-color:#22c55e;box-shadow:0 6px 24px rgba(34,197,94,.18);'
    'transform:translateY(-2px);}'
    '.dl-card.active{border-color:#16a34a;box-shadow:0 0 0 2px #bbf7d0,0 6px 24px rgba(22,163,74,.2);}'
    '.dl-card-img{height:105px;position:relative;display:flex;align-items:flex-end;'
    'justify-content:flex-start;padding:8px;}'
    '.dl-card-sev-badge{position:absolute;top:8px;right:8px;border-radius:999px;'
    'padding:2px 9px;font-size:.58rem;font-weight:800;letter-spacing:.5px;}'
    '.dl-card-critical-label{border-radius:999px;padding:3px 10px;'
    'font-size:.6rem;font-weight:800;letter-spacing:.4px;}'
    '.dl-card-body{padding:10px 13px 12px;}'
    '.dl-card-name{font-size:.9rem;font-weight:800;color:#111827;margin-bottom:7px;}'
    '.dl-sev-bar{height:18px;display:flex;gap:3px;border-radius:5px;overflow:hidden;}'
    '.dl-sev-seg{flex:1;display:flex;align-items:flex-end;padding:0 5px 3px;}'
    '.dl-sev-seg-lbl{font-size:.5rem;color:rgba(255,255,255,.9);font-weight:600;white-space:nowrap;}'

    # Detail panel
    '.dl-detail{background:#fff;border:1px solid #e5e7eb;border-radius:18px;'
    'overflow:hidden;box-shadow:0 4px 24px rgba(0,0,0,.07);}'
    '.dl-detail-top{background:#f0fdf4;border-bottom:1px solid #d1fae5;'
    'padding:12px 16px;}'
    '.dl-detail-body{padding:16px;}'

    # Symptoms
    '.dl-sym-wrap{display:flex;gap:12px;align-items:flex-start;margin-bottom:12px;}'
    '.dl-sym-img{width:80px;height:72px;border-radius:10px;flex-shrink:0;'
    'object-fit:cover;border:1px solid #e5e7eb;}'
    '.dl-sym-list{flex:1;}'
    '.dl-sym-item{display:flex;gap:7px;align-items:flex-start;margin-bottom:5px;}'
    '.dl-sym-bullet{font-size:.75rem;flex-shrink:0;margin-top:1px;}'
    '.dl-sym-text{font-size:.775rem;color:#374151;line-height:1.45;}'

    # Conditions
    '.dl-cond-box{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:11px;'
    'padding:12px 14px;margin:12px 0;}'
    '.dl-cond-items{display:flex;gap:6px;margin-top:8px;}'
    '.dl-cond-item{flex:1;text-align:center;background:#fff;border:1px solid #d1fae5;'
    'border-radius:9px;padding:9px 5px;}'
    '.dl-cond-icon{font-size:1.5rem;line-height:1;margin-bottom:4px;}'
    '.dl-cond-lbl{font-size:.65rem;font-weight:600;color:#374151;}'

    # Actions
    '.dl-actions-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;}'
    '.dl-action-card{background:#f9fafb;border:1px solid #e5e7eb;border-radius:9px;'
    'padding:10px 6px;text-align:center;}'
    '.dl-action-icon{font-size:1.4rem;line-height:1;margin-bottom:5px;}'
    '.dl-action-lbl{font-size:.65rem;font-weight:700;color:#374151;line-height:1.3;}'

    # Severity badge colours
    '.sev-critical{background:#fee2e2;color:#dc2626;}'
    '.sev-high{background:#fef3c7;color:#d97706;}'
    '.sev-moderate{background:#fff7ed;color:#ea580c;}'
    '.sev-low{background:#f0fdf4;color:#16a34a;}'
    '.sev-none{background:#f0fdf4;color:#16a34a;}'
    '</style>',
    unsafe_allow_html=True,
)

# ── Disease database ──────────────────────────────────────────────────────────
DISEASES = [
    {
        "key": "blast", "name": "Blast", "icon": "🔴",
        "severity": "CRITICAL", "sev_class": "sev-critical",
        "sev_color": "#dc2626", "sev_bg": "#fee2e2", "sev_border": "#fecaca",
        "accent": "#dc2626",
        "unsplash_id": "1560493236-bb5cdcfe5da8",
        "card_gradient": "linear-gradient(150deg,#0c1f0c 0%,#193219 55%,rgba(220,38,38,.35) 100%)",
        "detail_gradient": "linear-gradient(135deg,#0c1f0c,#1a3a1a)",
        "pathogen": "Magnaporthe oryzae (fungus)",
        "spread": "Wind, water splash, infected seeds",
        "conditions": ["Cool air", "Humid fog", "Heavy dew"],
        "conditions_icon": ["🌬️", "🌫️", "💧"],
        "symptoms": [
            "Diamond-shaped grey-white lesions with brown margins on leaves",
            "Grey-white sions with brown margins on leaves",
            "White or grey neck rot at panicle case (neck blast)",
            "Rapid leaf death in severe cases — \"fire blight\"",
        ],
        "actions": ["Dispose Affected Plants", "Apply Balanced Nitrogen", "Prevent Recurrence Plan"],
        "actions_icon": ["🪣", "🧪", "📋"],
        "note": "Most destructive paddy disease globally. Can cause 100% yield loss in severe neck blast.",
        "severity_bar": [("Light spotting", "#fde68a"), ("Disease progression", "#f97316"), ("Fire blight", "#dc2626")],
    },
    {
        "key": "bacterial_leaf_blight", "name": "Bacterial Leaf Blight", "icon": "🟡",
        "severity": "HIGH", "sev_class": "sev-high",
        "sev_color": "#d97706", "sev_bg": "#fef3c7", "sev_border": "#fde68a",
        "accent": "#d97706",
        "unsplash_id": "1574943320219-553eb213f72d",
        "card_gradient": "linear-gradient(150deg,#1a2e0a 0%,#2a4a10 55%,rgba(217,119,6,.3) 100%)",
        "detail_gradient": "linear-gradient(135deg,#1a2e0a,#2a4a10)",
        "pathogen": "Xanthomonas oryzae pv. oryzae",
        "spread": "Infected water, wind, contact",
        "conditions": ["Warm temps", "High humidity", "Strong winds"],
        "conditions_icon": ["🌡️", "💦", "🌬️"],
        "symptoms": [
            "Water-soaked to yellowish stripe on leaf margins",
            "Lesions turn white or yellow, dry from tip downwards",
            "Milky bacterial ooze on cut leaf ends under humid conditions",
        ],
        "actions": ["Drain Flooded Fields", "Reduce Nitrogen", "Apply Bactericide"],
        "actions_icon": ["💧", "🌱", "🧪"],
        "note": "Spreads rapidly through irrigation water. Major yield loss during kharif season.",
        "severity_bar": [("Water-soaking", "#fde68a"), ("Water soaking", "#d97706")],
    },
    {
        "key": "bacterial_leaf_streak", "name": "Bacterial Leaf Streak", "icon": "🟠",
        "severity": "MODERATE", "sev_class": "sev-moderate",
        "sev_color": "#ea580c", "sev_bg": "#fff7ed", "sev_border": "#fed7aa",
        "accent": "#ea580c",
        "unsplash_id": "1500382017468-9049fed747ef",
        "card_gradient": "linear-gradient(150deg,#161206 0%,#2a2010 55%,rgba(234,88,12,.3) 100%)",
        "detail_gradient": "linear-gradient(135deg,#161206,#2a2010)",
        "pathogen": "Xanthomonas oryzae pv. oryzicola",
        "spread": "Rain splash, wind, irrigation water",
        "conditions": ["High rainfall", "High temperature", "Dense planting"],
        "conditions_icon": ["🌧️", "☀️", "🌾"],
        "symptoms": [
            "Narrow water-soaked translucent streaks between leaf veins",
            "Streaks turn brown with yellow halo on margins",
            "Visible yellowish bacterial exudate (beads) on lesion surface",
        ],
        "actions": ["Reduce Plant Density", "Improve Drainage", "Limit Nitrogen"],
        "actions_icon": ["🌿", "💧", "🌱"],
        "note": "Often confused with BLB but affects different host tissue.",
        "severity_bar": [("Early streaks", "#fed7aa"), ("Brown lesions", "#ea580c")],
    },
    {
        "key": "bacterial_panicle_blight", "name": "Bacterial Panicle Blight", "icon": "🟤",
        "severity": "HIGH", "sev_class": "sev-high",
        "sev_color": "#92400e", "sev_bg": "#fef3c7", "sev_border": "#fde68a",
        "accent": "#92400e",
        "unsplash_id": "1592982538153-3a28d4e4e7e1",
        "card_gradient": "linear-gradient(150deg,#1a1006 0%,#2a1a08 55%,rgba(146,64,14,.35) 100%)",
        "detail_gradient": "linear-gradient(135deg,#1a1006,#2a1a08)",
        "pathogen": "Burkholderia glumae (bacterium)",
        "spread": "Infected seeds, splashing water",
        "conditions": ["High night temps", "High humidity", "Heading stage"],
        "conditions_icon": ["🌡️", "💦", "🌾"],
        "symptoms": [
            "Discolouration of glumes (hulls) — turning pale to brown",
            "Sterile, shrivelled or unfilled grains in panicle",
            "Rotting at grain base with pinkish bacterial mass",
        ],
        "actions": ["Harvest Early", "Remove Affected Panicles", "Seed Treatment"],
        "actions_icon": ["🌾", "🪣", "🌱"],
        "note": "Occurs at heading/grain-filling stage. Significant economic loss in affected seasons.",
        "severity_bar": [("Glume discolouration", "#fde68a"), ("Grain sterility", "#92400e")],
    },
    {
        "key": "brown_spot", "name": "Brown Spot", "icon": "🟫",
        "severity": "MODERATE", "sev_class": "sev-moderate",
        "sev_color": "#78350f", "sev_bg": "#fdf6ec", "sev_border": "#fcd9a8",
        "accent": "#78350f",
        "unsplash_id": "1518495973542-4542adad0130",
        "card_gradient": "linear-gradient(150deg,#120a04 0%,#1e1206 55%,rgba(120,53,15,.35) 100%)",
        "detail_gradient": "linear-gradient(135deg,#120a04,#1e1206)",
        "pathogen": "Bipolaris oryzae (fungus)",
        "spread": "Wind, infected seeds, soil debris",
        "conditions": ["Nutrient deficiency", "Drought stress", "Poor soils"],
        "conditions_icon": ["🌱", "☀️", "🏜️"],
        "symptoms": [
            "Oval or circular brown lesions (2–14 mm) on leaves",
            "Lesions have whitish-grey centre with dark brown margin",
            "Small dark brown spots on glumes reduce grain quality",
        ],
        "actions": ["Apply Potassium", "Maintain Soil Moisture", "Fungicide Treatment"],
        "actions_icon": ["🌿", "💧", "🧪"],
        "note": "Often a secondary disease of stressed crops. Correcting nutrients reduces severity.",
        "severity_bar": [("Early spots", "#fcd9a8"), ("Spread", "#78350f")],
    },
    {
        "key": "dead_heart", "name": "Dead Heart", "icon": "💀",
        "severity": "HIGH", "sev_class": "sev-high",
        "sev_color": "#374151", "sev_bg": "#f9fafb", "sev_border": "#e5e7eb",
        "accent": "#374151",
        "unsplash_id": "1581092921461-eab10380ed66",
        "card_gradient": "linear-gradient(150deg,#0e1016 0%,#1c1e24 55%,rgba(55,65,81,.45) 100%)",
        "detail_gradient": "linear-gradient(135deg,#0e1016,#1c1e24)",
        "pathogen": "Rice stem borer larvae (Scirpophaga spp.)",
        "spread": "Adult moths lay eggs on leaves; larvae bore into stems",
        "conditions": ["Vegetative stage", "Dense planting", "High nitrogen"],
        "conditions_icon": ["🌱", "🌾", "🧪"],
        "symptoms": [
            "Central tiller shoot turns yellow-brown and dies",
            "Dead shoot pulls out easily with hollow rotting base",
            "Presence of larval frass (excrement) inside the stem",
        ],
        "actions": ["Remove Dead Hearts", "Set Pheromone Traps", "Avoid Excess Nitrogen"],
        "actions_icon": ["🪣", "🪤", "🌱"],
        "note": "Most damaging during vegetative phase. Similar symptom (white ear) at reproductive stage.",
        "severity_bar": [("Early infestation", "#d1d5db"), ("Dead heart", "#374151")],
    },
    {
        "key": "downy_mildew", "name": "Downy Mildew", "icon": "🟢",
        "severity": "LOW", "sev_class": "sev-low",
        "sev_color": "#0d9488", "sev_bg": "#f0fdfa", "sev_border": "#99f6e4",
        "accent": "#0d9488",
        "unsplash_id": "1518611012118-696072aa579a",
        "card_gradient": "linear-gradient(150deg,#041410 0%,#082820 55%,rgba(13,148,136,.3) 100%)",
        "detail_gradient": "linear-gradient(135deg,#041410,#082820)",
        "pathogen": "Sclerophthora macrospora (oomycete)",
        "spread": "Infected plant debris, zoospores via water",
        "conditions": ["Waterlogged", "Cool weather", "High humidity"],
        "conditions_icon": ["💧", "❄️", "💦"],
        "symptoms": [
            "Pale green or yellowish patches on upper leaf surface",
            "White cottony/downy sporulation on underside of leaves",
            "Affected plants may show yellowing and stunting",
        ],
        "actions": ["Drain Waterlogged Fields", "Remove Infected Plants", "Improve Drainage"],
        "actions_icon": ["💧", "🪣", "🌾"],
        "note": "Relatively rare in well-drained paddy fields. Associated with waterlogged conditions.",
        "severity_bar": [("Yellowing", "#99f6e4"), ("Downy growth", "#0d9488")],
    },
    {
        "key": "hispa", "name": "Hispa", "icon": "🐛",
        "severity": "MODERATE", "sev_class": "sev-moderate",
        "sev_color": "#7c3aed", "sev_bg": "#faf5ff", "sev_border": "#ede9fe",
        "accent": "#7c3aed",
        "unsplash_id": "1495555775-c21e03d4d6fa",
        "card_gradient": "linear-gradient(150deg,#100a1e 0%,#1e1232 55%,rgba(124,58,237,.3) 100%)",
        "detail_gradient": "linear-gradient(135deg,#100a1e,#1e1232)",
        "pathogen": "Rice hispa beetle — Dicladispa armigera (insect)",
        "spread": "Adult insects fly; larvae mine inside leaf tissue",
        "conditions": ["Vegetative stage", "High humidity", "Excess nitrogen"],
        "conditions_icon": ["🌱", "💦", "🧪"],
        "symptoms": [
            "White parallel streaks on leaves where adults scraped the surface",
            "Blistered or blotchy appearance from leaf-mining larvae",
            "Severe infestation causes whitening and drying of entire leaf",
        ],
        "actions": ["Clip Leaf Tips with Larvae", "Light Traps", "Targeted Insecticide"],
        "actions_icon": ["✂️", "💡", "🧪"],
        "note": "Both adult beetles and larvae damage leaves simultaneously. Early detection is critical.",
        "severity_bar": [("White streaks", "#ede9fe"), ("Leaf whitening", "#7c3aed")],
    },
    {
        "key": "tungro", "name": "Tungro", "icon": "🟣",
        "severity": "CRITICAL", "sev_class": "sev-critical",
        "sev_color": "#6d28d9", "sev_bg": "#faf5ff", "sev_border": "#c4b5fd",
        "accent": "#6d28d9",
        "unsplash_id": "1444930694458-01babdd684e7",
        "card_gradient": "linear-gradient(150deg,#0e0618 0%,#1c0e30 55%,rgba(109,40,217,.3) 100%)",
        "detail_gradient": "linear-gradient(135deg,#0e0618,#1c0e30)",
        "pathogen": "Rice Tungro Bacilliform Virus (RTBV) + RTSV",
        "spread": "Green leafhopper (Nephotettix virescens)",
        "conditions": ["High leafhopper", "Susceptible variety", "Late planting"],
        "conditions_icon": ["🦗", "🌱", "📅"],
        "symptoms": [
            "Yellow-orange discolouration of leaves starting from the tip",
            "Stunted plant growth — infected plants noticeably shorter",
            "Reduced tiller number and very poor grain filling",
        ],
        "actions": ["Remove Infected Plants", "Control Leafhoppers", "Plant Resistant Varieties"],
        "actions_icon": ["🪣", "🦗", "🌱"],
        "note": "No curative treatment — only prevention and vector control. Most serious rice disease in Asia.",
        "severity_bar": [("Yellow tips", "#c4b5fd"), ("Stunting", "#6d28d9")],
    },
    {
        "key": "normal", "name": "Normal (Healthy)", "icon": "✅",
        "severity": "NONE", "sev_class": "sev-none",
        "sev_color": "#16a34a", "sev_bg": "#f0fdf4", "sev_border": "#bbf7d0",
        "accent": "#16a34a",
        "unsplash_id": "1534208750935-d3523516e85a",
        "card_gradient": "linear-gradient(150deg,#062010 0%,#103820 55%,rgba(22,163,74,.3) 100%)",
        "detail_gradient": "linear-gradient(135deg,#062010,#103820)",
        "pathogen": "No pathogen detected",
        "spread": "N/A",
        "conditions": ["Balanced irrigation", "Adequate nutrients", "Good drainage"],
        "conditions_icon": ["💧", "🌿", "🌾"],
        "symptoms": [
            "Uniform green colouration across the entire leaf surface",
            "No lesions, streaks, spots or discolouration visible",
            "Leaf texture and size consistent with expected variety growth",
        ],
        "actions": ["Continue Monitoring", "Maintain Irrigation", "Weekly Inspection"],
        "actions_icon": ["👁️", "💧", "📋"],
        "note": "A healthy leaf classification confirms your crop is in good condition at this growth stage.",
        "severity_bar": [("Healthy", "#bbf7d0")],
    },
]

# ── State ────────────────────────────────────────────────────────────────────
if "selected_disease" not in st.session_state:
    st.session_state["selected_disease"] = DISEASES[0]["key"]
if "dl_filter" not in st.session_state:
    st.session_state["dl_filter"] = t("disease_lib.filter_all")

selected = next(d for d in DISEASES if d["key"] == st.session_state["selected_disease"])

# ── Top header row ────────────────────────────────────────────────────────────
hdr_left, hdr_right = st.columns([3, 1], gap="large")

with hdr_left:
    st.markdown(
        '<div style="padding:1.5rem 0 0;">'
        f'<h1 class="dl-h1">{t("disease_lib.title")}</h1>'
        f'<p class="dl-sub">{t("disease_lib.subtitle")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )
    # Tips banner — real disease leaf photos
    _TIP_PHOTOS = [
        "1560493236-bb5cdcfe5da8",   # blast lesions
        "1574943320219-553eb213f72d", # bacterial blight
        "1518495973542-4542adad0130", # brown spot
    ]
    leaf_imgs = ''.join([
        f'<div class="dl-tip-img" style="background-image:url(https://images.unsplash.com/photo-{pid}?w=120&q=70&auto=format&fit=crop);background-size:cover;background-position:center;"></div>'
        for pid in _TIP_PHOTOS
    ])
    st.markdown(
        '<div class="dl-tips">'
        f'<div class="dl-tips-imgs">{leaf_imgs}</div>'
        '<div class="dl-tips-text">'
        f'{t("disease_lib.tips_text")}'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with hdr_right:
    st.markdown(
        '<style>'
        '@keyframes sunGlow{0%,100%{opacity:.85;transform:scale(1);}50%{opacity:1;transform:scale(1.12);}}'
        '</style>'
        '<div style="padding:1.5rem 0 0;">'
        '<div style="border-radius:18px;overflow:hidden;min-height:145px;position:relative;">'
        # Real farmer photo background
        '<img src="https://images.unsplash.com/photo-1566702693566-f3a2ac30282c?w=400&q=80&auto=format&fit=crop" '
        'style="width:100%;height:160px;object-fit:cover;object-position:center 30%;display:block;" />'
        # Overlay with text
        '<div style="position:absolute;inset:0;background:linear-gradient(to top,rgba(5,46,22,.88) 0%,rgba(5,46,22,.35) 55%,transparent 100%);">'
        '</div>'
        '<div style="position:absolute;bottom:12px;left:14px;right:14px;z-index:2;">'
        '<div style="font-size:.65rem;font-weight:800;letter-spacing:1.5px;text-transform:uppercase;color:rgba(255,255,255,.7);margin-bottom:3px;">&#127806; AgriShield-TN</div>'
        '<div style="font-size:.82rem;font-weight:700;color:#fff;line-height:1.35;">AI-powered disease<br>detection for farmers</div>'
        '<div style="font-size:.68rem;color:rgba(255,255,255,.6);font-family:&quot;Noto Sans Tamil&quot;,sans-serif;margin-top:3px;">விவசாயிகளுக்கான AI நோய் கண்டறிதல்</div>'
        '</div>'
        # Sun badge top-right
        '<span style="position:absolute;top:10px;right:12px;font-size:1.4rem;z-index:2;'
        'animation:sunGlow 3s ease-in-out infinite;filter:drop-shadow(0 0 6px rgba(251,191,36,.7));">&#9728;&#65039;</span>'
        '</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

# ── Main two-column layout ────────────────────────────────────────────────────
cards_col, detail_col = st.columns([55, 45], gap="large")

# ── LEFT: card grid ───────────────────────────────────────────────────────────
with cards_col:
    st.markdown(
        f'<div class="dl-sec-label">{t("disease_lib.all_classes")}</div>',
        unsafe_allow_html=True,
    )

    sev_options = [t("disease_lib.filter_all"), "CRITICAL", "HIGH", "MODERATE", "LOW", "NONE"]
    filt_c, _ = st.columns([2.5, 5])
    with filt_c:
        selected_sev = st.selectbox(t("disease_lib.filter_label"), options=sev_options, label_visibility="visible", key="dl_sev_filter")

    shown = DISEASES if selected_sev == t("disease_lib.filter_all") else [d for d in DISEASES if d["severity"] == selected_sev]

    for row_start in range(0, len(shown), 2):
        row_d = shown[row_start:row_start + 2]
        c1, c2 = st.columns(2, gap="small")
        for col, d in zip([c1, c2], row_d):
            with col:
                is_active = d["key"] == st.session_state["selected_disease"]
                active_class = "active" if is_active else ""

                bar_html = "".join(
                    f'<div class="dl-sev-seg" style="background:{c};">'
                    f'<span class="dl-sev-seg-lbl">{lbl}</span></div>'
                    for lbl, c in d["severity_bar"]
                )

                sev_lbl_color = d["sev_color"]
                sev_lbl_bg   = d["sev_bg"]

                _uns_id  = d.get("unsplash_id", "")
                _bg_url  = f"https://images.unsplash.com/photo-{_uns_id}?w=400&q=75&auto=format&fit=crop" if _uns_id else ""
                _bg_style = (
                    f"background-image:url({_bg_url}),{d['card_gradient']};"
                    "background-size:cover,cover;background-position:center,center;"
                ) if _bg_url else f"background:{d['card_gradient']};"

                st.markdown(
                    f'<div class="dl-card {active_class}">'

                    # Image zone — photo + overlay + big icon
                    f'<div class="dl-card-img" style="{_bg_style}height:130px;position:relative;">'
                    # dark overlay for readability
                    f'<div style="position:absolute;inset:0;background:linear-gradient(to bottom,rgba(0,0,0,.15) 0%,rgba(0,0,0,.6) 100%);border-radius:0;"></div>'
                    # big disease icon centered
                    f'<div style="position:absolute;top:50%;left:50%;transform:translate(-50%,-60%);'
                    f'font-size:2.4rem;line-height:1;filter:drop-shadow(0 2px 8px rgba(0,0,0,.7));z-index:1;">'
                    f'{d["icon"]}</div>'
                    # severity badge top-right
                    f'<div class="dl-card-sev-badge {d["sev_class"]}" style="z-index:2;">{t("severity." + d["severity"])}</div>'
                    f'<div class="dl-card-critical-label" '
                    f'style="background:{sev_lbl_bg};color:{sev_lbl_color};z-index:2;position:relative;">'
                    f'{t("severity." + d["severity"]).capitalize()}</div>'
                    f'</div>'

                    # Card body
                    f'<div class="dl-card-body">'
                    f'<div class="dl-card-name">{d["name"]}</div>'
                    f'<div class="dl-sev-bar">{bar_html}</div>'
                    f'</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                if st.button(t("disease_lib.view_details"), key=f"sel_{d['key']}", use_container_width=True):
                    st.session_state["selected_disease"] = d["key"]
                    st.rerun()

# ── RIGHT: detail panel ───────────────────────────────────────────────────────
with detail_col:
    st.markdown(
        f'<div class="dl-sec-label">Disease Details &middot; {selected["name"]}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="dl-detail">'

        # Panel top bar
        f'<div class="dl-detail-top">'
        f'<div style="display:flex;align-items:center;justify-content:space-between;">'
        f'<span style="font-size:.6rem;font-weight:700;letter-spacing:2px;'
        f'text-transform:uppercase;color:#16a34a;">{t("disease_lib.symptoms")}</span>'
        f'<span style="background:{selected["sev_bg"]};color:{selected["sev_color"]};'
        f'border:1px solid {selected["sev_border"]};border-radius:999px;'
        f'padding:2px 10px;font-size:.6rem;font-weight:800;letter-spacing:.5px;">'
        f'{t("severity." + selected["severity"])}</span>'
        f'</div>'
        f'</div>'

        f'<div class="dl-detail-body">',
        unsafe_allow_html=True,
    )

    # Symptom section — small leaf image + bullet list
    sym_rows = "".join(
        f'<div class="dl-sym-item">'
        f'<span class="dl-sym-bullet" style="color:{selected["accent"]};">&#9670;</span>'
        f'<span class="dl-sym-text">{s}</span>'
        f'</div>'
        for s in selected["symptoms"]
    )
    st.markdown(
        f'<div class="dl-sym-wrap">'
        f'<div class="dl-sym-img" style="background:{selected["card_gradient"]};'
        f'display:flex;align-items:center;justify-content:center;font-size:2.4rem;">'
        f'{selected["icon"]}'
        f'</div>'
        f'<div class="dl-sym-list">{sym_rows}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Favourable conditions
    cond_html = "".join(
        f'<div class="dl-cond-item">'
        f'<div class="dl-cond-icon">{ico}</div>'
        f'<div class="dl-cond-lbl">{cond}</div>'
        f'</div>'
        for ico, cond in zip(selected["conditions_icon"], selected["conditions"])
    )
    st.markdown(
        '<div class="dl-cond-box">'
        f'<div style="font-size:.6rem;font-weight:700;letter-spacing:2px;'
        f'text-transform:uppercase;color:#16a34a;">{t("disease_lib.conditions")}</div>'
        f'<div class="dl-cond-items">{cond_html}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    # Recommended actions
    action_html = "".join(
        f'<div class="dl-action-card">'
        f'<div class="dl-action-icon">{ico}</div>'
        f'<div class="dl-action-lbl">{act}</div>'
        f'</div>'
        for ico, act in zip(selected["actions_icon"], selected["actions"])
    )
    st.markdown(
        '<div style="margin-top:4px;">'
        f'<div style="font-size:.6rem;font-weight:700;letter-spacing:2px;'
        f'text-transform:uppercase;color:#6b7280;margin-bottom:8px;">{t("disease_lib.actions")}</div>'
        f'<div class="dl-actions-grid">{action_html}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown('</div></div>', unsafe_allow_html=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown('<div style="height:36px;"></div>', unsafe_allow_html=True)
ui_footer()
