"""Diagnose · AI crop health assistant — card-based diagnosis flow."""
import sys
import tempfile
import time
from pathlib import Path

_APP_DIR = Path(__file__).resolve().parent.parent
for _p in [str(_APP_DIR.parent), str(_APP_DIR)]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import streamlit as st
from PIL import Image

st.session_state["_cur_page"] = "diagnose"

from _shared import draw_scan, ui_divider, ui_error, ui_footer
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

# ── Page header with nav ──────────────────────────────────────────────────────
_h_left, _h_right = st.columns([4, 2], gap="small")
with _h_left:
    st.markdown(
        '<div class="diag-eyebrow">&#129302; AI Crop Diagnostic Tool</div>'
        '<div class="diag-card-hd">START YOUR CROP DIAGNOSIS</div>',
        unsafe_allow_html=True,
    )
with _h_right:
    st.markdown('<div style="display:flex;justify-content:flex-end;align-items:center;height:100%;gap:8px;padding-top:8px;">', unsafe_allow_html=True)
    _nb1, _nb2 = st.columns(2, gap="small")
    with _nb1:
        if st.button("🏠  Home", use_container_width=True, key="nav_home"):
            st.switch_page("pages/1_Home.py")
    with _nb2:
        if st.button("📖  Field Guide", use_container_width=True, key="nav_fg"):
            st.switch_page("pages/6_Disease_Library.py")
    st.markdown('</div>', unsafe_allow_html=True)

# ── Three-panel input layout ──────────────────────────────────────────────────
col_up, col_mid, col_det = st.columns([4, 3, 3], gap="large")

with col_up:
    st.markdown(
        '<div class="diag-step-hd">'
        '<span class="diag-step-num">01</span>'
        'CAPTURE &amp; UPLOAD'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<div class="diag-upload-zone">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "leaf", type=["jpg", "jpeg", "png"], label_visibility="collapsed"
    )
    if uploaded_file is not None:
        img_preview = Image.open(uploaded_file)
        uploaded_file.seek(0)
        st.image(img_preview, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="diag-tip">'
        '&#128161; Best results: clear, well-lit single leaf. Avoid blur or heavy shadows.'
        '</div>',
        unsafe_allow_html=True,
    )

    if uploaded_file is not None and uploaded_file.name != st.session_state["last_file_name"]:
        st.session_state["run_analysis"] = False
        st.session_state["last_file_name"] = uploaded_file.name

with col_mid:
    st.markdown(
        '<div class="diag-step-hd" style="justify-content:center;">DIAGNOSIS STATUS</div>',
        unsafe_allow_html=True,
    )
    if uploaded_file is None:
        st.markdown(
            '<div class="diag-status-wrap">'
            '<div class="diag-pulse-ring">'
            '<div class="diag-pulse-inner">&#128247;</div>'
            '</div>'
            '<div class="diag-status-lbl">AWAITING UPLOAD&#8230;</div>'
            '<div class="diag-status-sub">Upload a leaf image to begin your diagnosis</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="diag-status-wrap">'
            '<div class="diag-ready-ring">'
            '<div class="diag-ready-inner">&#10003;</div>'
            '</div>'
            '<div class="diag-status-lbl diag-status-lbl--ready">IMAGE READY</div>'
            '<div class="diag-status-sub">Click Start AI Diagnosis below to analyse</div>'
            '</div>',
            unsafe_allow_html=True,
        )

with col_det:
    st.markdown(
        '<div class="diag-step-hd">'
        '<span class="diag-step-num">02</span>'
        'ADD DETAILS'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:.78rem;font-weight:600;color:#374151;margin-bottom:6px;">'
        '&#128205; Your District</div>',
        unsafe_allow_html=True,
    )
    district = st.selectbox(
        "district",
        options=["(Select district)"] + sorted(DISTRICTS.keys()),
        index=0,
        label_visibility="collapsed",
        help="Used to fetch live weather for disease spread risk",
    )
    st.markdown(
        '<div class="diag-info-box">'
        '&#127806; Crop: <strong>Paddy (Oryza sativa)</strong><br>'
        '&#127981; Model: <strong>ResNet-18 CNN</strong><br>'
        '&#128202; Classes: <strong>10 disease types</strong>'
        '</div>',
        unsafe_allow_html=True,
    )

ui_divider()

# ── CTA button ────────────────────────────────────────────────────────────────
_, cta_col, _ = st.columns([2, 3, 2])
with cta_col:
    st.markdown('<div class="diag-cta-wrap">', unsafe_allow_html=True)
    clicked = st.button(
        "🤖  START AI DIAGNOSIS  →",
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
        'Upload a leaf image to enable diagnosis</div>',
        unsafe_allow_html=True,
    )

