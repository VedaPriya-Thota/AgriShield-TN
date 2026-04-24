# AgriShield-TN — Complete Project Reference

---

## 1. What It Is

**AgriShield-TN** is an AI-powered crop health diagnosis system for paddy (rice) farmers in Tamil Nadu, India. Farmers upload a leaf photo and receive a disease name, confidence score, visual Grad-CAM heatmap, weather-based risk assessment, and multilingual AI advisory — all served through a Streamlit web app.

**Core vision:** Bridge the gap between agricultural AI and actual farmer adoption via instant, explainable, multilingual crop health diagnostics.

---

## 2. System Architecture Diagram

```
╔══════════════════════════════════════════════════════════════════════════════════╗
║                          AgriShield-TN  —  System Architecture                 ║
╚══════════════════════════════════════════════════════════════════════════════════╝

 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                        STREAMLIT FRONTEND  (app/)                           │
 │                                                                             │
 │  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐  │
 │  │ 1_Home   │  │2_Analyze_Leaf│  │3_What_To_Do  │  │6_Disease_Library   │  │
 │  │ Landing  │  │  [MAIN UI]   │  │ Action Plan  │  │  Encyclopedia      │  │
 │  └──────────┘  └──────┬───────┘  └──────────────┘  └────────────────────┘  │
 │                        │                                                     │
 │         ┌──────────────┼──────────────────┐                                 │
 │         │              │                  │                                 │
 │  ┌──────▼──────┐ ┌─────▼──────┐  ┌───────▼──────┐                         │
 │  │  Image      │ │  District  │  │  Language    │                          │
 │  │  Upload     │ │  Selector  │  │  Selector    │                          │
 │  │ (JPG/PNG)   │ │ (38 TN     │  │ EN/TA/HI     │                          │
 │  └──────┬──────┘ │ districts) │  └───────┬──────┘                         │
 │         │        └─────┬──────┘          │                                 │
 │         │              │         ┌───────▼────────────┐                    │
 │         │              │         │  i18n / lang_utils  │                   │
 │         │              │         │  translations.py    │                   │
 │         │              │         │  (600+ strings)     │                   │
 │         │              │         └────────────────────┘                    │
 └─────────┼──────────────┼──────────────────────────────────────────────────┘
           │              │
           ▼              ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                          INFERENCE PIPELINE  (src/)                         │
 │                                                                             │
 │  ┌────────────────────────────────────────────────────────────────────┐    │
 │  │                    IMAGE CLASSIFICATION                             │    │
 │  │                                                                     │    │
 │  │   Input Image (JPG/PNG)                                             │    │
 │  │         │                                                           │    │
 │  │   ┌─────▼──────────────────────────────────────────────────────┐  │    │
 │  │   │              PREPROCESSING  (transforms.py)                 │  │    │
 │  │   │  Resize 224×224 → Normalize (ImageNet μ/σ) → Tensor         │  │    │
 │  │   └─────┬──────────────────────────────────────────────────────┘  │    │
 │  │         │                                                           │    │
 │  │   ┌─────▼──────────────────────────────────────────────────────┐  │    │
 │  │   │              ResNet-18 BACKBONE  (image_encoder.py)         │  │    │
 │  │   │  Conv1 → BN → ReLU → MaxPool                                │  │    │
 │  │   │  Layer1 (2× BasicBlock) → 64-dim                            │  │    │
 │  │   │  Layer2 (2× BasicBlock) → 128-dim                           │  │    │
 │  │   │  Layer3 (2× BasicBlock) → 256-dim                           │  │    │
 │  │   │  Layer4 (2× BasicBlock) → 512-dim  ← Grad-CAM hook here     │  │    │
 │  │   │  AvgPool → Flatten → 512-dim feature vector                  │  │    │
 │  │   └─────┬──────────────────────────────────────────────────────┘  │    │
 │  │         │                                                           │    │
 │  │   ┌─────▼──────────────────────────────────────────────────────┐  │    │
 │  │   │              CLASSIFIER HEAD  (disease_classifier.py)       │  │    │
 │  │   │  Linear(512 → 256) → ReLU → Dropout(0.3)                    │  │    │
 │  │   │  Linear(256 → 10)  → logits → softmax                       │  │    │
 │  │   └─────┬──────────────────────────────────────────────────────┘  │    │
 │  │         │                                                           │    │
 │  │         ▼                                                           │    │
 │  │   Top-1 prediction + confidence %  +  Top-3 alternatives            │    │
 │  └────────────────────────────────────────────────────────────────────┘    │
 │                                                                             │
 │  ┌────────────────────────────────────────────────────────────────────┐    │
 │  │                    EXPLAINABILITY  (explain.py)                     │    │
 │  │                                                                     │    │
 │  │   Grad-CAM                                                          │    │
 │  │   ├── Register forward hook on Layer4                               │    │
 │  │   ├── Register backward hook on Layer4 gradients                    │    │
 │  │   ├── Compute weighted sum of activation maps                       │    │
 │  │   ├── ReLU + upsample to 224×224                                    │    │
 │  │   └── Overlay heatmap on original image                             │    │
 │  │                                                                     │    │
 │  │   ExplanationResult dataclass                                       │    │
 │  │   ├── predicted_class, display_name, confidence_pct                 │    │
 │  │   ├── headline, short_desc, cause, spread, symptoms, treatment      │    │
 │  │   ├── urgency_label (CRITICAL / HIGH / MODERATE / LOW)              │    │
 │  │   ├── reliability note (based on confidence tier)                   │    │
 │  │   └── cam_note, action_urgency                                      │    │
 │  └────────────────────────────────────────────────────────────────────┘    │
 └─────────────────────────────────────────────────────────────────────────────┘
           │                              │
           ▼                              ▼
 ┌──────────────────────┐     ┌───────────────────────────────────────────────┐
 │   WEATHER MODULE      │     │           LLM ADVISORY MODULE                 │
 │   (utils/weather.py)  │     │           (llm/agri_insight.py)               │
 │                       │     │                                               │
 │  OpenMeteo API        │     │  Build prompt:                                │
 │  (free, no key)       │     │  ├── Disease name + confidence tier           │
 │       │               │     │  ├── Language instruction (EN/TA/HI)          │
 │  Current weather +    │     │  └── Urgency framing                          │
 │  3-day forecast       │     │             │                                 │
 │       │               │     │     ┌───────▼───────┐   ┌──────────────────┐ │
 │  38 TN district       │     │     │  Groq API      │   │  Static Fallback │ │
 │  coordinates          │     │     │  llama-3.1-8b  │   │  Knowledge Base  │ │
 │       │               │     │     │  temp=0.4      │   │  (10 diseases ×  │ │
 │  Disease risk rules   │     │     └───────┬───────┘   │   3 languages)   │ │
 │  per disease class    │     │             │            └──────────────────┘ │
 │       │               │     │     JSON parse → AgriInsight dataclass        │
 │  Output:              │     │     ├── summary, cause, action, prevention    │
 │  HIGH/MEDIUM/LOW      │     │     ├── immediate_actions checklist           │
 │  + contextual note    │     │     ├── confidence_note                       │
 └──────────┬────────────┘     │     └── source: "groq" or "fallback"          │
            │                  └───────────────────────┬───────────────────────┘
            │                                          │
            └─────────────────┬────────────────────────┘
                              │
                              ▼
 ┌─────────────────────────────────────────────────────────────────────────────┐
 │                        RESULTS RENDERED IN UI                               │
 │                                                                             │
 │   ┌─────────────────┐  ┌──────────────────┐  ┌────────────────────────┐   │
 │   │ Disease Name     │  │  Grad-CAM Image  │  │  Weather Risk Card     │   │
 │   │ + Confidence %   │  │  Heatmap Overlay │  │  HIGH / MED / LOW      │   │
 │   │ + Top-3 alts     │  │  + Urgency badge │  │  + forecast note       │   │
 │   └─────────────────┘  └──────────────────┘  └────────────────────────┘   │
 │                                                                             │
 │   ┌──────────────────────────────────────────────────────────────────────┐ │
 │   │  Groq Advisory  (in user's language: EN / தமிழ் / हिन्दी)            │ │
 │   │  ├── Summary  ├── Cause  ├── Immediate Actions  └── Prevention       │ │
 │   └──────────────────────────────────────────────────────────────────────┘ │
 │                                                                             │
 │   ┌──────────────────────────────────────────────────────────────────────┐ │
 │   │  Voice Output (gTTS)    │    Voice Input (Groq Whisper STT)          │ │
 │   └──────────────────────────────────────────────────────────────────────┘ │
 └─────────────────────────────────────────────────────────────────────────────┘


 ┌─────────────────────────────────────────────────────────────────────────────┐
 │               OPTIONAL: METADATA FUSION CLASSIFIER  (not wired to UI)      │
 │                                                                             │
 │   Image features (512) ──────────────────────────────────────┐            │
 │                                                               ├─ Concat    │
 │   Variety (e.g. ADT45) → Embedding(16) → LayerNorm ──────────┤            │
 │                                                               │            │
 │   Age (days) → Linear → ReLU → Dropout → Linear → (16) ──────┘            │
 │                                                               │            │
 │                     BatchNorm(544) → Linear(256) → ReLU → Dropout         │
 │                                    → Linear(128) → ReLU → Dropout         │
 │                                    → Linear(10)  → logits                 │
 └─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. End-to-End Data Flow

```
Farmer uploads JPG/PNG
       ↓
