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
from src.utils.story_mapper import build_story, FarmerStory
from src.utils.visual_mapper import build_visual_state, VisualState
from src.llm.agri_insight import generate_agri_insight, AgriInsight

# ── Session state ─────────────────────────────────────────────────────────────
if "run_analysis" not in st.session_state:
    st.session_state["run_analysis"] = False
if "last_file_name" not in st.session_state:
    st.session_state["last_file_name"] = None
if "voice_district" not in st.session_state:
    st.session_state["voice_district"] = None
if "voice_qa_question" not in st.session_state:
    st.session_state["voice_qa_question"] = None
if "voice_qa_answer" not in st.session_state:
    st.session_state["voice_qa_answer"] = None


@st.cache_data(ttl=600)
def _get_live_weather(district: str) -> dict:
    """Fetch live weather for district (cached 10 min to avoid API spam)."""
    from src.utils.weather import get_weather_risk
    return get_weather_risk(district, "normal")


@st.cache_data(ttl=86400, show_spinner=False)
def _gen_farmer_img(mood: str) -> "str | None":
    """AI-generated farmer illustration, cached 24 h (disk + memory)."""
    from src.utils.image_gen import generate_farmer_image
    return generate_farmer_image(mood)


@st.cache_data(ttl=86400, show_spinner=False)
def _gen_crop_img(crop_state: str) -> "str | None":
    """AI-generated crop state illustration, cached 24 h."""
    from src.utils.image_gen import generate_crop_image
    return generate_crop_image(crop_state)


@st.cache_data(ttl=86400, show_spinner=False)
def _gen_wx_img(weather_state: str) -> "str | None":
    """AI-generated weather scene illustration, cached 24 h."""
    from src.utils.image_gen import generate_weather_image
    return generate_weather_image(weather_state)


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

