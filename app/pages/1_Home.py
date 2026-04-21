"""Home · AgriShield-TN — premium landing page with farmer animations."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from _shared import ui_footer, inject_sidebar_brand, inject_header
from i18n import t

st.session_state["_cur_page"] = "home"

# Full-screen landing — hide sidebar, strip ALL container padding/gaps
st.markdown(
    '<style>'
    '[data-testid="stSidebar"]{display:none !important;}'
    '[data-testid="stSidebarCollapsedControl"]{display:flex !important;}'
    '[data-testid="collapsedControl"]{display:flex !important;}'
    '[data-testid="stHeader"]{display:flex !important;height:0 !important;}' # Restore but keep tiny
    '[data-testid="stToolbar"]{display:none !important;}'
    '[data-testid="stDecoration"]{display:none !important;}'
    '[data-testid="stAppViewContainer"]{padding:0 !important;margin:0 !important;}'
    '[data-testid="stMain"]{padding:0 !important;margin:0 !important;}'
    '[data-testid="stMainBlockContainer"]{padding:0 !important;max-width:100% !important;}'
    '[data-testid="block-container"]{padding:0 !important;max-width:100% !important;}'
    '[data-testid="stVerticalBlock"]{gap:0 !important;padding:0 !important;}'
    '[data-testid="stVerticalBlockBorderWrapper"]{padding:0 !important;}'
    '.hero{margin:0 !important;height:100vh !important;}'
    '</style>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────────────────
#  1. CINEMATIC HERO  (photo bg + birds + rice field + walking farmers)
# ─────────────────────────────────────────────────────────────────────────────
_STALKS = ''.join(['<span class="hstalk">&#127806;</span>' for _ in range(56)])

st.markdown(
    '<div class="hero">'
    '<div class="hero-bg"></div>'
    '<div class="hero-overlay"></div>'
    '<div class="hero-radial"></div>'
    '<div class="hero-vignette"></div>'
    '<div class="hero-orb hero-orb-1"></div>'
    '<div class="hero-orb hero-orb-2"></div>'
    '<div class="hero-orb hero-orb-3"></div>'

    '<div class="hero-birds">'
    '<div class="hbird hbird-1">&#128038;</div>'
    '<div class="hbird hbird-2">&#128038;</div>'
    '<div class="hbird hbird-3">&#128038;</div>'
    '</div>'

    '<div class="hero-inner">'

    '<div class="hero-badge">'
    '<span class="hero-badge-dot"></span>'
    f'<span class="hero-badge-text">{t("home.badge")}</span>'
    '</div>'

    '<div class="hero-title">'
    '<span class="ht-agri">Agri</span>'
    '<span class="ht-shield">&#128737;&#65039;</span>'
    '<span class="ht-ield">eld</span>'
    '<span class="ht-tn">&#8209;TN</span>'
    '</div>'

    f'<p class="hero-subtitle">{t("home.subtitle")}</p>'

    '<div class="hero-flow">'
    '<div class="hero-flow-step">'
    '<div class="hero-flow-icon">&#128247;</div>'
    f'<div class="hero-flow-label">{t("home.detect")}</div>'
    '</div>'
    '<div class="hero-flow-arr">&#8594;</div>'
    '<div class="hero-flow-step">'
    '<div class="hero-flow-icon">&#129504;</div>'
    f'<div class="hero-flow-label">{t("home.analyze")}</div>'
    '</div>'
    '<div class="hero-flow-arr">&#8594;</div>'
    '<div class="hero-flow-step">'
    '<div class="hero-flow-icon">&#128737;&#65039;</div>'
    f'<div class="hero-flow-label">{t("home.act")}</div>'
    '</div>'
    '</div>'

    '<div class="hero-feats">'
    f'<div class="hero-feat hero-feat--g"><span class="hero-feat__icon">&#127806;</span><span class="hero-feat__text">10 {t("diagnose.classes_val")}</span></div>'
    f'<div class="hero-feat hero-feat--p"><span class="hero-feat__icon">&#129504;</span><span class="hero-feat__text">{t("diagnose.model_name")}</span></div>'
    f'<div class="hero-feat hero-feat--h"><span class="hero-feat__icon">&#128293;</span><span class="hero-feat__text">{t("diagnose.gradcam_title").replace("🖼️ ", "")}</span></div>'
    f'<div class="hero-feat hero-feat--b"><span class="hero-feat__icon">&#127750;</span><span class="hero-feat__text">{t("diagnose.weather_title").replace("🌦 ", "")}</span></div>'
    f'<div class="hero-feat hero-feat--d"><span class="hero-feat__icon">&#129302;</span><span class="hero-feat__text">{t("diagnose.source_groq")} {t("diagnose.expert_advisory").lower()}</span></div>'
    f'<div class="hero-feat hero-feat--a"><span class="hero-feat__icon">&#9889;</span><span class="hero-feat__text">{t("common.instant")} {t("diagnose.detected_disease").lower()}</span></div>'
    '</div>'

    '</div>'  # close hero-inner — CTA buttons rendered below via st.button

    f'<div class="hero-field-row">{_STALKS}</div>'

    '<div class="hero-farmers">'
    '<div class="hf hf-1">&#129489;&#8205;&#127806;</div>'
    '<div class="hf hf-2">&#128104;&#8205;&#127806;</div>'
    '<div class="hf hf-3">&#128105;&#8205;&#127806;</div>'
    '<div class="hf hf-4">&#129489;&#8205;&#127806;</div>'
    '</div>'

    '<div class="hero-fade"></div>'
    '</div>',
    unsafe_allow_html=True,
)


# ─────────────────────────────────────────────────────────────────────────────
#  2. CAPABILITIES
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sec-hd">'
    f'<div class="sec-hd__eye">{t("home.capabilities_eye")}</div>'
    f'<h2 class="sec-hd__title">{t("home.capabilities_h2").replace(chr(10), "<br>")}</h2>'
    f'<p class="sec-hd__sub">{t("home.capabilities_sub")}</p>'
    '</div>',
    unsafe_allow_html=True,
)

_CAPS = [
    ("cap-green",  "&#127806;", t("home.cap_disease"),      t("home.cap_disease_desc"),  t("home.cap_disease_tag")),
    ("cap-red",    "&#9889;",   t("home.cap_actions"),      t("home.cap_actions_desc"),  t("home.cap_actions_tag")),
    ("cap-blue",   "&#127750;", t("home.cap_weather"),      t("home.cap_weather_desc"),  t("home.cap_weather_tag")),
    ("cap-teal",   "&#129302;", t("home.cap_groq"),         t("home.cap_groq_desc"),     t("home.cap_groq_tag")),
    ("cap-purple", "&#128293;", t("home.cap_gradcam"),      t("home.cap_gradcam_desc"),  t("home.cap_gradcam_tag")),
]

cols = st.columns(5, gap="small")
for col, (color, icon, title, desc, tag) in zip(cols, _CAPS):
    with col:
        st.markdown(
            f'<div class="cap-card {color}">'
            f'<div class="cap-card__icon">{icon}</div>'
            f'<div class="cap-card__title">{title}</div>'
            f'<p class="cap-card__desc">{desc}</p>'
            f'<div class="cap-card__tag">{tag}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  3. BUILT FOR TAMIL NADU FARMERS  (illustration + benefits)
# ─────────────────────────────────────────────────────────────────────────────
_STARS = ''.join(['<span class="fp-star">&#10022;</span>' for _ in range(24)])
_FP_STALKS = ''.join(['<span class="fp-stalk">&#127806;</span>' for _ in range(22)])

illus_col, text_col = st.columns([5, 6], gap="large")

with illus_col:
    st.markdown(
        '<div class="fp-wrap">'
        f'<div class="fp-stars">{_STARS}</div>'
        '<div class="fp-moon">&#127769;</div>'
        '<div class="fp-clouds">'
        '<span class="fp-cloud">&#9729;&#65039;</span>'
        '<span class="fp-cloud">&#9729;&#65039;</span>'
        '<span class="fp-cloud">&#9729;&#65039;</span>'
        '</div>'
        '<div class="fp-farmer-fig">&#129489;&#8205;&#127806;</div>'
        f'<div class="fp-field-row">{_FP_STALKS}</div>'
        '</div>',
        unsafe_allow_html=True,
    )

with text_col:
    st.markdown(
        '<div style="padding:28px 0 0;">'
        f'<div class="bff-eyebrow">{t("home.built_eyebrow")}</div>'
        f'<h2 class="bff-title">{t("home.built_h2").replace(chr(10), "<br>")}</h2>'
        f'<p class="bff-sub">{t("home.built_sub")}</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    _BENEFITS = [
        ("&#127806;", "#f0fdf4", "#bbf7d0", t("home.ben_small_title"),  t("home.ben_small_desc")),
        ("&#128652;", "#eff6ff", "#bfdbfe", t("home.ben_officer_title"), t("home.ben_officer_desc")),
        ("&#127891;", "#faf5ff", "#ddd6fe", t("home.ben_student_title"), t("home.ben_student_desc")),
    ]

    for icon, bg, border, title, desc in _BENEFITS:
        st.markdown(
            f'<div class="bff-benefit">'
            f'<div class="bff-benefit-icon" style="background:{bg};border:1px solid {border};">{icon}</div>'
            f'<div>'
            f'<div class="bff-benefit-title">{title}</div>'
            f'<p class="bff-benefit-desc">{desc}</p>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  4. HOW IT WORKS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="hiw">'
    '<div class="hiw-heading">'
    f'<div class="hiw-eyebrow">{t("home.hiw_eyebrow")}</div>'
    f'<h2 class="hiw-title">{t("home.hiw_h2")}</h2>'
    '</div>'
    '<div class="hiw-steps">'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#128247;</div>'
    f'<div class="hiw-step__num">{t("common.step")} 01</div>'
    f'<div class="hiw-step__name">{t("home.hiw_s1_name")}</div>'
    f'<div class="hiw-step__desc">{t("home.hiw_s1_desc")}</div>'
    '</div>'
    '<div class="hiw-arrow">&#8594;</div>'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#129504;</div>'
    f'<div class="hiw-step__num">{t("common.step")} 02</div>'
    f'<div class="hiw-step__name">{t("home.hiw_s2_name")}</div>'
    f'<div class="hiw-step__desc">{t("home.hiw_s2_desc")}</div>'
    '</div>'
    '<div class="hiw-arrow">&#8594;</div>'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#127750;</div>'
    f'<div class="hiw-step__num">{t("common.step")} 03</div>'
    f'<div class="hiw-step__name">{t("home.hiw_s3_name")}</div>'
    f'<div class="hiw-step__desc">{t("home.hiw_s3_desc")}</div>'
    '</div>'
    '<div class="hiw-arrow">&#8594;</div>'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#9889;</div>'
    f'<div class="hiw-step__num">{t("common.step")} 04</div>'
    f'<div class="hiw-step__name">{t("home.hiw_s4_name")}</div>'
    f'<div class="hiw-step__desc">{t("home.hiw_s4_desc")}</div>'
    '</div>'

    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  5. IMPACT STATS  (dark premium strip)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="impact-strip">'
    '<div class="impact-grid">'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#8377;</span>'
    '<div class="impact-value">4,500Cr</div>'
    f'<div class="impact-label">{t("home.impact_loss")}</div>'
    '</div>'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#128100;</span>'
    '<div class="impact-value">70%</div>'
    f'<div class="impact-label">{t("home.impact_farmers")}</div>'
    '</div>'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#9889;</span>'
    '<div class="impact-value">&lt; 2s</div>'
    f'<div class="impact-label">{t("home.impact_time")}</div>'
    '</div>'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#128205;</span>'
    '<div class="impact-value">38</div>'
    f'<div class="impact-label">{t("home.impact_districts")}</div>'
    '</div>'

    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  6. DISEASE PREVIEW TEASER
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="sec-hd">'
    f'<div class="sec-hd__eye">{t("home.disease_eye")}</div>'
    f'<h2 class="sec-hd__title">{t("home.disease_h2")}</h2>'
    f'<p class="sec-hd__sub">{t("home.disease_sub")}</p>'
    '</div>',
    unsafe_allow_html=True,
)

_DISEASES = [
    ("dprev-card--blast", "&#127806;", "Rice Blast",
     "dprev-sev--critical", "&#128308; CRITICAL",
     "Caused by Magnaporthe oryzae fungus, this is the most destructive paddy disease worldwide. Affects leaves, neck, and panicle at any growth stage.",
     "Airborne spores spread rapidly in cool, humid conditions with temperatures of 25&ndash;28&deg;C."),
    ("dprev-card--blight", "&#129399;", "Brown Plant Hopper",
     "dprev-sev--high", "&#128992; HIGH",
     "Massive pest infestations that suck plant sap causing &lsquo;hopperburn&rsquo; &mdash; circular patches of dried, yellow-brown plants in the field.",
     "Dense crop canopy and high nitrogen fertilisation create favourable breeding conditions."),
    ("dprev-card--spot", "&#127807;", "Bacterial Leaf Blight",
     "dprev-sev--moderate", "&#129002; MODERATE",
     "Water-soaked to yellow stripes along leaf margins that turn yellow-white and dry out. Can cause 20&ndash;30% yield loss in severe cases.",
     "Spreads through water, wind, and contaminated equipment. High humidity and rain increase risk."),
]

dcols = st.columns(3, gap="large")
for col, (card_cls, icon, title, sev_cls, sev_lbl, desc, cond) in zip(dcols, _DISEASES):
    with col:
        st.markdown(
            f'<div class="dprev-card {card_cls}">'
            f'<div class="dprev-icon">{icon}</div>'
            f'<div class="dprev-title">{title}</div>'
            f'<div class="dprev-sev {sev_cls}">{sev_lbl}</div>'
            f'<p class="dprev-desc">{desc}</p>'
            f'<div style="background:#f9fafb;border:1px solid #f3f4f6;border-radius:8px;padding:9px 12px;'
            f'font-size:.76rem;color:#6b7280;line-height:1.5;margin-bottom:16px;">'
            f'&#127750; {cond}'
            f'</div>'
            f'<div class="dprev-link">{t("home.view_field_link")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

_, see_all_col, _ = st.columns([3, 2, 3])
with see_all_col:
    if st.button(t("home.see_field_guide"), use_container_width=True, key="dprev_cta"):
        st.switch_page("pages/6_Disease_Library.py")

st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  7. BOTTOM CTA  (dark premium with animated farmer)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="btm-cta-v2">'
    '<span class="btm-cta-v2__farmer">&#129489;&#8205;&#127806;</span>'
    f'<h2 class="btm-cta-v2__title">{t("home.cta_title").replace(chr(10), "<br><span>") + "</span>"}</h2>'
    f'<p class="btm-cta-v2__sub">{t("home.cta_sub")}</p>'
    '</div>',
    unsafe_allow_html=True,
)

_, cta2_col, _ = st.columns([3, 2, 3])
with cta2_col:
    if st.button(t("home.cta_button"), use_container_width=True, key="cta_bottom"):
        st.switch_page("pages/2_Analyze_Leaf.py")

st.markdown(
    '<div class="btm-cta-v2__perks">'
    f'<span class="btm-cta-v2__perk">{t("home.perk_no_account")}</span>'
    '<span style="color:rgba(255,255,255,.12);">&middot;</span>'
    f'<span class="btm-cta-v2__perk">{t("home.perk_any_device")}</span>'
    '<span style="color:rgba(255,255,255,.12);">&middot;</span>'
    f'<span class="btm-cta-v2__perk">{t("home.perk_groq")}</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
ui_footer()