Resize to 224×224, ImageNet normalize
       ↓
ResNet-18 → FC(256) → FC(10) → softmax probabilities
       ↓
Top prediction + confidence score
       ↓
Grad-CAM: heatmap on last residual block → overlay on image
       ↓
Weather risk: OpenMeteo API for selected TN district → disease-specific rules
       ↓
Groq Llama-3.1-8b-instant: structured advice (summary/cause/action/prevention)
       ↓  (fallback: static KB if API fails)
Streamlit renders results in user's chosen language (EN / Tamil / Hindi)
```

---

## 3. Complete File Structure

```
AgriShield-TN/
├── app/                              ← Streamlit frontend
│   ├── streamlit_app.py              ← Entry point, multi-page nav (42 lines)
│   ├── _shared.py                    ← Full CSS design system + UI components (800+ lines)
│   ├── pages/
│   │   ├── 1_Home.py                 ← Hero landing page, farmer animations (350+ lines)
│   │   ├── 2_Analyze_Leaf.py         ← Main diagnosis interface (300+ lines)
│   │   ├── 3_What_To_Do.py           ← Treatment / action plan
│   │   ├── 3_How_It_Works.py         ← System explainer
│   │   ├── 4_Impact.py               ← Statistics & impact metrics
│   │   ├── 5_Future_Scope.py         ← Roadmap
│   │   └── 6_Disease_Library.py      ← Disease encyclopedia
│   ├── i18n/
│   │   ├── translations.py           ← 600+ strings (EN / Tamil / Hindi)
│   │   ├── lang_utils.py             ← t() lookup, fallback logic, session lang
│   │   └── __init__.py
│   ├── utils/
│   │   ├── voice_utils.py            ← gTTS TTS + Groq Whisper STT (73 lines)
│   │   └── __init__.py
│   ├── assets/
│   │   └── farmer_ai.png             ← Farmer illustration (base64-embedded)
│   └── .streamlit/
│       └── config.toml               ← Dark green Streamlit theme
│
├── src/                              ← Core ML pipeline
│   ├── config/
│   │   └── config.py                 ← IMAGE_SIZE=224, BATCH=16, LR=1e-4, 10 classes
│   ├── datasets/
│   │   ├── image_dataset.py          ← PyTorch Dataset (class-folder layout)
│   │   ├── metadata_dataset.py       ← Dataset with variety + age columns
│   │   ├── transforms.py             ← Albumentations augmentations
│   │   └── test_dataset_loading.py   ← Dataset validation script
│   ├── models/
│   │   ├── disease_classifier.py     ← ResNet-18 → FC(256) → FC(10)
│   │   ├── image_encoder.py          ← ResNet-18 backbone (512-dim output)
│   │   ├── metadata_encoder.py       ← Variety embedding + Age MLP (32-dim)
│   │   └── metadata_classifier.py    ← Fused image + metadata classifier
│   ├── training/
│   │   ├── train_classifier.py       ← 10-epoch training loop, Adam, checkpoint save
│   │   ├── train_metadata_classifier.py
│   │   └── evaluate.py               ← Accuracy, F1, confusion matrix → JSON
│   ├── inference/
│   │   ├── predict.py                ← Single / batch image inference (91 lines)
│   │   └── explain.py                ← Grad-CAM + ExplanationResult dataclass (582 lines)
│   ├── llm/
│   │   ├── groq_client.py            ← Groq API wrapper + Whisper transcription (137 lines)
│   │   └── agri_insight.py           ← LLM prompting + static fallback KB (396 lines)
│   └── utils/
│       ├── weather.py                ← OpenMeteo API + 38 TN district coords (150+ lines)
│       ├── metrics.py                ← Precision / recall / F1 / confusion matrix
│       └── visualization.py          ← Top-k prediction formatters
│
├── data/
│   └── raw/
│       ├── train.csv                 ← 10,407 rows: image_id, label, variety, age
│       ├── sample_submission.csv     ← 3,469 test rows
│       ├── train_images/             ← One folder per disease class
│       └── test_images/              ← Test set images
│
├── checkpoints/
│   └── best_disease_classifier.pth   ← 44 MB trained ResNet-18
│
├── outputs/
│   ├── evaluation_metrics.json
│   └── classification_report.json
│
├── .streamlit/
│   └── config.toml                   ← Top-level Streamlit config (dark theme)
│
├── .env                              ← GROQ_API_KEY (see Security section)
├── requirements.txt                  ← 69 packages
├── run_app.py                        ← Launcher that uses venv Streamlit
├── fix_indent.py                     ← Indentation cleanup utility
├── rewrite_diagnose.py               ← Page rewrite script
├── rewrite_diagnose_2.py             ← Page refactoring script
└── README.md
```

---

## 4. Disease Classes (10 total)

| # | Class Name |
|---|---|
| 1 | `bacterial_leaf_blight` |
| 2 | `bacterial_leaf_streak` |
| 3 | `bacterial_panicle_blight` |
| 4 | `blast` |
| 5 | `brown_spot` |
| 6 | `dead_heart` |
| 7 | `downy_mildew` |
| 8 | `hispa` |
| 9 | `normal` |
| 10 | `tungro` |

---

## 5. Model Architecture

### Image-only Classifier (deployed in UI)
```
Input image (224 × 224 × 3)
       ↓