# ── Step flow strip — active step tracks upload state ────────────────────────
_has_upload = bool(st.session_state.get("_has_upload"))
_step1_cls = "diag-step-item diag-step-item--done" if _has_upload else "diag-step-item diag-step-item--active"
_step2_cls = "diag-step-item diag-step-item--active" if _has_upload else "diag-step-item"
_step3_cls = "diag-step-item"
st.markdown(
    f'<div class="diag-steps-strip">'
    f'<div class="{_step1_cls}">'
    '<div class="diag-step-circle">1</div>'
    '<div class="diag-step-text">இலை படம்<br><small>Upload Leaf</small></div>'
    '</div>'
    '<div class="diag-step-connector"></div>'
    f'<div class="{_step2_cls}">'
    '<div class="diag-step-circle">2</div>'
    '<div class="diag-step-text">மாவட்டம்<br><small>Select District</small></div>'
    '</div>'
    '<div class="diag-step-connector"></div>'
    f'<div class="{_step3_cls}">'
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
        '<div class="diag-ex-photo" style="background-image:url(https://images.unsplash.com/photo-1587131782738-de30ea91a542?w=120&q=70&fit=crop)">'
        '<span class="diag-ex-badge diag-ex-badge--bad">Diseased</span></div>'
        '<div class="diag-ex-photo" style="background-image:url(https://images.unsplash.com/photo-1536054009244-c43bb5f1c1ac?w=120&q=70&fit=crop)">'
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
        key="district_sel",
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

    # ── Live weather card — 4 states: no district / loading / failure / success ──
    if district == t("diagnose.select_district"):
        # State: no district selected yet
        st.markdown(
            '<div class="wx-mini-card">'
            '<div class="wx-mini-hd">&#127806; Live Weather for Your District</div>'
            '<div class="wx-mini-body">'
            '<div class="wx-mini-msg" style="color:#6b7280;font-style:italic;">'
            '&#128205; Select your district above to see live weather and spread risk.'
            '</div></div></div>',
            unsafe_allow_html=True,
        )
    else:
        _wx_mini = _get_live_weather(district)
        if _wx_mini.get("available") and isinstance(_wx_mini.get("temp"), (int, float)):
            # State: success — show live weather with farmer headline
            _wm_icon     = _wx_mini.get("condition_icon", "&#127780;&#65039;")
            _wm_headline = _wx_mini.get("farmer_headline", "Weather data loaded")
            _wind_pill   = (
                f'<span class="wx-mini-pill">&#128168; {round(_wx_mini["wind_kmh"])} km/h wind</span>'
                if isinstance(_wx_mini.get("wind_kmh"), (int, float)) and _wx_mini["wind_kmh"] > 0
                else ""
            )
            st.markdown(
                f'<div class="wx-mini-card">'
                f'<div class="wx-mini-hd">{_wm_icon} Live Weather &middot; {district}</div>'
                f'<div class="wx-mini-body">'
                f'<div class="wx-mini-row">'
                f'<span class="wx-mini-temp-val">{_wx_mini["temp"]:.0f}&#176;C</span>'
                f'<span class="wx-mini-temp-rng"> &#8595;{_wx_mini["temp_min"]:.0f}&#176;'
                f' &#8593;{_wx_mini["temp_max"]:.0f}&#176;</span>'
                f'</div>'
                f'<div class="wx-mini-pills">'
                f'<span class="wx-mini-pill">&#128167; {int(_wx_mini["humidity"])}% humidity</span>'
                f'<span class="wx-mini-pill">&#127783; {_wx_mini["rain_3day"]:.0f}mm / 3d</span>'
                f'{_wind_pill}'
                f'</div>'
                f'<div class="wx-mini-msg">{_wm_headline}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        else:
            # State: API failure
            st.markdown(
                '<div class="wx-mini-card">'
                '<div class="wx-mini-hd">&#127780;&#65039; Weather Unavailable</div>'
                '<div class="wx-mini-body">'
                '<div class="wx-mini-msg" style="color:#9ca3af;">'
                'Could not load live weather &mdash; check your connection and try again.'
                '</div></div></div>',
                unsafe_allow_html=True,
            )

    # ── Voice input for district only ─────────────────────────────────────────
    st.markdown(
        '<div class="voice-input-panel">'
        '<div class="voice-panel-hd">&#128205; Say District Name'
        '<span class="voice-panel-ta"> · மாவட்டம் பெயர் சொல்லுங்கள்</span>'
        '</div>'
        '<div style="font-size:.7rem;color:#6b7280;margin-bottom:6px;">'
        'E.g. speak <strong>"Chennai"</strong>, <strong>"Madurai"</strong>, <strong>"Coimbatore"</strong>…'
        '</div>',
        unsafe_allow_html=True,
    )
    _voice_audio = st.audio_input(
        "Say district name",
        label_visibility="collapsed",
        key="voice_district_audio",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if _voice_audio is not None:
        with st.spinner("Listening..."):
            try:
                from utils.voice_utils import transcribe_audio as _va_transcribe
                _transcript = _va_transcribe(_voice_audio.read(), lang_key=get_lang())
            except Exception:
                _transcript = None
        if _transcript and _transcript not in ("Transcription failed", "Could not understand audio"):
            _lower_t = _transcript.lower()
            _matched_d = next(
                (d for d in DISTRICTS if d.lower() in _lower_t or _lower_t in d.lower()),
                None,
            )
            if _matched_d:
                st.session_state["district_sel"] = _matched_d
                st.rerun()
            else:
                st.markdown(
                    f'<div class="voice-transcript">&#128266; Heard: "{_transcript}"</div>',
                    unsafe_allow_html=True,
                )
                st.caption("District not found. Use the Ask AI section below for questions.")
        elif _transcript is not None:
            st.warning("Could not transcribe. Please try again.")

    # CTA inside the right column
    _district_selected = district != t("diagnose.select_district")
    _can_run = uploaded_file is not None and _district_selected

    st.markdown('<div class="diag-cta-wrap">', unsafe_allow_html=True)
    clicked = st.button(
        t("diagnose.start_button"),
        use_container_width=True,
        disabled=not _can_run,
        key="start_diag_btn",
    )
    st.markdown('</div>', unsafe_allow_html=True)
    if clicked:
        st.session_state["run_analysis"] = True
        st.rerun()

    if not _can_run:
        if uploaded_file is None and not _district_selected:
            _hint = t("diagnose.upload_to_enable")
        elif uploaded_file is None:
            _hint = t("diagnose.upload_to_enable")
        else:
            _hint = "&#128205; Please select your district to enable diagnosis"
        st.markdown(
            f'<div style="text-align:center;font-size:.77rem;color:#9ca3af;margin-top:4px;">'
            f'{_hint}</div>',
            unsafe_allow_html=True,
        )

# ── Voice Q&A panel ──────────────────────────────────────────────────────────
st.markdown(
    '<div class="voice-qa-panel">'
    '<div class="voice-qa-hd">'
    '<span class="voice-qa-hd-icon">&#128172;</span>'
    'Ask AI by Voice'
    '<span class="voice-qa-hd-ta"> · குரல் மூலம் AI ஐ கேளுங்கள்</span>'
    '</div>'
    '<div style="font-size:.78rem;color:#6b7280;margin-bottom:12px;">'
    'Ask anything about this disease — symptoms, treatment, medicines, prevention…'
    '</div>',
    unsafe_allow_html=True,
)
_qa_audio = st.audio_input(
    "Ask any question about crop disease",
    label_visibility="collapsed",
    key="voice_qa_audio",
)
st.markdown('</div>', unsafe_allow_html=True)

if _qa_audio is not None:
    with st.spinner("&#128266; Transcribing your question..."):
        try:
            from utils.voice_utils import transcribe_audio as _qa_transcribe
            _qa_text = _qa_transcribe(_qa_audio.read(), lang_key=get_lang())
        except Exception:
            _qa_text = None
    if _qa_text and _qa_text not in ("Transcription failed", "Could not understand audio"):
        st.session_state["voice_qa_question"] = _qa_text
        with st.spinner("&#129302; AI is answering..."):
            try:
                from src.llm.groq_client import call_groq
                _lang_name = {"en": "English", "ta": "Tamil", "hi": "Hindi"}.get(get_lang(), "English")
                _qa_sys = (
                    f"You are AgriShield-TN, an expert AI crop doctor for Tamil Nadu paddy farmers. "
                    f"Answer the farmer's question about crop diseases, prevention, medicines, and treatment. "
                    f"Be practical and concise (under 120 words). Use simple language. "
                    f"Reply in {_lang_name}."
                )
                _diag_ctx = st.session_state.get("diag_disease_name")
                if _diag_ctx:
                    _pct_ctx = st.session_state.get("diag_pct", 0)
                    _qa_sys += f" Current diagnosis context: {_diag_ctx} ({_pct_ctx:.0f}% confidence)."
                _qa_answer = call_groq(_qa_text, system_prompt=_qa_sys, max_tokens=200)
            except Exception:
                _qa_answer = None
        st.session_state["voice_qa_answer"] = _qa_answer or "Unable to get an answer. Please try again."
    elif _qa_text is not None:
        st.warning("Could not transcribe. Please speak clearly and try again.")

# Show Q&A exchange if available
if st.session_state.get("voice_qa_question"):
    st.markdown(
        f'<div class="voice-qa-question">'
        f'<div class="voice-qa-question-lbl">&#127908; YOUR QUESTION</div>'
        f'{st.session_state["voice_qa_question"]}'
        f'</div>',
        unsafe_allow_html=True,
    )
if st.session_state.get("voice_qa_answer"):
    st.markdown(
        f'<div class="voice-qa-answer">'
        f'<div class="voice-qa-answer-lbl">&#129302; AI ANSWER</div>'
        f'{st.session_state["voice_qa_answer"]}'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Listen to answer button + Stop
    _qa_listen_col, _qa_stop_col, _qa_clear_col = st.columns([2, 1, 1], gap="small")
    with _qa_listen_col:
        if st.button("🔊 Listen to Answer", key="qa_listen_btn", use_container_width=True):
            with st.spinner("Generating voice..."):
                try:
                    from utils.voice_utils import generate_speech, autoplay_audio
                    _qa_audio_b64 = generate_speech(
                        st.session_state["voice_qa_answer"], lang=get_lang()
                    )
                    autoplay_audio(_qa_audio_b64)
                except Exception as _qve:
                    st.warning(f"Voice unavailable: {_qve}")
    with _qa_stop_col:
        if st.button("■ Stop", key="qa_stop_btn", use_container_width=True):
            from utils.voice_utils import stop_audio
            stop_audio()
    with _qa_clear_col:
        if st.button("✕ Clear", key="qa_clear_btn", use_container_width=True):
            st.session_state["voice_qa_question"] = None
            st.session_state["voice_qa_answer"] = None
            if "voice_qa_audio" in st.session_state:
                del st.session_state["voice_qa_audio"]
            st.rerun()


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
        _fstory: FarmerStory  = build_story(predicted_class, sev, confidence, wx, disease_name)
        _vstate: VisualState  = build_visual_state(sev, wx, _fstory)

        # ── AI image generation (cached 24h — only calls API on first run per state)
        _gen_farmer_url = _gen_farmer_img(_vstate.farmer_mood)
        _gen_crop_url   = _gen_crop_img(_vstate.crop_state)
        _gen_wx_url     = _gen_wx_img(_vstate.weather_state)

        # Pre-compute crop illustration: AI-generated → emoji fallback
        _crop_illus = (
            f'<img src="{_gen_crop_url}" class="sc-gen-img" alt="{_vstate.crop_label}" />'
            if _gen_crop_url
            else _fstory.plant_emoji
        )

        # Farmer illustration: AI-generated → static asset → emoji fallback
        if _gen_farmer_url:
            _farmer_el = (
                f'<img src="{_gen_farmer_url}"'
                f' class="sg-farmer {_vstate.farmer_css_class}"'
                f' title="{_vstate.farmer_label}" />'
            )
        else:
            _farmer_img_path = _APP_DIR / "assets" / _vstate.farmer_img_local
            if _farmer_img_path.exists():
                with open(str(_farmer_img_path), "rb") as _bf:
                    _f64 = base64.b64encode(_bf.read()).decode()
                _farmer_el = (
                    f'<img src="data:image/png;base64,{_f64}"'
                    f' class="sg-farmer {_vstate.farmer_css_class}"'
                    f' title="{_vstate.farmer_label}" />'
                )
            else:
                _farmer_el = (
                    f'<span class="sg-farmer-emoji {_vstate.farmer_css_class}"'
                    f' title="{_vstate.farmer_label}">{_vstate.farmer_emoji}</span>'
                )

        # 1. Greeting banner — mood class drives banner border/bg tint
        st.markdown(
            f'<div class="sg-banner sg-banner--{_vstate.farmer_mood}">'
            f'<div class="sg-text">'
            f'<div class="sg-title">{_fstory.greeting}</div>'
            f'<div class="sg-sub">{_fstory.greeting_sub}</div>'
            f'</div>'
            f'{_farmer_el}'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Voice readout — compact helper bar ────────────────────────────────
        _vl_left, _vl_btn1, _vl_btn2 = st.columns([5, 1, 1], gap="small")
        with _vl_left:
            st.markdown(
                '<div class="voice-listen-sentinel"></div>'
                '<span class="voice-listen-icon">&#128266;</span>'
                '<span class="voice-listen-text">'
                '<span class="voice-listen-title">&#128266; Hear diagnosis read aloud</span>'
                '<span class="voice-listen-sub"> &nbsp;·&nbsp; கண்டறிதலை கேளுங்கள்</span>'
                '</span>',
                unsafe_allow_html=True,
            )
        with _vl_btn1:
            if st.button("▶", key="voice_readout_btn", use_container_width=True, help="Listen to diagnosis"):
                _speech_parts = [
                    f"{disease_name} detected with {pct:.0f} percent confidence.",
                    insight.cause[:160].rstrip(".") + ".",
                ]
                if insight.immediate_actions:
                    _speech_parts.append(f"First action: {insight.immediate_actions[0]}.")
                _speech_text = " ".join(_speech_parts)
                with st.spinner("Generating voice..."):
                    try:
                        from utils.voice_utils import generate_speech, autoplay_audio
                        _audio_b64 = generate_speech(_speech_text, lang=get_lang())
                        autoplay_audio(_audio_b64)
                    except Exception as _ve:
                        st.warning(f"Voice unavailable: {_ve}")
        with _vl_btn2:
            if st.button("■", key="voice_diag_stop_btn", use_container_width=True, help="Stop audio"):
                from utils.voice_utils import stop_audio
                stop_audio()

        # 2. What's happening — crop state class drives left-border accent
        st.markdown(
            f'<div class="story-card story-card--d1 {_vstate.crop_css_class}">'
            f'<div class="sc-illus">'
            f'<div class="sc-illus-plants" style="background:{_fstory.plant_bg};">'
            f'{_crop_illus}'
            f'</div>'
            f'</div>'
            f'<div class="sc-body">'
            f'<div class="sc-title">What&#39;s happening in your crop?</div>'
            f'<div class="sc-sub">{_fstory.what_sub}</div>'
            f'<div class="sc-risk {_fstory.risk_cls}">'
            f'<span class="sc-risk-badge {_fstory.risk_badge_cls}">{_fstory.risk_label}</span>'
            f'<span class="sc-risk-text">{_fstory.risk_msg}</span>'
            f'</div>'
            f'</div>'
            f'<div class="sc-sad-leaf">{_fstory.sad_leaf}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 3. Why is this happening — use live weather when available
        if wx.get("available") and isinstance(wx.get("humidity"), (int, float)):
            _hum_display  = f"{int(wx['humidity'])}%"
            _cond_icon    = wx.get("condition_icon", _fstory.wx_icon2)
            _cond_display = wx.get("condition", wx.get("risk_label", _fstory.weather_label))
            _rain_cue     = (
                f'&nbsp;&nbsp;&#183;&nbsp;&nbsp;&#127783; {wx["rain_3day"]:.0f}mm rain / 3d'
                if isinstance(wx.get("rain_3day"), (int, float)) and wx["rain_3day"] > 0
                else ""
            )
        else:
            _hum_display  = _fstory.humidity_label
            _cond_icon    = _fstory.wx_icon2
            _cond_display = _fstory.weather_label
            _rain_cue     = ""

        st.markdown(
            f'<div class="story-card story-card--d2">'
            f'<div class="sc-illus">'
            f'<div class="sc-illus-circle" style="background:{_fstory.circle_bg};">'
            f'{_fstory.circle_emoji}'
            f'</div>'
            f'</div>'
            f'<div class="sc-body">'
            f'<div class="sc-title">Why is this happening?</div>'
            f'<div class="sc-sub">{_fstory.why_text}</div>'
            f'<div class="sc-why-cues">'
            f'{_fstory.wx_icon} {_hum_display} humidity'
            f'&nbsp;&nbsp;&#183;&nbsp;&nbsp;'
            f'{_cond_icon} {_cond_display}'
            f'{_rain_cue}'
            f'</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 4. Action cards
        st.markdown('<div class="sa-section-hd">What should you do now?</div>', unsafe_allow_html=True)
        st.markdown('<div class="sa-section-sub">Follow these simple steps to protect your crop.</div>', unsafe_allow_html=True)
        _sa_html = '<div class="sa-grid">'
        for _i, (_ico, _lbl, _bg1, _bg2) in enumerate(_fstory.actions[:4], 1):
            _sa_html += (
                f'<div class="sa-card">'
                f'<div class="sa-illus" style="background:linear-gradient(135deg,{_bg1},{_bg2});">'
                f'<span style="font-size:3.4rem;">{_ico}</span>'
                f'<div class="sa-num-badge">{_i}</div>'
                f'</div>'
                f'<div class="sa-footer">'
                f'<div class="sa-label">{_lbl}</div>'
                f'</div>'
                f'</div>'
            )
        _sa_html += '</div>'
        st.markdown(_sa_html, unsafe_allow_html=True)

        # 5. Weather section — live data from district API
        if wx.get("available"):
            _wx_risk     = wx.get("risk_level", "UNKNOWN")
            _sw_headline = wx.get("farmer_headline", "How is the weather today?")
            _sw_story    = wx.get("farmer_story", "")
            _cond_icon   = wx.get("condition_icon", "&#127780;&#65039;")
            _cond_label  = wx.get("condition", "")
            if _wx_risk == "HIGH":
                _sw_cls, _sw_icon_cls = "sw-section--bad", "sw-icon--cloud"
                _sw_badge = f'{_cond_icon} {_cond_label} &rarr; Spread risk is HIGH &#9888;&#65039;'
            elif _wx_risk == "MODERATE":
                _sw_cls, _sw_icon_cls = "sw-section--mod", "sw-icon--cloud"
                _sw_badge = f'{_cond_icon} {_cond_label} &rarr; Monitor closely'
            else:
                _sw_cls, _sw_icon_cls = "sw-section--good", "sw-icon--sun"
                _sw_badge = f'{_cond_icon} {_cond_label} &rarr; Spread is unlikely &#128578;'
        else:
            _sw_cls, _sw_icon_cls = "sw-section--unk", "sw-icon--sun"
            _cond_icon   = "&#127780;&#65039;"
            _sw_headline = "How is the weather today?"
            _sw_story    = "Weather data is unavailable for your area. Stay vigilant and monitor your crop."
            _sw_badge    = "&#127780;&#65039; Unknown &rarr; Stay vigilant"

        # Weather icon: AI-generated scene → WMO emoji fallback
        _wx_icon_html = (
            f'<img src="{_gen_wx_url}" class="sc-gen-img--wx" alt="{_vstate.weather_label}" />'
            if _gen_wx_url
            else _cond_icon
        )

        _wx_pills_html = ""
        if wx.get("available") and isinstance(wx.get("temp"), (int, float)):
            _wind_p  = (
                f'<span class="wx-data-pill">&#128168; <strong>{round(wx["wind_kmh"])} km/h</strong> wind</span>'
                if isinstance(wx.get("wind_kmh"), (int, float)) and wx["wind_kmh"] > 0 else ""
            )
            _cloud_p = (
                f'<span class="wx-data-pill">&#9729;&#65039; <strong>{int(wx["cloud_pct"])}%</strong> cloud</span>'
                if isinstance(wx.get("cloud_pct"), (int, float)) else ""
            )
            _wx_pills_html = (
                f'<div class="wx-data-pills">'
                f'<span class="wx-data-pill">&#127777;&#65039; <strong>{wx["temp"]:.0f}&#176;C</strong>'
                f' <small style="font-weight:400;opacity:.75;">'
                f'&#8595;{wx["temp_min"]:.0f}&#176; &#8593;{wx["temp_max"]:.0f}&#176;</small></span>'
                f'<span class="wx-data-pill">&#128167; <strong>{int(wx["humidity"])}%</strong> humidity</span>'
                f'<span class="wx-data-pill">&#127783; <strong>{wx["rain_3day"]:.0f}mm</strong> / 3 days</span>'
                f'{_wind_p}'
                f'{_cloud_p}'
                f'</div>'
            )
        st.markdown(
            f'<div class="sw-section {_sw_cls}">'
            f'<div class="sw-icon {_sw_icon_cls} {_vstate.weather_css_class}">{_wx_icon_html}</div>'
            f'<div class="sw-content">'
            f'<div class="sw-title">{_sw_headline}</div>'
            f'<div class="sw-msg">{_sw_story}</div>'
            f'{_wx_pills_html}'
            f'<div class="sw-badge">{_sw_badge}</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # 6. Tip banner
        st.markdown(
            f'<div class="story-tip">'
            f'<span class="st-tip-icon">&#128161;</span>'
            f'<span class="st-tip-text"><strong>Tip:</strong> {_fstory.tip_msg}</span>'
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