# ── Diagnostic parameters strip ───────────────────────────────────────────────
st.markdown('<div class="diag-params-strip">', unsafe_allow_html=True)
_PARAMS = [
    ("&#127806;", "10",       "Paddy Disease Classes"),
    ("&#128205;", "38",       "Tamil Nadu Districts"),
    ("&#128293;", "Grad-CAM", "XAI Explainability"),
    ("&#9889;",   "&lt;2s",   "Diagnosis Time"),
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
            '<div class="ds-lbl">&#129302; Running AI Analysis&#8230;</div>',
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

        # ── 1. DIAGNOSIS BANNER ────────────────────────────────────────────────
        ui_divider()
        st.markdown('<p class="ds-lbl">Diagnosis result</p>', unsafe_allow_html=True)

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
            '&#9203; Generating AI advisory&#8230;</div>',
            unsafe_allow_html=True,
        )
        insight: AgriInsight = generate_agri_insight(predicted_class, confidence)
        insight_slot.empty()

        sev = insight.severity
        sev_text_col, sev_accent, sev_bg_col, sev_border_col, sev_icon = SEV_STYLE.get(
            sev, SEV_STYLE["MODERATE"]
        )

        if pct >= 70:
            conf_color = "#16a34a"; conf_badge = "High Confidence"
        elif pct >= 40:
            conf_color = "#d97706"; conf_badge = "Moderate Confidence"
        else:
            conf_color = "#dc2626"; conf_badge = "Low Confidence"

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid {sev_border_col};'
            f'border-radius:18px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.07);">'
            f'<div style="height:5px;background:{sev_accent};"></div>'
            f'<div style="padding:24px 28px;display:flex;align-items:center;gap:24px;flex-wrap:wrap;">'
            f'<div style="flex:1;min-width:200px;">'
            f'<div style="font-size:.68rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#9ca3af;margin-bottom:6px;">Detected Disease</div>'
            f'<div style="font-size:2rem;font-weight:900;color:#111827;letter-spacing:-1px;line-height:1.1;">{disease_name}</div>'
            f'<div style="font-size:.8rem;color:#6b7280;margin-top:4px;">ResNet-18 CNN &middot; Top-1 prediction</div>'
            f'</div>'
            f'<div style="text-align:center;">'
            f'<div style="font-size:.65rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#9ca3af;margin-bottom:8px;">Severity</div>'
            f'<div style="background:{sev_bg_col};border:1.5px solid {sev_border_col};border-radius:12px;padding:12px 24px;display:inline-block;">'
            f'<div style="font-size:1.5rem;line-height:1;">{sev_icon}</div>'
            f'<div style="font-size:.9rem;font-weight:800;color:{sev_text_col};margin-top:4px;letter-spacing:.5px;">{sev}</div>'
            f'</div></div>'
            f'<div style="text-align:center;min-width:110px;">'
            f'<div style="font-size:.65rem;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#9ca3af;margin-bottom:8px;">Confidence</div>'
            f'<div style="font-size:2.2rem;font-weight:900;color:{conf_color};line-height:1;">'
            f'{pct:.0f}<span style="font-size:1rem;">%</span></div>'
            f'<div style="font-size:.72rem;font-weight:600;color:{conf_color};margin-top:4px;">{conf_badge}</div>'
            f'</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div style="background:#fffbeb;border:1px solid #fde68a;border-radius:12px;'
            f'padding:14px 18px;margin-top:14px;display:flex;gap:12px;align-items:flex-start;">'
            f'<span style="font-size:1.2rem;flex-shrink:0;">&#127806;</span>'
            f'<div>'
            f'<div style="font-size:.72rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:#b45309;margin-bottom:4px;">In Simple Terms</div>'
            f'<div style="font-size:.9rem;color:#374151;font-weight:500;line-height:1.6;">{insight.plain_summary}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )

        # ── 2. IMMEDIATE ACTION + WEATHER RISK ────────────────────────────────
        ui_divider()
        action_col, weather_col = st.columns([1, 1], gap="large")

        with action_col:
            st.markdown(
                '<div style="font-size:.68rem;font-weight:700;letter-spacing:1.2px;'
                'text-transform:uppercase;color:#dc2626;margin-bottom:10px;">&#9889; What To Do Now</div>',
                unsafe_allow_html=True,
            )
            actions_html = "".join(
                f'<div style="display:flex;gap:10px;align-items:flex-start;padding:10px 14px;'
                f'background:#FFFFFF;border:1px solid #e5e7eb;border-radius:10px;margin-bottom:8px;">'
                f'<span style="font-size:.85rem;flex-shrink:0;margin-top:1px;background:#fef2f2;'
                f'border-radius:50%;width:24px;height:24px;display:flex;align-items:center;justify-content:center;">'
                f'{i+1}</span>'
                f'<span style="font-size:.855rem;color:#111827;font-weight:500;line-height:1.5;">{action}</span>'
                f'</div>'
                for i, action in enumerate(insight.immediate_actions)
            )
            st.markdown(
                f'<div style="background:#fef2f2;border:1.5px solid #fecaca;border-radius:14px;padding:18px 16px;">'
                f'<div style="font-size:.97rem;font-weight:800;color:#991b1b;margin-bottom:14px;">Priority Action List</div>'
                f'{actions_html}'
                f'<div style="font-size:.72rem;color:#9ca3af;margin-top:10px;padding-top:10px;border-top:1px solid #fecaca;">'
                f'&#9888;&#65039; Consult a certified agronomist before applying any chemicals.'
                f'</div></div>',
                unsafe_allow_html=True,
            )

        with weather_col:
            st.markdown(
                '<div style="font-size:.68rem;font-weight:700;letter-spacing:1.2px;'
                'text-transform:uppercase;color:#2563eb;margin-bottom:10px;">&#127750; Weather Spread Risk</div>',
                unsafe_allow_html=True,
            )
            selected_district = district if district != "(Select district)" else None
            if selected_district:
                with st.spinner("Fetching weather data&#8230;"):
                    wx = get_weather_risk(selected_district, predicted_class)
            else:
                wx = {"available": False}

            if wx.get("available"):
                WX_RISK_STYLE = {
                    "HIGH":     ("#dc2626", "#fef2f2", "#fecaca", "&#128308;"),
                    "MODERATE": ("#d97706", "#fffbeb", "#fde68a", "&#129000;"),
                    "LOW":      ("#16a34a", "#f0fdf4", "#bbf7d0", "&#128994;"),
                }
                rl = wx["risk_level"]
                wr_col, wr_bg, wr_border, wr_icon = WX_RISK_STYLE.get(rl, WX_RISK_STYLE["MODERATE"])

                reasons_html = "".join(
                    f'<div style="display:flex;gap:8px;align-items:flex-start;margin-bottom:6px;font-size:.8rem;color:#374151;">'
                    f'<span style="flex-shrink:0;color:{wr_col};">&#9658;</span>{r}</div>'
                    for r in wx["risk_reasons"]
                ) or '<div style="font-size:.8rem;color:#6b7280;">Current conditions are relatively favourable.</div>'

                st.markdown(
                    f'<div style="background:#FFFFFF;border:1.5px solid {wr_border};border-radius:14px;overflow:hidden;">'
                    f'<div style="background:{wr_bg};border-bottom:1px solid {wr_border};padding:14px 18px;display:flex;align-items:center;gap:12px;">'
                    f'<div style="font-size:1.8rem;">{wr_icon}</div>'
                    f'<div>'
                    f'<div style="font-size:1rem;font-weight:800;color:{wr_col};">{wx["risk_label"]}</div>'
                    f'<div style="font-size:.75rem;color:#6b7280;margin-top:2px;">&#128205; {wx["district"]}</div>'
                    f'</div></div>'
                    f'<div style="padding:14px 18px;">'
                    f'<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px;">'
                    f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;">'
                    f'<div style="font-size:.65rem;color:#9ca3af;font-weight:600;letter-spacing:.5px;margin-bottom:3px;">TEMPERATURE</div>'
                    f'<div style="font-size:1.1rem;font-weight:800;color:#111827;">{wx["temp"]}&#176;C</div>'
                    f'<div style="font-size:.7rem;color:#6b7280;">{wx["temp_min"]}&#176; &ndash; {wx["temp_max"]}&#176;C today</div>'
                    f'</div>'
                    f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;">'
                    f'<div style="font-size:.65rem;color:#9ca3af;font-weight:600;letter-spacing:.5px;margin-bottom:3px;">HUMIDITY</div>'
                    f'<div style="font-size:1.1rem;font-weight:800;color:#111827;">{wx["humidity"]}%</div>'
                    f'<div style="font-size:.7rem;color:#6b7280;">Relative humidity</div>'
                    f'</div>'
                    f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;">'
                    f'<div style="font-size:.65rem;color:#9ca3af;font-weight:600;letter-spacing:.5px;margin-bottom:3px;">RAIN NOW</div>'
                    f'<div style="font-size:1.1rem;font-weight:800;color:#111827;">{wx["rain_now"]} mm</div>'
                    f'<div style="font-size:.7rem;color:#6b7280;">Current precipitation</div>'
                    f'</div>'
                    f'<div style="background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:10px 12px;">'
                    f'<div style="font-size:.65rem;color:#9ca3af;font-weight:600;letter-spacing:.5px;margin-bottom:3px;">3-DAY RAIN</div>'
                    f'<div style="font-size:1.1rem;font-weight:800;color:#111827;">{wx["rain_3day"]:.0f} mm</div>'
                    f'<div style="font-size:.7rem;color:#6b7280;">Forecast total</div>'
                    f'</div></div>'
                    f'<div style="border-top:1px solid #e5e7eb;padding-top:12px;">'
                    f'<div style="font-size:.7rem;font-weight:700;letter-spacing:.5px;color:#9ca3af;text-transform:uppercase;margin-bottom:8px;">Risk Factors</div>'
                    f'{reasons_html}'
                    f'<div style="font-size:.75rem;color:#6b7280;margin-top:10px;padding-top:8px;border-top:1px solid #f3f4f6;font-style:italic;">'
                    f'{wx["risk_note"]}</div></div></div></div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    '<div style="background:#f9fafb;border:1.5px dashed #e5e7eb;border-radius:14px;padding:32px 20px;text-align:center;">'
                    '<div style="font-size:2rem;margin-bottom:10px;">&#127750;</div>'
                    '<div style="font-size:.9rem;font-weight:700;color:#374151;margin-bottom:6px;">Select your district above</div>'
                    '<div style="font-size:.8rem;color:#9ca3af;line-height:1.5;">'
                    'We\'ll fetch live weather data and assess how current conditions may affect disease spread in your area.'
                    '</div></div>',
                    unsafe_allow_html=True,
                )

        # ── 3. AI AGRICULTURAL ADVISORY ───────────────────────────────────────
        ui_divider()
        st.markdown(
            '<div style="font-size:.68rem;font-weight:700;letter-spacing:1.2px;'
            'text-transform:uppercase;color:#0d9488;margin-bottom:10px;">&#129302; AI Agricultural Advisory</div>',
            unsafe_allow_html=True,
        )

        tier_colors = {
            "high":   ("#16a34a", "#f0fdf4", "#bbf7d0", "&#9989; High Confidence"),
            "medium": ("#d97706", "#fffbeb", "#fde68a", "&#9888;&#65039; Moderate Confidence"),
            "low":    ("#dc2626", "#fef2f2", "#fecaca", "&#128308; Low Confidence"),
        }
        t_accent, t_bg, t_border, t_label = tier_colors[insight.tier]

        source_badge = (
            '<span style="font-size:.68rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;'
            'background:#f0fdf4;border:1px solid #bbf7d0;color:#16a34a;border-radius:999px;padding:2px 10px;">Groq AI</span>'
            if insight.source == "groq" else
            '<span style="font-size:.68rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;'
            'background:#f9fafb;border:1px solid #e5e7eb;color:#6b7280;border-radius:999px;padding:2px 10px;">Knowledge Base</span>'
        )

        st.markdown(
            f'<div style="background:#FFFFFF;border:1px solid #e5e7eb;border-radius:16px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.07);">'
            f'<div style="background:linear-gradient(135deg,#f0fdf4,#dcfce7);border-bottom:1px solid #bbf7d0;padding:16px 24px;display:flex;align-items:center;gap:14px;">'
            f'<div style="width:42px;height:42px;border-radius:11px;background:linear-gradient(135deg,#16a34a,#22c55e);display:flex;align-items:center;justify-content:center;font-size:1.2rem;flex-shrink:0;box-shadow:0 2px 8px rgba(22,163,74,.35);">&#127806;</div>'
            f'<div style="flex:1;">'
            f'<div style="font-size:.95rem;font-weight:800;color:#14532d;">Expert Advisory</div>'
            f'<div style="font-size:.75rem;color:#16a34a;margin-top:2px;">{insight.display_name} &middot; {pct:.1f}% confidence</div>'
            f'</div>{source_badge}</div>'
            f'<div style="background:{t_bg};border-bottom:1px solid {t_border};padding:10px 24px;display:flex;align-items:center;gap:10px;">'
            f'<span style="font-size:.72rem;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:{t_accent};">{t_label}</span>'
            f'<span style="width:1px;height:14px;background:{t_border};flex-shrink:0;"></span>'
            f'<span style="font-size:.82rem;color:{t_accent};">{insight.confidence_note}</span>'
            f'</div>'
            f'<div style="padding:20px 24px;">',
            unsafe_allow_html=True,
        )

        insight_blocks = [
            ("&#128203;", "Disease Summary",      insight.summary,    "#111827", "#f9fafb", "#e5e7eb"),
            ("&#128300;", "Likely Cause",         insight.cause,      "#1d4ed8", "#eff6ff", "#dbeafe"),
            ("&#128138;", "Treatment Guidance",   insight.action,     "#b45309", "#fffbeb", "#fde68a"),
            ("&#128737;&#65039;", "Prevention Strategy", insight.prevention, "#6d28d9", "#faf5ff", "#ede9fe"),
        ]

        adv_a, adv_b = st.columns(2, gap="large")
        for i, (icon, title, body, accent, bg, border) in enumerate(insight_blocks):
            col = adv_a if i % 2 == 0 else adv_b
            with col:
                st.markdown(
                    f'<div style="background:{bg};border:1px solid {border};border-radius:12px;padding:15px 16px;margin-bottom:12px;">'
                    f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">'
                    f'<span style="font-size:1rem;">{icon}</span>'
                    f'<span style="font-size:.8rem;font-weight:700;color:{accent};">{title}</span>'
                    f'</div>'
                    f'<p style="font-size:.845rem;color:#374151;line-height:1.65;margin:0;">{body}</p>'
                    f'</div>',
                    unsafe_allow_html=True,
                )

        st.markdown('</div></div>', unsafe_allow_html=True)

        # ── 4. VISUAL ANALYSIS (expander) ─────────────────────────────────────
        ui_divider()
        with st.expander("&#128444;&#65039; View Grad-CAM Visual Analysis", expanded=False):
            st.markdown(
                '<p style="font-size:.82rem;color:#6b7280;margin:0 0 16px;">'
                'Original leaf image alongside the Grad-CAM heatmap showing which regions the model focused on.'
                '</p>',
                unsafe_allow_html=True,
            )
            img_col, heatmap_col = st.columns(2, gap="large")
            with img_col:
                st.markdown(
                    '<div class="ds-card"><div class="ds-card-hd">'
                    '<span style="width:8px;height:8px;border-radius:50%;background:#16a34a;display:inline-block;"></span>'
                    '<span style="font-size:.78rem;font-weight:600;color:#374151;">Original Image</span>'
                    '</div><div class="ds-card-bd">',
                    unsafe_allow_html=True,
                )
                st.image(image, use_container_width=True)
                st.markdown('</div></div>', unsafe_allow_html=True)

            with heatmap_col:
                st.markdown(
                    '<div class="ds-card"><div class="ds-card-hd">'
                    '<span style="width:8px;height:8px;border-radius:50%;background:#2563eb;display:inline-block;"></span>'
                    '<span style="font-size:.78rem;font-weight:600;color:#374151;">Grad-CAM Heatmap</span>'
                    '</div><div class="ds-card-bd">',
                    unsafe_allow_html=True,
                )
                st.image(gradcam_overlay, use_container_width=True)
                st.markdown('</div></div>', unsafe_allow_html=True)

            gc_pct = gradcam_confidence * 100
            st.markdown(
                f'<div style="background:#eff6ff;border:1px solid #dbeafe;border-radius:10px;padding:12px 16px;margin-top:12px;font-size:.8rem;color:#1d4ed8;">'
                f'&#128300; Grad-CAM attention strength: <strong>{gc_pct:.1f}%</strong> &mdash; '
                f'red/yellow zones are the leaf regions most responsible for this prediction.'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── 5. TOP PREDICTIONS (expander) ─────────────────────────────────────
        with st.expander("&#128202; Model Confidence Breakdown", expanded=False):
            st.markdown(
                '<p style="font-size:.82rem;color:#6b7280;margin:0 0 16px;">Top 3 disease classes by model probability.</p>',
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

        st.markdown(
            '<div style="display:flex;align-items:flex-start;gap:8px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:10px;padding:10px 14px;margin-top:16px;">'
            '<span style="font-size:.85rem;flex-shrink:0;">&#9888;&#65039;</span>'
            '<span style="font-size:.78rem;color:#9ca3af;line-height:1.55;">'
            'AI-generated guidance is for informational purposes only. '
            'Always consult a certified agronomist or your local agricultural extension officer before making treatment decisions.'
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