ResNet-18 backbone (ImageNet pretrained) → 512-dim feature vector
       ↓
Linear(512 → 256) → ReLU → Dropout(0.3)
       ↓
Linear(256 → 10) → logits → softmax
```

### Metadata Fusion Classifier (built, not yet wired to UI)
```
Image features (512) ─────────────────────┐
                                           ├─ Concat → BatchNorm
Variety embedding (16) ─┐                 │
                         ├─ MLP → (32) ───┘
Age MLP (16) ───────────┘

→ Linear(256) → ReLU → Dropout
→ Linear(128) → ReLU → Dropout
→ Linear(10)  → logits
```

### Grad-CAM Explainability
- **Target layer:** Last residual block of ResNet-18
- **Output:** Pixel-level heatmap overlaid on original image
- **Confidence tiers:**
  - High ≥ 70% → reliable diagnosis language
  - Medium 40–70% → hedged language
  - Low < 40% → uncertainty warning
- **Urgency levels:** CRITICAL / HIGH / MODERATE / LOW

---

## 6. Training Configuration

| Parameter | Value |
|---|---|
| Image size | 224 × 224 |
| Batch size | 16 |
| Learning rate | 1e-4 |
| Optimizer | Adam |
| Epochs | 10 |
| Random seed | 42 |
| Train/Val split | 80 / 20 (stratified) |
| Loss function | CrossEntropyLoss |
| Device | Auto CUDA / CPU |
| Checkpoint path | `checkpoints/best_disease_classifier.pth` |

### Data Augmentations (Albumentations)
- **Training:** HorizontalFlip, VerticalFlip, Rotate(±20°), RandomBrightnessContrast
- **Validation:** Resize only
- **Normalization:** ImageNet standard — mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]

---

## 7. Dataset

| Property | Value |
|---|---|
| Training images | 10,407 |
| Test images | 3,469 |
| Classes | 10 |
| Image format | JPG, variable resolution → preprocessed to 224×224 |
| Metadata columns | `image_id`, `label`, `variety` (e.g. ADT45, TRY2), `age` (days after transplanting, 45–120) |
| Folder layout | `train_images/<disease_class>/<image_id>.jpg` |

---

## 8. External APIs

| API | Purpose | Auth |
|---|---|---|
| Groq (`llama-3.1-8b-instant`) | Advisory text generation (EN/TA/HI) | `GROQ_API_KEY` |
| Groq (`whisper-large-v3-turbo`) | Voice-to-text transcription | Same key |
| OpenMeteo | Real-time weather + 3-day forecast | None (free) |
| gTTS (Google) | Text-to-speech synthesis | None (free) |

### Weather Integration Detail
- Covers **38 Tamil Nadu districts** with pre-configured lat/lon coordinates
- Fetches current conditions + 3-day forecast from OpenMeteo
- Disease-specific risk rules (humidity thresholds, rain/heat/cold impact)
- Output: **HIGH / MEDIUM / LOW** risk + contextual note per disease

### LLM Advisory Detail
- Temperature: 0.4 (consistent, low variance)
- Confidence-tier-aware prompting (prompt changes based on high/medium/low)
- Language-aware system instructions (output in EN/TA/HI as requested)
- Fallback: static knowledge base responses if API unavailable
- Output parsed as structured JSON: `summary`, `cause`, `action`, `prevention`, `immediate_actions`

---

## 9. Multilingual System

| Language | Code | Display |
|---|---|---|
| English | `en` | English |
| Tamil | `ta` | தமிழ் |
| Hindi | `hi` | हिन्दी |

- **600+ translation keys** in `app/i18n/translations.py`
- Structure: `TRANSLATIONS[lang_code][section][key]`
- Sections: `nav`, `home`, `diagnose`, `weather`, `severity`, `disease_lib`, `common`
- Lookup: `t("section.key")` → falls back to English if key missing in target lang
- Language persisted in `st.session_state` across all pages
- Fonts: **Noto Sans Tamil** + **Noto Sans Devanagari** loaded via CSS

---

## 10. Frontend Pages

### `1_Home.py` — Landing Page
- Full-screen hero with animated badge, title, subtitle
- 3-step flow pills: 📷 Detect → 🧠 Analyze → ⚡ Act
- 6 feature pills (Disease Detection, Actions, Weather, Groq, Grad-CAM, AI Advisory)
- 5 capability cards in grid (color-coded: green, red, blue, teal, purple)
- Disease examples: 3 common diseases with severity levels
- 3 user personas: small farmers, field officers, students
- Impact metrics: annual crop loss, % small farmers, diagnosis time, districts covered
- Farmer walk animation: CSS-animated farmer, swaying grass, flying birds, fireflies
- Language selector in sidebar (EN / தமிழ் / हिन्दी)

### `2_Analyze_Leaf.py` — Main Diagnosis Interface
- Welcome badge: "🤖 AGRISHIELD-TN · AI CROP DOCTOR"
- Step tracker: Upload → District → Diagnose
- Two-column layout: left (upload/preview), right (district/results)
- File uploader: JPG/PNG, preview with filename badge
- Example leaf photos (diseased, affected, healthy)
- District dropdown: 38 TN districts
- Results (post-analysis):
  - Disease name + confidence %
  - Grad-CAM heatmap overlay
  - Top 3 alternative predictions
  - Weather risk card
  - Groq AI advisory text
  - Immediate action checklist
  - Severity badge + urgency framing
- Voice: gTTS playback + Groq Whisper voice input

### `3_What_To_Do.py` — Action Plan
- Disease-specific treatment steps
- Urgency-framed instructions

### `6_Disease_Library.py` — Encyclopedia
- Reference cards for all 10 diseases
- Cause, symptoms, spread, treatment per disease

### `3_How_It_Works.py`, `4_Impact.py`, `5_Future_Scope.py`
- System explanation, statistics, roadmap

---

## 11. Design System (`app/_shared.py`)

### Color Tokens
```css
primaryColor:   #22c55e   (green)
background:     #0f1f12   (very dark green)
secondaryBg:    #0B1A0D
text:           #ffffff
```

### Animations Defined
- `fadeUp`, `fadeIn`, `float`, `pulse`, `shimmer`, `scan`, `glow`
- `heroBadge`, `heroTitle`, `heroSub`, `heroFlow`, `heroCta`
- `farmerWalk`, `grassSway`, `birdFly`, `firefly`

### UI Components
| Function | Purpose |
|---|---|
| `inject_css()` | Embeds full stylesheet |
| `inject_header()` | Custom navigation bar |
| `inject_sidebar_brand()` | Logo + nav links in sidebar |
| `ui_footer()` | Footer section |
| `ui_divider()` | Visual separator |
| `ui_error()` | Styled error message |
| `draw_scan()` | Animated scan effect on images |

---

## 12. Voice Interface (`app/utils/voice_utils.py`)

| Function | Description |
|---|---|
| `generate_speech(text, lang)` | gTTS TTS → base64 audio |
| `autoplay_audio(audio_base64)` | HTML5 audio player with autoplay |
| `stop_audio()` | JavaScript to stop all audio |
| `transcribe_audio(audio_bytes, lang_key)` | Groq Whisper transcription |

---

## 13. Key Source File Summaries

### `src/inference/explain.py` (582 lines)
Central explainability engine. Runs Grad-CAM, builds `ExplanationResult` dataclass with:
`predicted_class`, `display_name`, `confidence_pct`, `headline`, `short_desc`, `cause`, `spread`, `symptoms`, `treatment`, `urgency_label`, `reliability`, `cam_note`, `action_urgency`

### `src/llm/agri_insight.py` (396 lines)
Groq LLM integration. Builds language-aware, confidence-tier-aware prompts. Parses JSON response into `AgriInsight` dataclass. Falls back to hardcoded static KB for all 10 diseases × 3 languages if API is unavailable.

### `src/utils/weather.py` (150+ lines)
OpenMeteo integration. Contains coordinate map for 38 TN districts. Disease-specific risk rules (e.g., Blast → HIGH if humidity >80% + cold + rain forecast). Returns structured risk object.

### `src/llm/groq_client.py` (137 lines)
Groq API wrapper. Loads key from `.env` or environment. Model: `llama-3.1-8b-instant`, temperature: 0.4. Whisper transcription supports EN/TA/HI. Single cached client instance. Never raises — always returns None on failure.

### `app/_shared.py` (800+ lines)
Complete CSS design system, all animation keyframes, and all reusable Streamlit UI component functions.

### `app/i18n/translations.py` (600+ lines)
Full translation dictionary for EN/TA/HI across all pages and all UI sections.

---

## 14. Configuration Files

### `.env`
```
GROQ_API_KEY=<api_key_here>
```

### `.streamlit/config.toml`
```toml
[theme]
base                     = "dark"
primaryColor             = "#22c55e"
backgroundColor          = "#0f1f12"
secondaryBackgroundColor = "#0B1A0D"
textColor                = "#ffffff"
font                     = "sans serif"
```

### `.gitignore` (key entries)
```
__pycache__/
*.pyc
venv/
.env
data/raw/train_images/
data/raw/test_images/
checkpoints/
outputs/
```

---

## 15. Dependencies (requirements.txt — 69 packages)

### Core ML/DL
| Package | Version |
|---|---|
| torch | 2.11.0 |
| torchvision | 0.26.0 |
| numpy | 2.4.4 |
| pandas | 3.0.2 |
| scikit-learn | 1.8.0 |
| opencv-python | 4.13.0.92 |
| albumentations | 2.0.8 |
| pillow | 12.2.0 |
| tqdm | 4.67.3 |

### Streamlit & Web
| Package | Version |
|---|---|
| streamlit | 1.56.0 |
| altair | 6.0.0 |
| tornado | 6.5.5 |
| pydeck | 0.9.1 |
| watchdog | 6.0.0 |
| protobuf | 7.34.1 |

### LLM & APIs
| Package | Version |
|---|---|
| groq | >=0.9.0 |
| gTTS | >=2.3.1 |

### Config & Utilities
| Package | Version |
|---|---|
| python-dotenv | >=1.0.0 |
| pyyaml | 6.0.3 |
| tenacity | 9.1.4 |
| requests | 2.33.1 |
| certifi | 2026.2.25 |
| python-dateutil | 2.9.0.post0 |

---

## 16. Running the App

```bash
# Recommended (uses venv Streamlit)
python run_app.py

