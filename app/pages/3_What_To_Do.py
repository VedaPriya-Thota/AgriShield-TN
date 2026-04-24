"""What To Do Now · Full illustrated action plan for diagnosed disease."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from _shared import ui_footer, inject_header, inject_sidebar_brand
from i18n import t

st.session_state["_cur_page"] = "action_plan"

# ── Check diagnosis data ──────────────────────────────────────────────────────
if "diag_insight" not in st.session_state:
    st.markdown(
        '<div style="text-align:center;padding:60px 20px;">'
        '<div style="font-size:3rem;margin-bottom:16px;">&#127807;</div>'
        '<div style="font-size:1.2rem;font-weight:800;color:#111827;margin-bottom:8px;">No Diagnosis Found</div>'
        '<div style="font-size:.85rem;color:#6b7280;margin-bottom:24px;">Please diagnose a leaf first to view your action plan.</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    if st.button("🤖 Go to Diagnose", use_container_width=False, key="goto_diag"):
        st.switch_page("pages/2_Analyze_Leaf.py")
    st.stop()

insight      = st.session_state["diag_insight"]
disease_name = st.session_state.get("diag_disease_name", "Unknown Disease")
sev          = st.session_state.get("diag_sev", "MODERATE")
pct          = st.session_state.get("diag_pct", 0.0)

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="wtdn-page-hero">'
    '<div class="wtdn-page-hero-content">'
    '<div class="wtdn-page-hero-title">WHAT TO DO NOW</div>'
    '<div class="wtdn-page-hero-sep">|</div>'
    '<div class="wtdn-page-hero-ta">என்ன செய்ய வேண்டும்</div>'
    '</div>'
    f'<div class="wtdn-page-hero-sub">&#127807; {disease_name} &middot; {pct:.0f}% confidence</div>'
    '</div>',
    unsafe_allow_html=True,
)

_bc1, _bc2 = st.columns([1, 6])
with _bc1:
    if st.button("← Diagnose", use_container_width=True, key="back_to_diag"):
        st.switch_page("pages/2_Analyze_Leaf.py")

# ── Action map ────────────────────────────────────────────────────────────────
_ACTION_MAP = [
    (["drain","flood","water","irrigat","standing water"],
     "&#128167;","wtdn-badge--today","TODAY","நீர் வடிகால்",
     "Improve Drainage","மேம்படுத்தப்பட்ட வடிகால்",
     "1559827260-dc66d52bef19","linear-gradient(135deg,#0c2a3a,#1e4d6b)"),
    (["crowd","spac","densit","plant distance","thin"],
     "&#127807;","wtdn-badge--week","THIS WEEK","பயிர் இடைவெளி",
     "Reduce Plant Crowding","பயிர் கூட்டத்தை குறைக்கவும்",
     "1574943320219-553eb213f72d","linear-gradient(135deg,#0c2a0c,#1e5a1e)"),
    (["wet","leaf","touch","moist","dew","humid"],
     "&#127811;","wtdn-badge--wet","WHEN WET","ஈர இலைகள்",
     "Handle Wet Leaves","ஈரமான இலைகளை கவனிக்கவும்",
     "1500382017468-9049fed747ef","linear-gradient(135deg,#0c1a3a,#1e3060)"),
    (["monitor","inspect","check","watch","survey","daily","spread"],
     "&#128269;","wtdn-badge--daily","DAILY","கண்காணி",
     "Monitor New Spread","புதிய பரவலை கண்காணிக்கவும்",
     "1622383563227-04401ab4e5ea","linear-gradient(135deg,#0c2a10,#1a5020)"),
    (["spray","fungicide","pesticide","chemic","insecticid","bactericid","apply"],
     "&#129514;","wtdn-badge--directed","AS DIRECTED","மருந்து தெளி",
     "Apply Treatment","சிகிச்சை பயன்படுத்தவும்",
     "1587131782738-de30ea91a542","linear-gradient(135deg,#1a1040,#2e1a70)"),
    (["remov","dispos","harvest","uproot","cut","destroy","eliminat"],
     "&#9889;","wtdn-badge--now","IMMEDIATELY","உடனே அகற்று",
     "Remove Affected Plants","பாதிக்கப்பட்ட பயிர்களை அகற்றவும்",
     "1536054009244-c43bb5f1c1ac","linear-gradient(135deg,#3a0c0c,#6b1e1e)"),
]

def _classify_action_full(text: str):
    lower = text.lower()
    for kws, icon, badge_cls, badge_lbl, ta_short, en_title, ta_title, uns_id, fallback in _ACTION_MAP:
        if any(k in lower for k in kws):
            return icon, badge_cls, badge_lbl, ta_short, en_title, ta_title, uns_id, fallback
    return ("&#127806;","wtdn-badge--daily","DAILY","கவனமாக இரு",
            "Stay Vigilant","கவனமாக இருங்கள்",
            "1500382017468-9049fed747ef","linear-gradient(135deg,#062010,#103820)")

# ── Main layout ───────────────────────────────────────────────────────────────
main_col, side_col = st.columns([7, 3], gap="large")

with main_col:
    st.markdown(
        '<div style="font-size:.7rem;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;'
        'color:#dc2626;margin-bottom:14px;">&#9889; WHAT TO DO NOW</div>',
        unsafe_allow_html=True,
    )

    # Build large illustrated action cards
    cards_html = ""
    for action in insight.immediate_actions:
        icon, badge_cls, badge_lbl, ta_short, en_title, ta_title, uns_id, fallback = _classify_action_full(action)
        bg_url = f"https://images.unsplash.com/photo-{uns_id}?w=500&q=80&auto=format&fit=crop"
        cards_html += (
            f'<div class="wtdn-action-card-lg">'
            f'<div class="wtdn-action-card-img" style="background-image:url({bg_url}),{fallback};">'
            f'<div class="wtdn-badge {badge_cls}">{badge_lbl}</div>'
            f'<div class="wtdn-action-card-icon-lg">{icon}</div>'
            f'</div>'
            f'<div class="wtdn-action-card-body">'
            f'<div class="wtdn-action-card-en">{en_title.upper()}</div>'
            f'<div class="wtdn-action-card-ta">{ta_title}</div>'
            f'</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="wtdn-cards-scroll">{cards_html}</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div style="font-size:.7rem;color:#9ca3af;margin-top:10px;">'
        f'{t("diagnose.consult_warning")}'
        f'</div>',
        unsafe_allow_html=True,
    )

with side_col:
    # Expert Advisory sidebar
    _SEV_CAUSE_ICON = {
        "CRITICAL": "&#128308;", "HIGH": "&#9888;&#65039;",
        "MODERATE": "&#127746;", "LOW": "&#128994;", "NONE": "&#9989;",
    }
    _cause_icon = _SEV_CAUSE_ICON.get(sev, "&#9888;&#65039;")
    _cause_sentences = insight.cause.split(". ")
    _cause_short = ". ".join(_cause_sentences[:2]).strip().rstrip(".") + "."

    # Pill map
    _PILL_MAP = [
        (["nitrogen","npk","fertil","nutrient","potassium","phosphorus"],
         "&#127807;", "Use Balanced Fertilizer", "நடர்ஜன்"),
        (["seed","variety","resistant","certified"],
         "&#127807;", "Disease-Free Seeds", "தேர்ந்த விதை"),
        (["drain","water","irrigat"],
         "&#128167;", "Improve Drainage", "நீர் வடிகால்"),
        (["fungicide","spray","chemical","pesticide","bactericide"],
         "&#129514;", "Spray Treatment", "மருந்து தெளி"),
        (["monitor","inspect","watch","survey"],
         "&#128269;", "Monitor Daily", "கண்காணி"),
        (["remov","dispos","uproot","destroy"],
         "&#9889;", "Remove Affected", "பாதிப்பை நீக்கு"),
    ]
    _pill_text = (insight.prevention + " " + insight.action).lower()
    _pills_html = ""
    for _kws, _p_icon, _p_en, _p_ta in _PILL_MAP:
        if any(k in _pill_text for k in _kws):
            _pills_html += (
                f'<div class="wtdn-adv-pill">'
                f'<div class="wtdn-adv-pill-icon">{_p_icon}</div>'
                f'<div><div class="wtdn-adv-pill-en">{_p_en}</div>'
                f'<div class="wtdn-adv-pill-ta">| {_p_ta}</div></div>'
                f'</div>'
            )
        if _pills_html.count("wtdn-adv-pill") >= 3:
            break

    st.markdown(
        '<div class="wtdn-adv-sidebar">'
        '<div class="wtdn-adv-sidebar-hd">EXPERT ADVISORY</div>'
        f'<div class="wtdn-why-banner" style="margin-bottom:14px;">'
        f'<div class="wtdn-why-icon">{_cause_icon}</div>'
        f'<div style="flex:1;">'
        f'<div class="wtdn-why-title">WHY IT HAPPENED</div>'
        f'<div class="wtdn-why-text">{_cause_short}</div>'
        f'<div class="wtdn-why-ta">Act now to protect your crop · உங்கள் பயிரை பாதுகாக்க இப்போதே நடவடிக்கை எடுங்கள்.</div>'
        f'</div></div>'
        f'<div class="wtdn-adv-pills-hd">Treatment &amp; Prevention Guidance</div>'
        f'<div class="wtdn-adv-pills-wrap">{_pills_html}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)
ui_footer()
