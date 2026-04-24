"""About · AgriShield-TN — How it works, impact, and future scope."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from _shared import ui_divider, ui_footer, inject_header, inject_sidebar_brand

st.session_state["_cur_page"] = "home"

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ds-ph">'
    '<h1 class="ds-ph-title">About AgriShield-TN</h1>'
    '<p class="ds-ph-sub">'
    'How the AI pipeline works, the problem it solves for Tamil Nadu farmers, '
    'and what we\'re building next.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

ui_divider()

# ─────────────────────────────────────────────────────────────────────────────
#  HOW IT WORKS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl">How it works</p>', unsafe_allow_html=True)

steps = [
    {
        "number": "1", "icon": "📸", "title": "Upload a Leaf Photo",
        "body": "Take a photo of a paddy leaf with any smartphone. Upload it directly — JPG or PNG, no special equipment needed.",
        "accent": "#16a34a", "bg": "#f0fdf4", "border": "#bbf7d0",
        "chips": ["Any smartphone", "JPG / PNG", "Under 5 seconds"],
    },
    {
        "number": "2", "icon": "🧠", "title": "AI Disease Detection",
        "body": "A ResNet-18 CNN fine-tuned on 10,000+ paddy images classifies the disease from 10 possible classes and produces a confidence score.",
        "accent": "#2563eb", "bg": "#eff6ff", "border": "#dbeafe",
        "chips": ["ResNet-18", "10 disease classes", "~10k training images"],
    },
    {
        "number": "3", "icon": "🔥", "title": "Grad-CAM Explainability",
        "body": "Gradient-weighted Class Activation Mapping highlights exactly which leaf regions drove the model's decision — so you can see what the AI saw.",
        "accent": "#0d9488", "bg": "#f0fdfa", "border": "#99f6e4",
        "chips": ["Grad-CAM XAI", "Visual proof", "224×224 heatmap"],
    },
    {
        "number": "4", "icon": "🌦️", "title": "Weather Risk Assessment",
        "body": "Live weather data (temperature, humidity, rainfall) from OpenMeteo is mapped against disease-specific spread conditions for your district.",
        "accent": "#7c3aed", "bg": "#faf5ff", "border": "#ede9fe",
        "chips": ["OpenMeteo API", "38 TN districts", "3-day forecast"],
    },
    {
        "number": "5", "icon": "🤖", "title": "Groq AI Advisory",
        "body": "Groq's Llama 3 model generates a structured expert advisory — disease summary, cause, treatment guidance, and prevention strategy — in plain language.",
        "accent": "#d97706", "bg": "#fffbeb", "border": "#fde68a",
        "chips": ["Groq Llama 3", "Farmer-friendly language", "< 3s response"],
    },
]

_, card_col, _ = st.columns([0.5, 7, 0.5])
with card_col:
    for i, s in enumerate(steps):
        chip_html = "".join(
            f'<span style="font-size:0.72rem;font-weight:600;'
            f'background:{s["bg"]};border:1px solid {s["border"]};color:{s["accent"]};'
            f'border-radius:999px;padding:3px 11px;white-space:nowrap;">{c}</span>'
            for c in s["chips"]
        )
        st.markdown(
            f'<div class="ds-card" style="margin-bottom:12px;">'
            f'<div class="ds-card-strip" style="background:{s["accent"]};"></div>'
            f'<div style="padding:18px 20px;display:flex;gap:16px;align-items:flex-start;">'

            # Step number circle
            f'<div style="width:40px;height:40px;border-radius:50%;flex-shrink:0;'
            f'background:{s["bg"]};border:2px solid {s["border"]};'
            f'display:flex;align-items:center;justify-content:center;'
            f'font-size:1.2rem;">{s["icon"]}</div>'

            f'<div style="flex:1;">'
            f'<div style="font-size:0.65rem;font-weight:700;letter-spacing:1px;'
            f'text-transform:uppercase;color:{s["accent"]};margin-bottom:3px;">Step {s["number"]}</div>'
            f'<div style="font-size:0.97rem;font-weight:800;color:#111827;margin-bottom:6px;">{s["title"]}</div>'
            f'<p style="font-size:0.855rem;color:#64748B;line-height:1.65;margin:0 0 12px;">{s["body"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:6px;">{chip_html}</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        if i < len(steps) - 1:
            st.markdown(
                f'<div style="display:flex;justify-content:center;padding:2px 0 2px 38px;">'
                f'<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">'
                f'<div style="width:1.5px;height:14px;background:#e5e7eb;"></div>'
                f'<div style="width:0;height:0;border-left:5px solid transparent;'
                f'border-right:5px solid transparent;border-top:7px solid #e5e7eb;"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

ui_divider()

# ─────────────────────────────────────────────────────────────────────────────
#  IMPACT
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl ds-lbl--center">Why this matters</p>', unsafe_allow_html=True)

st.markdown(
    '<div style="max-width:620px;margin:0 auto;text-align:center;padding:8px 0 32px;">'
    '<h2 style="font-size:clamp(1.4rem,2.5vw,1.9rem);font-weight:800;color:#111827;'
    'letter-spacing:-.5px;margin:0 0 14px;">Tamil Nadu loses ₹4,500 crore<br>'
    'every year to crop disease</h2>'
    '<p style="font-size:0.9rem;color:#64748B;line-height:1.7;margin:0;">'
    'Most small and marginal farmers in Tamil Nadu cannot afford timely expert diagnosis. '
    'By the time a disease is identified, it has often spread to neighbouring crops. '
    'AgriShield-TN puts an AI agronomist in every farmer\'s pocket — free, instant, '
    'and available in the field with a smartphone.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

impact_stats = [
    ("₹4,500 Cr", "Annual crop loss in Tamil Nadu to disease", "#dc2626", "#fef2f2", "#fecaca"),
    ("70%",        "Of TN farmers are small/marginal holders",  "#d97706", "#fffbeb", "#fde68a"),
    ("< 2s",       "Time to get a full AI diagnosis",           "#16a34a", "#f0fdf4", "#bbf7d0"),
    ("10",         "Paddy disease classes detected",            "#2563eb", "#eff6ff", "#dbeafe"),
]

i_cols = st.columns(4, gap="large")
for col, (val, lbl, accent, bg, border) in zip(i_cols, impact_stats):
    with col:
        st.markdown(
            f'<div class="ds-premium-card" style="text-align:center;padding:24px 16px;">'
            f'<div style="height:3px;background:{accent};margin:-24px -16px 20px;"></div>'
            f'<div style="font-size:2rem;font-weight:900;color:{accent};'
            f'letter-spacing:-1.5px;line-height:1;">{val}</div>'
            f'<div style="font-size:0.78rem;color:#6b7280;margin-top:8px;line-height:1.5;">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

ui_divider()

# ─────────────────────────────────────────────────────────────────────────────
#  AI PIPELINE AT A GLANCE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl ds-lbl--center">Technical stack</p>', unsafe_allow_html=True)

tech_items = [
    ("🧠", "ResNet-18",    "CNN backbone fine-tuned on Paddy Doctor dataset",    "#2563eb", "#eff6ff", "#dbeafe"),
    ("🔥", "Grad-CAM",     "Visual explainability via class activation mapping",  "#0d9488", "#f0fdfa", "#99f6e4"),
    ("🤖", "Groq Llama 3", "LLM-powered expert advisory generation",             "#7c3aed", "#faf5ff", "#ede9fe"),
    ("🌦️", "OpenMeteo",   "Free weather API for real-time spread risk",          "#16a34a", "#f0fdf4", "#bbf7d0"),
    ("🧬", "Metadata",     "Variety + age fused into prediction head",           "#d97706", "#fffbeb", "#fde68a"),
    ("⚡", "Streamlit",    "Interactive multi-page web app with custom UI",       "#6b7280", "#f9fafb", "#e5e7eb"),
]

t_cols = st.columns(3, gap="large")
for i, (icon, name, desc, accent, bg, border) in enumerate(tech_items):
    with t_cols[i % 3]:
        st.markdown(
            f'<div class="ds-card" style="padding:18px 16px;margin-bottom:14px;">'
            f'<div class="ds-card-strip" style="background:{accent};opacity:.7;"></div>'
            f'<div style="display:flex;gap:12px;align-items:flex-start;">'
            f'<div style="width:36px;height:36px;border-radius:9px;flex-shrink:0;'
            f'background:{bg};border:1px solid {border};'
            f'display:flex;align-items:center;justify-content:center;font-size:1rem;">{icon}</div>'
            f'<div>'
            f'<div style="font-size:0.88rem;font-weight:700;color:{accent};margin-bottom:3px;">{name}</div>'
            f'<div style="font-size:0.78rem;color:#6b7280;line-height:1.5;">{desc}</div>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

ui_divider()

# ─────────────────────────────────────────────────────────────────────────────
#  FUTURE SCOPE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl ds-lbl--center">What we\'re building next</p>', unsafe_allow_html=True)

future_items = [
    {
        "icon": "🗣️", "title": "Tamil & Telugu Voice Advisory",
        "desc": "Convert the AI advisory into spoken audio in Tamil and Telugu — making the tool accessible to farmers who cannot read.",
        "accent": "#16a34a", "bg": "#f0fdf4", "border": "#bbf7d0", "tag": "In Design",
    },
    {
        "icon": "📱", "title": "Offline Mobile App",
        "desc": "A lightweight Android app with on-device inference — no internet required. Critical for farmers in remote areas.",
        "accent": "#2563eb", "bg": "#eff6ff", "border": "#dbeafe", "tag": "Planned",
    },
    {
        "icon": "📡", "title": "IoT Sensor Integration",
        "desc": "Connect soil moisture, temperature, and humidity sensors directly to the app for continuous field monitoring.",
        "accent": "#0d9488", "bg": "#f0fdfa", "border": "#99f6e4", "tag": "Research",
    },
    {
        "icon": "🗺️", "title": "District-Level Disease Map",
        "desc": "Aggregate anonymised reports to build a live heatmap of disease outbreaks across Tamil Nadu districts.",
        "accent": "#7c3aed", "bg": "#faf5ff", "border": "#ede9fe", "tag": "Planned",
    },
    {
        "icon": "💊", "title": "Precision Treatment Engine",
        "desc": "Recommend dosage, timing, and type of treatment based on crop stage, variety, disease severity, and local market availability.",
        "accent": "#d97706", "bg": "#fffbeb", "border": "#fde68a", "tag": "Planned",
    },
    {
        "icon": "🤝", "title": "Extension Officer Dashboard",
        "desc": "A dashboard for agricultural extension officers to review flagged cases, prioritise field visits, and track intervention outcomes.",
        "accent": "#dc2626", "bg": "#fef2f2", "border": "#fecaca", "tag": "Planned",
    },
]

f_cols = st.columns(2, gap="large")
for i, f in enumerate(future_items):
    with f_cols[i % 2]:
        st.markdown(
            f'<div class="ds-card" style="padding:18px 18px;margin-bottom:14px;">'
            f'<div class="ds-card-strip" style="background:{f["accent"]};"></div>'
            f'<div style="display:flex;align-items:flex-start;gap:14px;">'
            f'<div style="width:38px;height:38px;border-radius:10px;flex-shrink:0;'
            f'background:{f["bg"]};border:1px solid {f["border"]};'
            f'display:flex;align-items:center;justify-content:center;font-size:1.1rem;">{f["icon"]}</div>'
            f'<div style="flex:1;">'
            f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">'
            f'<div style="font-size:0.88rem;font-weight:800;color:#111827;">{f["title"]}</div>'
            f'<span style="font-size:0.6rem;font-weight:700;letter-spacing:.8px;'
            f'text-transform:uppercase;background:{f["bg"]};border:1px solid {f["border"]};'
            f'color:{f["accent"]};border-radius:999px;padding:1px 8px;">{f["tag"]}</span>'
            f'</div>'
            f'<p style="font-size:0.81rem;color:#6b7280;line-height:1.6;margin:0;">{f["desc"]}</p>'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)
ui_footer()