# Direct
streamlit run app/streamlit_app.py

# Using venv binary explicitly
.\venv\Scripts\streamlit.exe run app/streamlit_app.py
```

### Training & Evaluation
```bash
# Verify dataset loads correctly
python -m src.datasets.test_dataset_loading

# Train model (saves to checkpoints/)
python -m src.training.train_classifier

# Evaluate trained model
python -m src.training.evaluate

# Run inference on a single image
python -m src.inference.predict
```

---

## 17. Git History (Recent Commits)

| Hash | Message |
|---|---|
| `17fcd9b` | updated frontend |
| `23de43d` | Add run_app.py launcher that always uses venv Streamlit |
| `976b23c` | Move language selector into sidebar to restore multilingual feature |
| `dad4c67` | Remove inject_header() from app entry point to preserve full-screen hero layout |
| `7b010da` | Enhance README with multilingual features and updates |
| `890149b` | Added multilingual system |
| `dcc0200` | Update README with alternative Streamlit run command |
| `ef17d6b` | updated frontend and backend |
| `0a8407a` | Initial setup: dataset pipeline + training + inference |

---

## 18. Current Git Status (as of session start)

Files with uncommitted changes:
- `app/_shared.py` (modified, staged)
- `app/pages/2_Analyze_Leaf.py` (modified, unstaged)
- `requirements.txt` (modified, unstaged)
- `src/llm/groq_client.py` (modified, unstaged)
- `app/utils/` (entire folder untracked — voice_utils.py not yet staged)

---

## 19. Project Summary Table

| Aspect | Details |
|---|---|
| Project type | AI-powered crop health diagnosis |
| Target users | Paddy farmers in Tamil Nadu, India |
| Core model | ResNet-18 CNN (10-class disease classifier) |
| Model file size | 44 MB |
| Inference speed | < 1 second per image (CPU) |
| Main frameworks | PyTorch, Streamlit |
| External APIs | Groq (LLM + STT), OpenMeteo (weather) |
| Languages supported | English, Tamil, Hindi |
| Translation strings | 600+ |
| Training samples | 10,407 images |
| Test samples | 3,469 images |
| Disease classes | 10 |
| TN districts covered | 38 |
| Total Python files | ~40 |
| Approx. Python LOC | 3,000+ |

---

## 20. Known Issues & Gaps

1. **API key in `.env` is committed to git** — `GROQ_API_KEY` visible in repo history; should use environment secrets or GitHub Secrets.
2. **Metadata classifier not wired to UI** — fusion model is built and trained but `2_Analyze_Leaf.py` only uses the image-only classifier.
3. **No unit tests** — only `src/datasets/test_dataset_loading.py` for dataset validation; no pytest suite.
4. **`app/utils/` is untracked** — `voice_utils.py` exists on disk but has never been `git add`-ed.
5. **Mobile optimization incomplete** — CSS/JS is partially responsive; dedicated mobile breakpoints not fully implemented.
6. **Only 3 languages** — no Telugu, Kannada, or Marathi support despite large farming populations speaking those.
7. **Dataset balance unverified** — 10,407 images assumed balanced across 10 classes; no explicit check in code.

---

## 21. Detailed File-by-File Explanation

---

### `run_app.py`

This is the **launch script**. It uses Python's `pathlib` to find `venv/Scripts/streamlit.exe` inside the project folder, then calls `subprocess.run()` to start Streamlit on `app/streamlit_app.py` with the working directory set to the project root. If the venv doesn't exist, it exits immediately with an error message telling you to create it. This exists because running `streamlit run` globally might pick the wrong Streamlit version — this guarantees the correct one from the project's own virtual environment.

---

### `src/config/config.py`

This is the **single source of truth** for every hardcoded value in the project. On import it does two things: builds all `Path` objects (project root → data dirs → checkpoint dir → output dir) and calls `.mkdir(parents=True, exist_ok=True)` on the output directories so training scripts never crash with "directory not found". It stores image size (224), batch size (16), learning rate (1e-4), epochs (10), the 10 class names in their exact integer order (changing this order would break existing saved checkpoints), and builds two dicts — `CLASS_TO_IDX` and `IDX_TO_CLASS` — that translate between string labels and integer indices. Every other file imports from here instead of duplicating values.

---

### `src/datasets/transforms.py`

Defines two Albumentations pipelines. `get_train_transforms()` chains: resize to 224×224 → random horizontal flip (50%) → random vertical flip (20%) → random rotation ±20° (50%) → random brightness/contrast (50%) → ImageNet normalisation → convert numpy HWC to PyTorch CHW tensor. `get_val_transforms()` skips all random operations — just resize, normalise, and convert. The reason there are two is that augmentation must only happen during training. At validation time you need deterministic results so metrics are comparable across epochs.

---

### `src/datasets/image_dataset.py`

This is a standard PyTorch `Dataset` subclass. The `__init__` reads `train.csv` into a pandas DataFrame, checks that all 4 required columns exist, drops rows with missing image IDs or labels, then checks for any label strings that aren't in `CLASS_NAMES` (catching typos early). `__len__` returns the row count. `_resolve_image_path()` handles the folder layout — since images live at `train_images/<label>/<image_id>.jpg`, it concatenates the path and tries 4 possible extensions in case the file was saved as `.JPG` or `.jpeg`. `__getitem__` is called by the DataLoader for each sample: it reads the row, loads the image with OpenCV (which reads BGR), converts to RGB, runs the Albumentations transform if provided, converts the string label to an integer via `CLASS_TO_IDX`, and returns a 3-tuple: `(image_tensor, label_tensor, metadata_dict)`. The metadata dict carries the raw string values (image_id, label name, variety, age, path) so callers can inspect or log them.

---

### `src/datasets/metadata_dataset.py`

Inherits from `PaddyImageDataset` and adds two extra output tensors per sample. In `__init__` it first calls `super().__init__()` to get all the base dataset behaviour, then builds a `variety_to_idx` vocabulary by taking all unique variety strings, sorting them alphabetically, and assigning integer indices. It computes `age_mean` and `age_std` from the loaded data (or uses externally passed values — important so validation uses the same statistics as training, preventing data leakage). `_variety_idx()` looks up a variety string and returns 0 for any unknown variety. `_normalize_age()` applies z-score normalisation: `(age - mean) / std`. `__getitem__` calls the parent's `__getitem__` first to get the image/label/metadata, then wraps variety and age into two additional tensors. The return is a 5-tuple: `(image, variety_idx, age_norm, label, metadata)`.

---

### `src/datasets/test_dataset_loading.py`

A manual verification script. It builds `PaddyImageDataset` with training transforms, prints the total sample count, loads sample index 0 and prints the image shape/label/metadata, then creates a `DataLoader` with batch_size=4 and prints the shape of one batch. Run it after any dataset changes to confirm loading still works before starting a full training run.

---

### `src/models/image_encoder.py`

Loads ResNet-18 from `torchvision` with ImageNet pretrained weights. Then it strips the final 1000-class fully-connected layer using `nn.Sequential(*list(backbone.children())[:-1])` — this keeps everything from the initial convolution through to the global average pooling layer. The result is a module that takes a `[B, 3, 224, 224]` image tensor and outputs `[B, 512, 1, 1]` from the last residual block's average pool. The `forward()` method flattens this to `[B, 512]`. The `output_dim = 512` attribute is stored so downstream modules (classifier head, metadata classifier) can read it programmatically instead of hardcoding 512.

---

### `src/models/disease_classifier.py`

Builds the full image-only classifier by composing two modules. It instantiates `ImageEncoder` (ResNet-18 backbone, 512-dim output) then builds a two-layer MLP classifier head: `Linear(512→256) → ReLU → Dropout(0.3) → Linear(256→10)`. The `forward()` method passes the image through the encoder to get a 512-dim vector, then through the head to get 10 raw logits. Softmax is NOT applied here — `CrossEntropyLoss` in the training script handles that internally. This is the model saved to `best_disease_classifier.pth` and loaded by the Streamlit UI.

---

### `src/models/metadata_encoder.py`

Encodes two metadata fields into a 32-dim vector.

**Variety branch**: takes a `LongTensor` of variety indices → `nn.Embedding` (learnable lookup table) → `LayerNorm` (stabilises gradients when the vocabulary is small and embeddings are randomly initialised). Output: `[B, 16]`.

**Age branch**: takes a `FloatTensor` of z-score ages → unsqueeze to `[B, 1]` → `Linear(1→32) → ReLU → Dropout(0.2) → Linear(32→16) → ReLU`. Output: `[B, 16]`.

Both outputs are concatenated to produce `[B, 32]`. The `output_dim = 32` attribute is exposed for the fusion classifier to read.

---

### `src/models/metadata_classifier.py`

The fusion model. It holds an `ImageEncoder` and a `MetadataEncoder` as sub-modules. In `forward()` it runs the image through the image encoder (→ `[B, 512]`), runs variety + age through the metadata encoder (→ `[B, 32]`), then `torch.cat` concatenates them into `[B, 544]`. This is fed into a fusion classifier: `BatchNorm1d(544)` (bridges the scale gap between 512-dim image features and 32-dim metadata features so neither branch dominates) → `Linear(544→256) → ReLU → Dropout(0.3)` → `Linear(256→128) → ReLU → Dropout(0.15)` → `Linear(128→10)`. This model is fully implemented and trainable but **not yet connected to the Streamlit UI**, which still uses the image-only classifier.

---

### `src/training/train_classifier.py`

The complete training loop.

- `set_seed()` fixes all random generators (Python `random`, NumPy, PyTorch CPU and CUDA) for reproducibility.
- `get_device()` picks CUDA if available, otherwise CPU.
- `create_dataloaders()` loads the full dataset once (no transform) just to get the label list for stratified splitting, calls `train_test_split` with `stratify=labels` to maintain class distribution, then creates **two separate dataset objects** (one with train augmentations, one with val transforms) and wraps each with `Subset` using the split indices.
- `train_one_epoch()` sets `model.train()`, iterates batches with a tqdm progress bar, runs forward pass → CrossEntropyLoss → `.backward()` → Adam `.step()`, accumulates running loss and accuracy.
- `validate_one_epoch()` is decorated with `@torch.no_grad()` (no gradient graph built, faster + less memory) and sets `model.eval()` (disables Dropout, fixes BatchNorm statistics).
- `main()` runs for `NUM_EPOCHS`, and whenever `val_acc` improves over the previous best, saves a `deepcopy` of the model state dict to `checkpoints/best_disease_classifier.pth`. `deepcopy` ensures it stores a snapshot rather than a reference to the live model.

---

### `src/training/evaluate.py`

Loads the saved checkpoint, runs the full validation set through the model, and computes per-class precision, recall, F1, overall accuracy, and a confusion matrix using scikit-learn. Results are exported as JSON to `outputs/evaluation_metrics.json` and `outputs/classification_report.json`. Also generates Grad-CAM visualisations for a sample of correctly and incorrectly classified images.

---

### `src/inference/predict.py`

Standalone inference for a single image.

- `load_model()` builds a `PaddyDiseaseClassifier` with `pretrained=False` (random weights) then loads the saved checkpoint via `torch.load`, overwriting those weights with the trained values. The model is set to `eval()` mode.
- `preprocess_image()` reads the image with OpenCV, converts BGR→RGB, and applies `get_val_transforms()` (resize + normalise) then unsqueezes to add a batch dimension: `[1, 3, 224, 224]`.
- `predict_image()` (decorated with `@torch.no_grad()`) runs the tensor through the model, applies softmax to the logits, finds the argmax for the predicted class, and returns a 3-tuple: the class name string, the confidence float (0–1), and a dict of all 10 class probabilities.

---

### `src/inference/explain.py`

The most complex inference file — it does two jobs.

**Grad-CAM**: The `GradCAM` class registers two PyTorch hooks on the target layer (ResNet-18's last residual block, `model.encoder.feature_extractor[-1]`). A forward hook saves the layer's activation map `[C, H, W]` during the forward pass. A backward hook saves the gradients `[C, H, W]` during backpropagation. When `generate()` is called, it runs the forward pass, calls `.backward()` on the target class's output score, then computes a weighted sum: for each channel, the gradient's spatial mean becomes the channel's weight, multiplied by the activation map and summed across all channels. `ReLU` zeros out negative values, the result is normalised to 0–1, resized to 224×224, colourised with `cv2.COLORMAP_JET`, and blended onto the original image with `cv2.addWeighted`.

**Explanation engine**: `_DISEASE_KB` is a hardcoded dictionary with clinical data for all 10 diseases — display name, short description, symptoms list, cause, spread route, treatment steps, urgency level, and typical Grad-CAM focus region. `_TIER_LANGUAGE` defines 3 sets of text fragments for high/medium/low confidence. `generate_explanation()` looks up the disease in the KB, determines the confidence tier, then assembles an `ExplanationResult` dataclass with every field populated — headline, reliability sentence, urgency badge, Grad-CAM note, action urgency. The public `generate_gradcam_with_explanation()` function runs both and returns everything in one call.

---

### `src/llm/groq_client.py`

A thin wrapper around the Groq Python SDK. On module load it calls `_load_dotenv()` which walks up the directory tree looking for a `.env` file and loads it via `python-dotenv` (silently skips if not installed). `_get_client()` is called once and caches the `Groq` client in a module-level variable — if `GROQ_API_KEY` is missing, or the `groq` package isn't installed, or instantiation fails, it returns `None` and logs a warning rather than raising. `call_groq()` takes a user prompt and system prompt, calls `client.chat.completions.create()` with `llama-3.1-8b-instant` at temperature 0.4, and returns the content string — or `None` on any exception. `transcribe_audio()` sends raw audio bytes to the Groq Whisper endpoint with an optional language hint and returns the transcription string. Both functions are entirely exception-safe: they catch everything and return `None` so callers never need try/except.

---

### `src/llm/agri_insight.py`

The agricultural advisory generator.

- `_tier()` buckets confidence into high (≥70%), medium (40–70%), or low (<40%).
- `_build_prompt()` constructs a structured prompt with the disease name, confidence percentage, a tier-specific instruction ("be direct" vs "recommend verification" vs "strongly uncertain"), and asks Groq to return a specific JSON object with 6 required keys.
- `_LANG_INSTRUCTION` adds a language directive to the system prompt so Groq responds in Tamil or Hindi when requested.
- `_parse_response()` strips markdown fences from the response, tries `json.loads()` directly, and if that fails tries extracting the first `{...}` block with a regex.
- `_FALLBACK` is a complete static knowledge base with pre-written answers for all 10 diseases (including `immediate_actions` checklists) used when Groq is unavailable.
- `generate_agri_insight()` tries the full Groq path, and if `call_groq()` returns `None` or parsing fails, silently calls `_make_fallback()` instead. It always returns an `AgriInsight` dataclass — never raises.

---

### `src/utils/weather.py`

- `DISTRICTS` maps all 38 Tamil Nadu district names to their GPS coordinates (lat, lon).
- `_DISEASE_RISK_RULES` defines disease-specific weather sensitivity for each of the 10 classes — e.g., Blast is sensitive to humidity >80% AND cool temperatures AND rain; Tungro (leafhopper-spread) is sensitive to heat but not rain.
- `_fetch_weather()` builds an OpenMeteo API URL with the district's lat/lon requesting current temperature, humidity, and precipitation plus 3-day daily forecasts, calls `urllib.request.urlopen()` with a 5-second timeout, and parses the JSON response.
- `_compute_risk()` extracts humidity, temperature, current rain, and 3-day rain total, increments a `risk_score` based on which rules apply for the current disease, and returns "HIGH" (score ≥4), "MODERATE" (≥2), or "LOW" (below 2) along with a list of human-readable reasons.
- `get_weather_risk()` is the public function — looks up the district coordinates, fetches weather, computes risk, and returns a flat dict with all weather values plus risk level, label, reasons, and disease-specific note.

---

### `src/utils/visualization.py`

Three pure utility functions used by the Streamlit UI:

- `get_top_k_predictions()` — sorts a `{class_name: probability}` dict by probability descending and returns the top k as a list of `(name, prob)` tuples.
- `format_class_name()` — converts `"bacterial_leaf_blight"` → `"Bacterial Leaf Blight"` via `.replace("_", " ").title()`.
- `format_percentage()` — converts `0.9234` → `"92.34%"`.
- `prepare_prediction_rows()` — combines all three to return display-ready dicts like `{"class_name": "Blast", "probability": "91.24%"}` for the results table.

---

### `app/streamlit_app.py`

The Streamlit entry point. It inserts both the project root and the `app/` folder into `sys.path` so imports work from either directory. Calls `st.set_page_config()` to set the browser tab title, icon, wide layout, and expanded sidebar. Calls `st.navigation()` to register 4 pages (Home, Diagnose, Action Plan, Field Guide) with `position="hidden"` so Streamlit's built-in sidebar nav is suppressed — navigation is handled by custom HTML links instead. Then `inject_css()`, `inject_header()`, `inject_theme()`, and `inject_sidebar_brand()` from `_shared.py` inject the full design system into every page. Finally `pg.run()` renders whichever page is currently active.

---

### `app/_shared.py`

The **entire design system** for the app in one file. It defines a large `_CSS` string (~2000 lines) containing:

- **CSS custom properties** — colour tokens (green-50 through green-950, text greys, shadows, border radii, transition curves)
- **Keyframe animations** — `fadeUp`, `fadeIn`, `float`, `pulse`, `shimmer`, `scan`, `glow`, `heroBadge`, `heroTitle`, `heroSub`, `farmerWalk`, `grassSway`, `birdFly`, `firefly`
- **Component styles** — hero section, nav header, sidebar brand, diagnosis page cards, result cards, weather cards, voice panel, action cards, disease library cards, footer

Beyond CSS, it exports these Python functions:
| Function | What it does |
|---|---|
| `inject_css()` | Dumps `_CSS` into a `<style>` tag via `st.markdown(unsafe_allow_html=True)` |
| `inject_header()` | Renders the sticky navigation bar using `st.page_link` buttons |
| `inject_sidebar_brand()` | Renders the green logo + nav links inside the Streamlit sidebar |
| `inject_theme()` | Additional runtime theme overrides |
| `ui_footer()` | Renders the page footer HTML |
| `ui_divider()` | Renders a styled horizontal separator |
| `ui_error(msg)` | Renders a styled red error card |
| `draw_scan(image)` | Overlays an animated scan line effect on a Grad-CAM result image |

---

### `app/pages/1_Home.py`

The **full-screen landing page**. On load it injects CSS to strip all Streamlit padding and hide the sidebar so the hero occupies 100% viewport height. The hero is built entirely with `st.markdown(unsafe_allow_html=True)` — it stacks: background div (rice field photo via CSS `background-image`), overlay gradient, radial highlight, vignette, 3 animated floating orbs, 3 animated flying birds (emoji with CSS animation), the inner content (badge, split title "Agri🌾Shield-TN", subtitle, 3-step flow pills, 6 feature pills), and a rice-field bottom strip with 56 animated grass stalks and 2 walking farmer emojis.

Below the hero it renders:
- **Capabilities grid** — 5 colour-coded cards (Disease Detection, Action Plan, Weather, Groq AI, Grad-CAM)
- **Disease preview** — 3 example diseases with severity badges
- **Built for farmers** — 3 persona cards (small farmers, field officers, students)
- **How it works** — 4-step timeline
- **Impact stats** — 4 numbers (annual crop loss, % small farmers, diagnosis time, districts covered)

All user-facing text goes through `t("key")` so it renders in the selected language.

---

### `app/pages/2_Analyze_Leaf.py`

The **main diagnosis interface** and the most complex page (1010 lines). It initialises 5 session state keys on first load. It defines `_get_live_weather()` cached for 10 minutes to avoid hammering OpenMeteo. It loads the farmer illustration from `assets/farmer_ai.png` as a base64 data URI for embedding directly in HTML.

The page renders in this order:

1. **Welcome header** — animated badge, "Vanakkam! 👋" greeting, page subtitle from i18n, Tamil subtitle, farmer illustration
2. **Step strip** — 3 numbered steps (Upload → District → Diagnose) with CSS classes that change dynamically based on `st.session_state["_has_upload"]`
3. **Two-column layout** (6:4 split):
   - **Left column**: `st.file_uploader` for JPG/PNG → shows image preview + filename badge on upload, example photo strip (3 Unsplash images), and a tip card. Resets `run_analysis=False` when a new file is uploaded.
   - **Right column**: paddy field banner, status card (pulsing ring "awaiting" / green checkmark "ready"), district selectbox (38 TN districts), model info box, live weather mini-card (4 states: no district selected / success / API failure / loading), voice input panel (`st.audio_input` → Groq Whisper transcription → fuzzy match against district names to auto-select)

4. **Analyse button** — sets `run_analysis=True` in session state when clicked. The analysis block only executes when this flag is True:
   - Saves uploaded file bytes to a `tempfile` on disk
   - Calls `predict_image()` → class name + confidence + all 10 probabilities
   - Calls `generate_gradcam()` → Grad-CAM heatmap overlay as numpy array
   - Calls `generate_agri_insight()` with disease, confidence, and current language code → `AgriInsight` dataclass
   - Calls `get_weather_risk()` with selected district and disease → weather + risk dict
   - Stores `insight` in `st.session_state["diag_insight"]` (so `3_What_To_Do.py` can read it)
   - Renders: disease name badge, confidence bar, Grad-CAM heatmap image, top-3 alternatives table, weather risk card (red/yellow/green), AI advisory block (summary, cause, action, prevention), immediate actions checklist, severity badge

---

### `app/pages/3_What_To_Do.py`

The **action plan page**. First checks if `st.session_state["diag_insight"]` exists — if not, shows "No Diagnosis Found" with a button to go back. If it does exist, reads `insight`, `disease_name`, `sev`, and `pct` from session state.

`_ACTION_MAP` is a list of tuples — each tuple has: a keyword list, icon, CSS badge class, timing label (TODAY/DAILY/AS DIRECTED/IMMEDIATELY etc.), Tamil label, English title, Tamil title, Unsplash photo ID, and a CSS fallback gradient. `_classify_action_full()` scans each action string from `insight.immediate_actions` against these keyword lists and returns the first matching entry.

The **main column** renders large illustrated cards for each action item: full-bleed background photo from Unsplash, coloured urgency badge, icon, bilingual title (English + Tamil).

The **side column** renders an expert advisory panel: a "Why It Happened" banner (first 2 sentences of `insight.cause`), and up to 3 treatment/prevention pills auto-selected by keyword-scanning `insight.prevention + insight.action` text.

---

### `app/pages/6_Disease_Library.py`

A disease encyclopaedia. Defines page-scoped CSS for the card grid. Displays 10 disease cards with background images, severity badges, and disease names. Clicking a card expands a detail panel with full clinical information — symptoms, cause, spread route, and treatment steps from the same `_DISEASE_KB` data used in `explain.py`. A filter row lets users narrow cards by severity level. All text goes through `t()`.

---

### `app/i18n/translations.py`

A nested Python dictionary structured as `TRANSLATIONS[lang_code][section][key] = "string"`. Three top-level keys: `"en"`, `"ta"`, `"hi"`. Inside each language are sections: `nav`, `home`, `diagnose`, `weather`, `severity`, `disease_lib`, `common`. Tamil and Hindi entries use full Unicode strings. This is the only place translations live — no external translation service or file format is used.

---

### `app/i18n/lang_utils.py`

The runtime translation engine.

- `get_lang()` reads `st.session_state["lang"]` (defaults to `"en"`).
- `set_lang(code)` sets the session key and calls `st.rerun()` to immediately re-render the whole app in the new language.
- `t(key)` is the core function: splits a dot-separated key like `"diagnose.page_title"`, walks the `TRANSLATIONS` dict following each segment, and returns the string. If any segment is missing in the target language it falls back to English. If also missing in English it returns the key string itself — so the UI never crashes with a `KeyError`. If `**kwargs` are passed, it formats them into the string via `.format(**kwargs)`.

---

### `app/i18n/__init__.py`

A package init that re-exports `t`, `get_lang`, `set_lang`, and `SUPPORTED_LANGS` from `lang_utils.py`. This means page files can write `from i18n import t, get_lang` instead of `from i18n.lang_utils import ...`.

---

### `app/utils/voice_utils.py`

- `generate_speech(text, lang)` — uses `gTTS` to synthesise speech: creates a `gTTS` object, saves it to a temp `.mp3`, reads bytes back, base64-encodes them, and returns the string. Cached with `@st.cache_data` so the same text isn't re-synthesised on every Streamlit rerender.
- `autoplay_audio(audio_base64)` — injects an HTML5 `<audio autoplay>` tag with the base64 data URI as the source via `st.markdown`.
- `stop_audio()` — injects a JavaScript snippet that loops through all `<audio>` elements in the DOM and pauses them.
- `transcribe_audio(audio_bytes, lang_key)` — imports `groq_client.transcribe_audio` at call time (lazy import), normalises the language code to one of `"en"/"ta"/"hi"`, and returns the transcription string or an error message if Groq fails.

---

### How All Files Connect at Runtime

```
run_app.py
  └─ app/streamlit_app.py
       ├─ app/_shared.py              (CSS + nav injected into every page)
       ├─ app/i18n/lang_utils.py      (t() used on every page)
       │
       ├─ app/pages/1_Home.py
       │    └─ reads t() for all text
       │
       ├─ app/pages/2_Analyze_Leaf.py  ← main data flow
       │    ├─ src/inference/predict.py
       │    │    └─ src/models/disease_classifier.py
       │    │         └─ src/models/image_encoder.py  (ResNet-18)
       │    ├─ src/inference/explain.py
       │    │    ├─ GradCAM (hooks on ResNet-18 last layer)
       │    │    └─ _DISEASE_KB (clinical knowledge base)
       │    ├─ src/utils/weather.py    (OpenMeteo API)
       │    ├─ src/llm/agri_insight.py
       │    │    └─ src/llm/groq_client.py  (Groq LLM API)
       │    └─ app/utils/voice_utils.py
       │         └─ src/llm/groq_client.py  (Groq Whisper STT)
       │
       ├─ app/pages/3_What_To_Do.py
       │    └─ reads st.session_state["diag_insight"] set by 2_Analyze_Leaf.py
       │
       └─ app/pages/6_Disease_Library.py
            └─ static disease reference data
```

**Training-time file connections (offline, not part of the app):**
```
src/training/train_classifier.py
  ├─ src/datasets/image_dataset.py
  │    └─ src/config/config.py
  ├─ src/datasets/transforms.py
  └─ src/models/disease_classifier.py
       └─ src/models/image_encoder.py
            → saves checkpoints/best_disease_classifier.pth
```
