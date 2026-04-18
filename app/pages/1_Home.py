"""Home · AgriShield-TN — premium landing page with farmer animations."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from _shared import ui_footer

st.session_state["_cur_page"] = "home"

# Full-screen landing — hide sidebar, strip ALL container padding/gaps
st.markdown(
    '<style>'
    '[data-testid="stSidebar"]{display:none !important;}'
    '[data-testid="stSidebarCollapsedControl"]{display:none !important;}'
    '[data-testid="collapsedControl"]{display:none !important;}'
    '[data-testid="stHeader"]{display:none !important;}'
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
    '<span class="hero-badge-text">AI&#8209;Powered &nbsp;&bull;&nbsp; Tamil Nadu Agri&#8209;AI</span>'
    '</div>'

    '<div class="hero-title">'
    '<span class="ht-agri">Agri</span>'
    '<span class="ht-shield">&#128737;&#65039;</span>'
    '<span class="ht-ield">eld</span>'
    '<span class="ht-tn">&#8209;TN</span>'
    '</div>'

    '<p class="hero-subtitle">AI Crop Health Assistant for Tamil Nadu Farmers</p>'

    '<div class="hero-flow">'
    '<div class="hero-flow-step">'
    '<div class="hero-flow-icon">&#128247;</div>'
    '<div class="hero-flow-label">Detect</div>'
    '</div>'
    '<div class="hero-flow-arr">&#8594;</div>'
    '<div class="hero-flow-step">'
    '<div class="hero-flow-icon">&#129504;</div>'
    '<div class="hero-flow-label">Analyze</div>'
    '</div>'
    '<div class="hero-flow-arr">&#8594;</div>'
    '<div class="hero-flow-step">'
    '<div class="hero-flow-icon">&#128737;&#65039;</div>'
    '<div class="hero-flow-label">Act</div>'
    '</div>'
    '</div>'

    '<div class="hero-feats">'
    '<div class="hero-feat hero-feat--g"><span class="hero-feat__icon">&#127806;</span><span class="hero-feat__text">10 Disease Classes</span></div>'
    '<div class="hero-feat hero-feat--p"><span class="hero-feat__icon">&#129504;</span><span class="hero-feat__text">ResNet&#8209;18 CNN</span></div>'
    '<div class="hero-feat hero-feat--h"><span class="hero-feat__icon">&#128293;</span><span class="hero-feat__text">Grad&#8209;CAM XAI</span></div>'
    '<div class="hero-feat hero-feat--b"><span class="hero-feat__icon">&#127750;</span><span class="hero-feat__text">Live Weather Risk</span></div>'
    '<div class="hero-feat hero-feat--d"><span class="hero-feat__icon">&#129302;</span><span class="hero-feat__text">Groq AI Advisory</span></div>'
    '<div class="hero-feat hero-feat--a"><span class="hero-feat__icon">&#9889;</span><span class="hero-feat__text">&lt;2s Diagnosis</span></div>'
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
    '<div class="sec-hd__eye">Core Capabilities</div>'
    '<h2 class="sec-hd__title">Everything a farmer needs<br>to protect their crop</h2>'
    '<p class="sec-hd__sub">From instant AI diagnosis to live weather risk &mdash; one tool, every answer.</p>'
    '</div>',
    unsafe_allow_html=True,
)

_CAPS = [
    ("cap-green",  "&#127806;", "Disease Detection",
     "Classifies 10 paddy disease classes using a fine-tuned ResNet-18 CNN with severity grading from NONE to CRITICAL.",
     "ResNet-18 &middot; 10 classes"),
    ("cap-red",    "&#9889;",   "Immediate Actions",
     "Priority-ordered action checklist specific to each disease &mdash; what to do today, this week, and to prevent recurrence.",
     "Disease-specific &middot; 3&ndash;5 steps"),
    ("cap-blue",   "&#127750;", "Weather Spread Risk",
     "Live temperature, humidity and 3-day rain forecast from OpenMeteo mapped against disease spread conditions for 38 TN districts.",
     "OpenMeteo &middot; 38 districts"),
    ("cap-teal",   "&#129302;", "Groq AI Advisory",
     "Structured expert guidance from Groq&rsquo;s Llama 3 &mdash; disease summary, cause, treatment, and prevention in plain farmer language.",
     "Llama 3 &middot; &lt;3s response"),
    ("cap-purple", "&#128293;", "Grad-CAM XAI",
     "Pixel-level heatmap showing exactly which leaf regions drove the model&rsquo;s prediction &mdash; visual proof any farmer can verify.",
     "Grad-CAM &middot; 224&times;224"),
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
        '<div class="bff-eyebrow">Built for Real Farmers</div>'
        '<h2 class="bff-title">Every farmer deserves<br>expert crop guidance</h2>'
        '<p class="bff-sub">AgriShield-TN brings agricultural science directly to the field &mdash; '
        'in seconds, on any smartphone, completely free.</p>'
        '</div>',
        unsafe_allow_html=True,
    )

    _BENEFITS = [
        ("&#127806;", "#f0fdf4", "#bbf7d0",
         "Small &amp; Marginal Farmers",
         "Get instant disease identification without waiting days for an agronomist visit. Know exactly what to spray, and when."),
        ("&#128652;", "#eff6ff", "#bfdbfe",
         "Agricultural Field Officers",
         "Scale your expertise across thousands of farms simultaneously. Use AI as your second opinion on the ground."),
        ("&#127891;", "#faf5ff", "#ddd6fe",
         "Agri Students &amp; Researchers",
         "Study real disease patterns with Grad-CAM visual explanations &mdash; see exactly which leaf features the AI uses."),
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
    '<div class="hiw-eyebrow">How It Works</div>'
    '<h2 class="hiw-title">From photo to action plan in 4 steps</h2>'
    '</div>'
    '<div class="hiw-steps">'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#128247;</div>'
    '<div class="hiw-step__num">Step 01</div>'
    '<div class="hiw-step__name">Upload Photo</div>'
    '<div class="hiw-step__desc">Take a close-up photo of the affected paddy leaf with any smartphone and upload it.</div>'
    '</div>'
    '<div class="hiw-arrow">&#8594;</div>'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#129504;</div>'
    '<div class="hiw-step__num">Step 02</div>'
    '<div class="hiw-step__name">AI Detection</div>'
    '<div class="hiw-step__desc">ResNet-18 CNN classifies the disease from 10 classes with confidence score and severity grade.</div>'
    '</div>'
    '<div class="hiw-arrow">&#8594;</div>'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#127750;</div>'
    '<div class="hiw-step__num">Step 03</div>'
    '<div class="hiw-step__name">Risk Analysis</div>'
    '<div class="hiw-step__desc">Live weather data from your district is evaluated against disease spread conditions.</div>'
    '</div>'
    '<div class="hiw-arrow">&#8594;</div>'

    '<div class="hiw-step">'
    '<div class="hiw-step__orb">&#9889;</div>'
    '<div class="hiw-step__num">Step 04</div>'
    '<div class="hiw-step__name">Action Plan</div>'
    '<div class="hiw-step__desc">Receive an immediate checklist and full Groq AI advisory in plain farmer language.</div>'
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
    '<div class="impact-label">Annual crop loss in Tamil Nadu</div>'
    '</div>'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#128100;</span>'
    '<div class="impact-value">70%</div>'
    '<div class="impact-label">Farmers are small or marginal holders</div>'
    '</div>'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#9889;</span>'
    '<div class="impact-value">&lt; 2s</div>'
    '<div class="impact-label">Full AI diagnosis time from upload</div>'
    '</div>'

    '<div class="impact-cell">'
    '<span class="impact-icon">&#128205;</span>'
    '<div class="impact-value">38</div>'
    '<div class="impact-label">Tamil Nadu districts with live weather</div>'
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
    '<div class="sec-hd__eye">Disease Intelligence</div>'
    '<h2 class="sec-hd__title">Know the enemy before it strikes</h2>'
    '<p class="sec-hd__sub">AgriShield-TN detects 10 major paddy diseases. Here are 3 of the most common threats in Tamil Nadu.</p>'
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
            f'<div class="dprev-link">&#128218; View full details in Field Guide &#8594;</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

_, see_all_col, _ = st.columns([3, 2, 3])
with see_all_col:
    if st.button("📖  Open Full Field Guide  →", use_container_width=True, key="dprev_cta"):
        st.switch_page("pages/6_Disease_Library.py")

st.markdown('<div class="spacer-lg"></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  7. BOTTOM CTA  (dark premium with animated farmer)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    '<div class="btm-cta-v2">'
    '<span class="btm-cta-v2__farmer">&#129489;&#8205;&#127806;</span>'
    '<h2 class="btm-cta-v2__title">Ready to protect<br><span>your harvest?</span></h2>'
    '<p class="btm-cta-v2__sub">Free &nbsp;&middot;&nbsp; Instant &nbsp;&middot;&nbsp; No sign-up required</p>'
    '</div>',
    unsafe_allow_html=True,
)

_, cta2_col, _ = st.columns([3, 2, 3])
with cta2_col:
    if st.button("🩺  Start Diagnosis  →", use_container_width=True, key="cta_bottom"):
        st.switch_page("pages/2_Analyze_Leaf.py")

st.markdown(
    '<div class="btm-cta-v2__perks">'
    '<span class="btm-cta-v2__perk">No account needed</span>'
    '<span style="color:rgba(255,255,255,.12);">&middot;</span>'
    '<span class="btm-cta-v2__perk">Works on any device</span>'
    '<span style="color:rgba(255,255,255,.12);">&middot;</span>'
    '<span class="btm-cta-v2__perk">Groq AI powered</span>'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
ui_footer()
