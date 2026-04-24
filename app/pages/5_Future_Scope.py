"""Future Scope · AgriShield-TN product roadmap."""
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
    '<h1 class="ds-ph-title">Future Scope</h1>'
    '<p class="ds-ph-sub">'
    'AgriShield-TN v1 is a proof-of-concept built for the Tamil Nadu Agri-AI Hackathon 2025. '
    'The roadmap below outlines the path from demo to a production-grade precision agriculture platform.'
    '</p>'
    '</div>',
    unsafe_allow_html=True,
)

ui_divider()

# ── Roadmap cards ─────────────────────────────────────────────────────────────
st.markdown('<p class="ds-lbl">Product roadmap</p>', unsafe_allow_html=True)

def _roadmap_card(phase, icon, title, timeline, items, accent):
    bullets = "".join(
        f'<div style="display:flex;align-items:flex-start;gap:9px;margin-bottom:8px;">'
        f'<span style="width:5px;height:5px;border-radius:50%;background:{accent};'
        f'flex-shrink:0;margin-top:7px;display:inline-block;"></span>'
        f'<span class="ds-prose">{item}</span>'
        f'</div>'
        for item in items
    )
    return (
        f'<div class="ds-card" style="margin-bottom:20px;">'
        f'<div class="ds-card-strip" style="background:{accent};"></div>'
        f'<div class="ds-card-hd">'
        f'<div class="ds-icon-tile" style="background:#f9fafb;border:1px solid #e5e7eb;font-size:1.4rem;">{icon}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:0.68rem;font-weight:700;letter-spacing:1.1px;'
        f'text-transform:uppercase;color:{accent};margin-bottom:2px;">{phase}</div>'
        f'<div style="font-size:0.97rem;font-weight:700;color:#111827;">{title}</div>'
        f'</div>'
        f'<span style="font-size:0.7rem;font-weight:700;letter-spacing:0.8px;text-transform:uppercase;'
        f'padding:4px 12px;border-radius:999px;background:#f9fafb;'
        f'border:1px solid #e5e7eb;color:#6b7280;white-space:nowrap;">{timeline}</span>'
        f'</div>'
        f'<div class="ds-card-bd">{bullets}</div>'
        f'</div>'
    )

col1, col2 = st.columns(2, gap="large")

with col1:
    st.markdown(
        _roadmap_card(
            "Phase 1", "📱", "Mobile-First PWA", "Q3 2025",
            [
                "Progressive Web App deployable on Android &amp; iOS",
                "Offline inference via ONNX-quantised ResNet-18 (&lt;25 MB)",
                "Tamil &amp; English voice readout of diagnosis",
                "GPS-tagged photo capture for geospatial logging",
            ],
            "#16a34a",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        _roadmap_card(
            "Phase 3", "🧠", "Multi-Crop &amp; Multi-Disease", "Q1 2026",
            [
                "Expand beyond paddy to sugarcane, banana, groundnut",
                "Pest &amp; insect detection alongside disease classification",
                "Severity grading: mild / moderate / severe per detection",
                "Actionable treatment protocol linked to each disease class",
            ],
            "#7c3aed",
        ),
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        _roadmap_card(
            "Phase 2", "🗺️", "District-Level Disease Map", "Q4 2025",
            [
                "Anonymised telemetry from field scans &rarr; heat-map dashboard",
                "Disease outbreak alerts to district agriculture officers",
                "Integration with Tamil Nadu e-Farming portal",
                "Retrospective trend analysis by season / district / variety",
            ],
            "#2563eb",
        ),
        unsafe_allow_html=True,
    )
    st.markdown(
        _roadmap_card(
            "Phase 4", "📈", "Foundation Model Upgrade", "Q2 2026",
            [
                "Replace ResNet-18 backbone with EfficientNet-B3 or ViT-Small",
                "Self-supervised pre-training on Tamil Nadu paddy dataset",
                "Few-shot learning for rare or emerging disease classes",
                "Federated learning to train on farmer data without centralising images",
            ],
            "#d97706",
        ),
        unsafe_allow_html=True,
    )

ui_divider()

# ── Open research questions ───────────────────────────────────────────────────
st.markdown('<p class="ds-lbl">Open research questions</p>', unsafe_allow_html=True)

questions = [
    ("🌿", "Domain Shift",          "#16a34a",
     "Models trained on field photos from one district may degrade on images from another due to soil, "
     "lighting, and camera variation. Robust domain adaptation techniques are needed for pan-TN deployment."),
    ("🔬", "Calibration",           "#2563eb",
     "High softmax confidence does not always mean the model is correct. Temperature scaling and conformal "
     "prediction can produce reliable uncertainty bounds for farmer-facing applications."),
    ("✨", "Low-Resource Learning",  "#7c3aed",
     "Many rare disease classes have fewer than 200 training images. Synthetic augmentation, "
     "generative models, and SMOTE-style oversampling are active research areas."),
    ("⚡", "Edge Deployment",        "#d97706",
     "Running inference on a ₹5000 feature phone with no internet requires extreme model compression. "
     "Quantisation-aware training, knowledge distillation, and pruning are key levers."),
]

for icon, title, accent, desc in questions:
    st.markdown(
        f'<div class="ds-card" style="margin-bottom:12px;">'
        f'<div style="position:absolute;top:0;left:0;bottom:0;width:3px;background:{accent};opacity:.7;"></div>'
        f'<div style="display:flex;align-items:flex-start;gap:14px;padding:18px 20px 18px 24px;">'
        f'<div class="ds-icon-tile" style="background:#f9fafb;border:1px solid #e5e7eb;'
        f'width:38px;height:38px;font-size:1.1rem;flex-shrink:0;">{icon}</div>'
        f'<div style="flex:1;">'
        f'<div style="font-size:0.95rem;font-weight:700;color:#111827;margin-bottom:5px;">{title}</div>'
        f'<p class="ds-prose-muted">{desc}</p>'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

st.markdown('<div style="height:40px;"></div>', unsafe_allow_html=True)
ui_footer()
