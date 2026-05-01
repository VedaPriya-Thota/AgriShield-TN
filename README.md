
# AgriShield-TN
### AI-Powered Crop Health Diagnosis & Multilingual Decision Support System

---

## Overview

AgriShield-TN is an AI-powered crop health system for paddy (rice) farmers in Tamil Nadu, India. A farmer uploads a leaf photo and receives a disease name, confidence score, visual Grad-CAM heatmap, weather-based risk assessment, and multilingual AI advisory — all served through a Streamlit web app.

**Core vision:** Bridge the gap between agricultural AI and actual farmer adoption via instant, explainable, multilingual crop health diagnostics.

---

## System Architecture

```
Farmer uploads JPG/PNG
       ↓
Resize to 224×224 · ImageNet normalize
       ↓
ResNet-18 → FC(256) → FC(10) → softmax probabilities
       ↓
Top prediction + confidence score + Top-3 alternatives
       ↓
Grad-CAM: heatmap on last residual block → overlay on image
       ↓
Weather risk: OpenMeteo API for selected TN district → disease-specific rules
       ↓
Groq llama-3.1-8b-instant: structured advice (summary / cause / action / prevention)
       ↓  (fallback: static KB if API fails)
Streamlit renders results in user's chosen language (EN / Tamil / Hindi)
```

---

## Features

| Feature | Details |
|---|---|
| Disease detection | 10 paddy disease classes, ResNet-18 backbone |
| Explainability | Grad-CAM heatmap with urgency labels (CRITICAL / HIGH / MODERATE / LOW) |
| Weather risk | Real-time + 3-day forecast for 38 Tamil Nadu districts |
| AI advisory | Groq LLM generates treatment/prevention steps in user's language |
| Multilingual | English, Tamil (தமிழ்), Hindi (हिन्दी) — 600+ translation strings |
| Voice | gTTS text-to-speech output + Groq Whisper voice input |
| Offline fallback | Static knowledge base for all 10 diseases × 3 languages when API unavailable |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Deep learning | PyTorch, Torchvision (ResNet-18) |
| Data / augmentation | Albumentations, OpenCV, NumPy, Pandas |
| Explainability | Grad-CAM (custom hooks on ResNet-18 Layer4) |
| Frontend | Streamlit, custom CSS design system |
| LLM advisory | Groq API (`llama-3.1-8b-instant`, temp=0.4) |
| Voice STT | Groq Whisper (`whisper-large-v3-turbo`) |
| Voice TTS | gTTS (Google Text-to-Speech) |
| Weather | OpenMeteo API (free, no key required) |
| Training utilities | scikit-learn, tqdm |

---

## Disease Classes (10 total)

| # | Class |
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

## Model Architecture

### Image Classifier (deployed in UI)
```
Input image (224 × 224 × 3)
       ↓
ResNet-18 backbone (ImageNet pretrained) → 512-dim feature vector
       ↓
Linear(512 → 256) → ReLU → Dropout(0.3)
       ↓
Linear(256 → 10) → logits → softmax
```
Checkpoint: `checkpoints/best_disease_classifier.pth` (44 MB)

### Metadata Fusion Classifier (built, not yet wired to UI)
```
Image features (512) ─────────────────────┐
                                           ├─ Concat → BatchNorm(544)
Variety embedding (16) ─┐                 │
                         ├─ MLP → (32) ───┘
Age MLP (16) ───────────┘

→ Linear(256) → ReLU → Dropout
→ Linear(128) → ReLU → Dropout
→ Linear(10)  → logits
```

### Grad-CAM
- Target layer: last residual block of ResNet-18
- Output: pixel-level heatmap overlaid on original image
- Confidence tiers: High ≥70% · Medium 40–70% · Low <40%

---

## Training Configuration

| Parameter | Value |
|---|---|
| Image size | 224 × 224 |
| Batch size | 16 |
| Learning rate | 1e-4 |
| Optimizer | Adam |
| Epochs | 10 |
| Loss | CrossEntropyLoss |
| Train/Val split | 80 / 20 (stratified) |
| Device | Auto CUDA / CPU |

**Augmentations (training):** HorizontalFlip, VerticalFlip, Rotate(±20°), RandomBrightnessContrast  
**Normalization:** ImageNet mean=[0.485, 0.456, 0.406] · std=[0.229, 0.224, 0.225]

---

## Dataset

| Property | Value |
|---|---|
| Training images | 10,407 |
| Test images | 3,469 |
| Classes | 10 |
| Metadata columns | `image_id`, `label`, `variety` (e.g. ADT45), `age` (days after transplanting) |
| Folder layout | `train_images/<disease_class>/<image_id>.jpg` |

---

## External APIs

| API | Purpose | Auth |
|---|---|---|
| Groq `llama-3.1-8b-instant` | Advisory text (EN / Tamil / Hindi) | `GROQ_API_KEY` in `.env` |
| Groq `whisper-large-v3-turbo` | Voice-to-text transcription | Same key |
| OpenMeteo | Real-time weather + 3-day forecast | None (free) |
| gTTS | Text-to-speech synthesis | None (free) |

