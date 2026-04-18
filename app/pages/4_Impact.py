"""Impact · Real-world value for Tamil Nadu farmers."""
import sys
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from _shared import ui_divider, ui_footer

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    '<div class="ds-ph">'
    '<h1 class="ds-ph-title">Real-World Impact</h1>'
    '<p class="ds-ph-sub">'
    'Tamil Nadu contributes over 10 million tonnes of paddy annually. '
    'Crop disease silently erodes yield, income, and food security — '
    'often going undetected until it is too late. '
    'AgriShield-TN was built to change that.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

ui_divider()

# ── Context stats ─────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl">Scale of the problem</p>', unsafe_allow_html=True)

context_stats = [
    ("10M+",    "tonnes/year",    "Tamil Nadu paddy output",           "#16a34a"),
    ("₹4500Cr", "estimated loss", "Annual crop disease damage in TN",  "#d97706"),
    ("70%",     "of farmers",     "Operate holdings under 2 hectares", "#2563eb"),
    ("10",      "disease classes","Detected by AgriShield-TN",         "#7c3aed"),
]

stat_cols = st.columns(4, gap="large")
for col, (value, unit, label, accent) in zip(stat_cols, context_stats):
    with col:
        st.markdown(
            f'<div class="ds-card" style="padding:22px 18px;text-align:center;">'
            f'<div class="ds-card-strip" style="background:{accent};opacity:.65;"></div>'
            f'<div style="font-size:1.9rem;font-weight:900;color:{accent};'
            f'line-height:1;margin-top:4px;">{value}</div>'
            f'<div style="font-size:0.7rem;font-weight:600;letter-spacing:.8px;'
            f'text-transform:uppercase;color:#9ca3af;margin:4px 0 6px;">{unit}</div>'
            f'<div class="ds-prose-muted" style="font-size:0.79rem;">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

ui_divider()

# ── 3 Impact cards ────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl">Core impact areas</p>', unsafe_allow_html=True)

impact_cards = [
    {
        "icon": "⚡", "accent": "#16a34a", "bg": "#f0fdf4", "border": "#bbf7d0",
        "tag": "Speed", "headline": "Diagnosis in under 2 seconds",
        "body": (
            "Manual field inspection requires a trained agronomist to physically visit the crop, "
            "identify symptoms by eye, and cross-reference disease guides — a process that can "
            "take hours or days. AgriShield-TN processes a single leaf photo and returns a ranked "
            "diagnosis with confidence score in under 2 seconds, directly on the user's device."
        ),
        "bullets": [
            "No specialist visit required for initial screening",
            "Works from any standard smartphone camera photo",
            "Immediate result allows same-day intervention decisions",
        ],
    },
    {
        "icon": "🌾", "accent": "#d97706", "bg": "#fffbeb", "border": "#fde68a",
        "tag": "Prevention", "headline": "Earlier detection, smaller spread",
        "body": (
            "Paddy diseases such as Blast and Bacterial Leaf Blight spread rapidly under humid "
            "conditions. The earlier a disease is identified, the narrower the window of spread "
            "to adjacent plants and neighbouring plots. Faster detection enables targeted, "
            "localised treatment rather than broad-spectrum pesticide application across the field."
        ),
        "bullets": [
            "Early-stage detection before visible large-scale symptoms",
            "Supports targeted treatment, reducing unnecessary pesticide use",
            "Potential to limit inter-plot spread with timely alerts",
        ],
    },
    {
        "icon": "🔬", "accent": "#2563eb", "bg": "#eff6ff", "border": "#dbeafe",
        "tag": "Trust", "headline": "Explainability builds confidence",
        "body": (
            "Farmers and agronomists are understandably cautious about trusting an AI system "
            "with decisions that affect their livelihood. AgriShield-TN generates a Grad-CAM "
            "heatmap alongside every prediction, visually highlighting the exact leaf regions "
            "that drove the model's decision — making the AI transparent and auditable."
        ),
        "bullets": [
            "Grad-CAM overlay shows which lesion areas the model focused on",
            "Confidence score flags uncertain predictions for human review",
            "Agronomists can verify or override AI output with full context",
        ],
    },
]

card_cols = st.columns(3, gap="large")
for col, card in zip(card_cols, impact_cards):
    bullet_html = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:9px;margin-bottom:7px;">'
        f'<span style="width:5px;height:5px;border-radius:50%;background:{card["accent"]};'
        f'flex-shrink:0;margin-top:7px;display:inline-block;"></span>'
        f'<span class="ds-prose">{b}</span>'
        f'</div>'
        for b in card["bullets"]
    )
    with col:
        st.markdown(
            f'<div class="ds-card" style="height:100%;">'
            f'<div class="ds-card-strip" style="background:{card["accent"]};opacity:.7;"></div>'

            f'<div class="ds-card-hd">'
            f'<div class="ds-icon-tile" style="background:{card["bg"]};border:1px solid {card["border"]};">'
            f'{card["icon"]}</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:1.1px;'
            f'text-transform:uppercase;color:{card["accent"]};margin-bottom:2px;">{card["tag"]}</div>'
            f'<div style="font-size:0.95rem;font-weight:700;color:#111827;">{card["headline"]}</div>'
            f'</div>'
            f'</div>'

            f'<div class="ds-card-bd">'
            f'<p class="ds-prose" style="margin-bottom:16px;">{card["body"]}</p>'
            f'<div style="border-top:1px solid #f3f4f6;padding-top:14px;">{bullet_html}</div>'
            f'</div>'

            f'</div>',
            unsafe_allow_html=True,
        )