---

## Multilingual System

| Language | Code | Script |
|---|---|---|
| English | `en` | Latin |
| Tamil | `ta` | தமிழ் |
| Hindi | `hi` | हिन्दी |

- 600+ translation keys in `app/i18n/translations.py`
- Structure: `TRANSLATIONS[lang_code][section][key]`
- Lookup: `t("section.key")` falls back to English if key missing
- Language persisted in `st.session_state` across all pages
- Fonts: Noto Sans Tamil + Noto Sans Devanagari loaded via CSS
- Groq responds in the user's selected language for AI advisory

---

## Project Structure

```
AgriShield-TN/
├── app/                              ← Streamlit frontend
│   ├── streamlit_app.py              ← Entry point, multi-page nav
│   ├── _shared.py                    ← Full CSS design system + UI components (800+ lines)
│   ├── pages/
│   │   ├── 1_Home.py                 ← Hero landing page with farmer animations
│   │   ├── 2_Analyze_Leaf.py         ← Main diagnosis interface
│   │   ├── 3_What_To_Do.py           ← Disease-specific action plan
│   │   ├── 3_How_It_Works.py         ← System explainer
│   │   ├── 4_Impact.py               ← Statistics & impact metrics
│   │   ├── 5_Future_Scope.py         ← Roadmap
│   │   └── 6_Disease_Library.py      ← Disease encyclopedia
│   ├── i18n/
│   │   ├── translations.py           ← 600+ strings (EN / Tamil / Hindi)
│   │   └── lang_utils.py             ← t() lookup, fallback logic, session lang
│   └── utils/
│       └── voice_utils.py            ← gTTS TTS + Groq Whisper STT
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
│   │   ├── predict.py                ← Single / batch image inference
│   │   └── explain.py                ← Grad-CAM + ExplanationResult dataclass
│   ├── llm/
│   │   ├── groq_client.py            ← Groq API wrapper + Whisper transcription
│   │   └── agri_insight.py           ← LLM prompting + static fallback KB
│   └── utils/
│       ├── weather.py                ← OpenMeteo API + 38 TN district coordinates
│       ├── metrics.py                ← Precision / recall / F1 / confusion matrix
│       └── visualization.py          ← Top-k prediction formatters
│
├── data/
│   └── raw/
│       ├── train.csv                 ← 10,407 rows: image_id, label, variety, age
│       ├── train_images/             ← One folder per disease class
│       └── test_images/
│
├── checkpoints/
│   └── best_disease_classifier.pth   ← 44 MB trained ResNet-18
│
├── outputs/
│   ├── evaluation_metrics.json
│   └── classification_report.json
│
├── .streamlit/
│   └── config.toml                   ← Dark green Streamlit theme
├── .env                              ← GROQ_API_KEY
├── requirements.txt
└── run_app.py                        ← Launcher that uses venv Streamlit
```

---

## Setup

### 1. Clone

```bash
git clone <your-repo-url>
cd AgriShield-TN
```

### 2. Create & activate virtual environment

```bash
python -m venv venv
```

PowerShell:
```powershell
.\venv\Scripts\Activate.ps1
```

CMD / bash:
```bash
venv\Scripts\activate        # Windows CMD
source venv/bin/activate      # Linux/macOS
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set API key

Create `.env` in the project root:
```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### 5. Place dataset

```
data/raw/
├── train.csv
├── train_images/
└── test_images/
```

---

## Running the App

```bash
# Recommended — uses venv Streamlit automatically
python run_app.py

# Or directly
streamlit run app/streamlit_app.py

# Or with explicit venv binary
.\venv\Scripts\streamlit.exe run app/streamlit_app.py
```

---

## Training & Evaluation

```bash
# Verify dataset loads correctly
python -m src.datasets.test_dataset_loading

# Train model (saves to checkpoints/best_disease_classifier.pth)
python -m src.training.train_classifier

# Evaluate trained model (outputs to outputs/)
python -m src.training.evaluate

# Train metadata fusion model (optional)
python -m src.training.train_metadata_classifier
```

---

## Frontend Pages

| Page | Description |
|---|---|
| `1_Home.py` | Hero landing page — animated farmer, feature cards, impact stats |
| `2_Analyze_Leaf.py` | Main UI — upload, district select, Grad-CAM, AI advisory, voice |
| `3_What_To_Do.py` | Action plan with illustrated treatment cards |
| `3_How_It_Works.py` | Step-by-step system explainer |
| `4_Impact.py` | Statistics and impact metrics |
| `5_Future_Scope.py` | Product roadmap |
| `6_Disease_Library.py` | Encyclopedia for all 10 disease classes |

---

## Future Scope

- More regional languages (Telugu, Kannada, Marathi)
- Voice-first interaction for low-literacy users
- Metadata fusion classifier wired to UI (variety + crop age improves accuracy)
- Offline/PWA mode for areas with poor connectivity
- Disease severity scoring (mild / moderate / severe)
- Mobile app with camera integration