ui_divider()

# ── Who benefits ──────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl">Who this is for</p>', unsafe_allow_html=True)

stakeholders = [
    {
        "icon": "🧑‍🌾", "title": "Farmers",
        "accent": "#16a34a", "bg": "#f0fdf4", "border": "#bbf7d0",
        "body": (
            "Smallholder farmers managing plots under 2 hectares often cannot afford regular "
            "agronomist consultations. AgriShield-TN puts a diagnostic tool in their pocket — "
            "no internet dependency for inference, no agronomic background required."
        ),
        "tags": ["Accessible", "No expertise needed", "Immediate result"],
    },
    {
        "icon": "🔭", "title": "Agronomists & Researchers",
        "accent": "#2563eb", "bg": "#eff6ff", "border": "#dbeafe",
        "body": (
            "Field experts can use the Grad-CAM overlay to validate model decisions at the pixel "
            "level, identify systematic errors, and build annotated datasets to improve the next "
            "model version. Confidence scores clearly flag cases that warrant human judgement."
        ),
        "tags": ["Grad-CAM verification", "Confidence flagging", "Dataset building"],
    },
    {
        "icon": "🏛️", "title": "Policymakers",
        "accent": "#7c3aed", "bg": "#faf5ff", "border": "#ede9fe",
        "body": (
            "Aggregated, anonymised detection data across districts can reveal disease hotspots "
            "before they become crises. This enables targeted advisory deployment, data-driven "
            "subsidy allocation, and early-warning integration with government agriculture portals."
        ),
        "tags": ["District-level insight", "Early warning", "Data-driven policy"],
    },
]

s_cols = st.columns(3, gap="large")
for col, s in zip(s_cols, stakeholders):
    tag_html = "".join(
        f'<span style="font-size:0.72rem;font-weight:600;'
        f'background:{s["bg"]};border:1px solid {s["border"]};color:{s["accent"]};'
        f'border-radius:999px;padding:3px 11px;white-space:nowrap;">{t}</span>'
        for t in s["tags"]
    )
    with col:
        st.markdown(
            f'<div class="ds-card" style="padding:24px 22px;height:100%;">'
            f'<div class="ds-card-strip" style="background:{s["accent"]};opacity:.65;"></div>'
            f'<div style="font-size:1.8rem;margin-bottom:10px;margin-top:4px;">{s["icon"]}</div>'
            f'<div style="font-size:0.97rem;font-weight:700;color:#111827;margin-bottom:10px;">{s["title"]}</div>'
            f'<p class="ds-prose" style="margin-bottom:16px;">{s["body"]}</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:7px;">{tag_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
ui_divider()

# ── Closing note ──────────────────────────────────────────────────────────────
st.markdown(
    '<div style="max-width:600px;margin:36px auto 44px;text-align:center;">'
    '<div style="display:inline-flex;align-items:center;gap:8px;'
    'background:#f0fdf4;border:1px solid #bbf7d0;'
    'border-radius:999px;padding:6px 16px;margin-bottom:16px;">'
    '<span style="width:6px;height:6px;border-radius:50%;background:#16a34a;'
    'display:inline-block;flex-shrink:0;"></span>'
    '<span style="font-size:0.72rem;font-weight:700;color:#15803d;'
    'letter-spacing:1.2px;text-transform:uppercase;">Research &amp; demonstration</span>'
    '</div>'
    '<p class="ds-prose-muted">'
    'AgriShield-TN is a proof-of-concept built for the Tamil Nadu Agri-AI Hackathon 2025. '
    'Figures cited reflect publicly available data on Tamil Nadu agriculture. '
    'All AI predictions should be validated by a certified agronomist before '
    'treatment decisions are made.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

ui_footer()
