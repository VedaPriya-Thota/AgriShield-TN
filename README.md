<div align="center">

# 🌾 AgriShield-TN

### AI-Powered Paddy Disease Diagnosis for Tamil Nadu Farmers

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.56-FF4B4B?style=flat&logo=streamlit&logoColor=white)](https://streamlit.io)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.11-EE4C2C?style=flat&logo=pytorch&logoColor=white)](https://pytorch.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA%203-F55036?style=flat)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat)](LICENSE)

*Upload a leaf photo → get a disease name, Grad-CAM heatmap, weather risk, and AI advisory in English, Tamil, or Hindi — in under 2 seconds.*

</div>

---

## What It Does

A farmer photographs a paddy leaf on their phone. AgriShield-TN identifies the disease, highlights the infected region on the image, pulls live weather data for their district, and generates treatment advice in their language — all without needing a trained agronomist on-site.

| Step | What happens |
|---|---|
| 📷 **Upload** | JPG/PNG of a paddy leaf |
| 🧠 **Classify** | ResNet-18 identifies 1 of 10 disease classes with confidence score |
| 🔥 **Explain** | Grad-CAM heatmap shows *where* on the leaf the model focused |
| 🌦 **Risk** | Live weather for the farmer's district flags HIGH/MEDIUM/LOW spread risk |
| 💬 **Advise** | Groq LLaMA 3 generates treatment + prevention steps in EN / தமிழ் / हिन्दी |

---

## Features

- **10 disease classes** — Blast, Brown Spot, Bacterial Leaf Blight, Tungro, Hispa, and 5 more
- **Grad-CAM explainability** — pixel-level heatmap overlaid on the original leaf image
- **Live weather integration** — OpenMeteo API covering all 38 Tamil Nadu districts
- **Multilingual AI advisory** — Groq LLaMA 3.1 responds in the user's chosen language
- **Voice I/O** — gTTS text-to-speech output + Groq Whisper voice input for district selection
- **Offline fallback** — static knowledge base for all 10 diseases × 3 languages when API is down
- **Fully responsive UI** — works on desktop, tablet, and mobile browsers
- **Dark/light theme** — toggleable, persisted in localStorage

---

## Pages

| Page | Description |
|---|---|
| **Home** | Cinematic hero with animated rice field, feature cards, impact stats |
| **Diagnose** | Upload leaf → run full analysis pipeline |
| **Action Plan** | Illustrated treatment cards auto-generated from diagnosis |
| **Field Guide** | Encyclopedia for all 10 disease classes |
| **How It Works** | Step-by-step pipeline explanation |
| **Impact & Future** | Statistics and product roadmap |

---

## Tech Stack

| Layer | Tools |
|---|---|
| Deep learning | PyTorch · Torchvision (ResNet-18) |
| Explainability | Grad-CAM (hooks on ResNet-18 Layer4) |
| Frontend | Streamlit · Custom CSS design system |
| LLM advisory | Groq API — `llama-3.1-8b-instant` |
| Voice STT | Groq Whisper — `whisper-large-v3-turbo` |
| Voice TTS | gTTS (Google Text-to-Speech) |
| Weather | OpenMeteo API (free, no key required) |
| Data / augmentation | Albumentations · OpenCV · Pandas |
| Training utilities | scikit-learn · tqdm |

---

## Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/your-username/AgriShield-TN.git
cd AgriShield-TN
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Windows (CMD)
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Add your Groq API key

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com](https://console.groq.com).

### 5. Place the dataset *(training only — not needed to run the app)*

```
data/raw/
├── train.csv
├── train_images/
└── test_images/
```

### 6. Run the app

```bash
# Recommended — uses venv Streamlit automatically
python run_app.py

# Or directly
streamlit run app/streamlit_app.py
```

Open `http://localhost:8501` in your browser.

---

## Model Architecture

### Image Classifier (deployed in the UI)

```
Input image  (224 × 224 × 3)
      ↓
ResNet-18 backbone — ImageNet pretrained  →  512-dim feature vector
      ↓
Linear(512 → 256) → ReLU → Dropout(0.3)
      ↓
Linear(256 → 10)  → logits → softmax
```

Checkpoint: `checkpoints/best_disease_classifier.pth` (44 MB)

### Grad-CAM

- **Target layer:** last residual block of ResNet-18
- **Output:** pixel-level heatmap blended onto the original image
- **Confidence tiers:** High ≥ 70% · Medium 40–70% · Low < 40%
- **Urgency labels:** CRITICAL · HIGH · MODERATE · LOW

### Metadata Fusion Classifier *(built, not yet wired to UI)*

```
Image features (512) ────────────────────┐
                                         ├─ Concat → BatchNorm(544)
Variety embedding (16) ─┐               │
                         ├─ MLP → (32) ─┘
Age MLP (16) ───────────┘
      ↓
Linear(256) → ReLU → Dropout
Linear(128) → ReLU → Dropout
Linear(10)  → logits
```

---

## Disease Classes

| # | Class | # | Class |
|---|---|---|---|
| 1 | Bacterial Leaf Blight | 6 | Dead Heart |
| 2 | Bacterial Leaf Streak | 7 | Downy Mildew |
| 3 | Bacterial Panicle Blight | 8 | Hispa |
| 4 | Blast | 9 | Normal (healthy) |
| 5 | Brown Spot | 10 | Tungro |

---

## Training

```bash
# Verify the dataset loads correctly
python -m src.datasets.test_dataset_loading

# Train the image classifier (saves to checkpoints/)
python -m src.training.train_classifier

# Evaluate and export metrics to outputs/
python -m src.training.evaluate

# Train the metadata fusion classifier (optional)
python -m src.training.train_metadata_classifier
```

### Training configuration

| Parameter | Value |
|---|---|
| Image size | 224 × 224 |
| Batch size | 16 |
| Learning rate | 1e-4 |
| Optimizer | Adam |
| Epochs | 10 |
| Train / Val split | 80 / 20 (stratified) |
| Loss | CrossEntropyLoss |
| Device | Auto CUDA / CPU |

**Augmentations:** HorizontalFlip · VerticalFlip · Rotate ±20° · RandomBrightnessContrast  
**Normalization:** ImageNet — mean `[0.485, 0.456, 0.406]` · std `[0.229, 0.224, 0.225]`

---

## Dataset

| Property | Value |
|---|---|
| Training images | 10,407 |
| Test images | 3,469 |
| Classes | 10 |
| Metadata | `image_id`, `label`, `variety` (e.g. ADT45), `age` (days after transplanting) |
| Layout | `train_images/<disease_class>/<image_id>.jpg` |

---

## Multilingual System

| Language | Code | Script |
|---|---|---|
| English | `en` | Latin |
| Tamil | `ta` | தமிழ் |
| Hindi | `hi` | हिन्दी |

- 600+ translation keys in `app/i18n/translations.py`
- `t("section.key")` lookup with automatic English fallback
- Language persisted in `st.session_state` across all pages
- Fonts: Noto Sans Tamil + Noto Sans Devanagari via CSS
- Groq responds in the selected language for AI advisory

---

## Project Structure

```
AgriShield-TN/
├── app/                          # Streamlit frontend
│   ├── streamlit_app.py          # Entry point, multi-page nav
│   ├── _shared.py                # CSS design system + UI helpers
│   ├── pages/
│   │   ├── 1_Home.py             # Hero landing page
│   │   ├── 2_Analyze_Leaf.py     # Main diagnosis interface
│   │   ├── 3_What_To_Do.py       # Action plan
│   │   ├── 3_How_It_Works.py     # Pipeline explainer
│   │   ├── 4_Impact.py           # Impact metrics
│   │   ├── 5_Future_Scope.py     # Roadmap
│   │   └── 6_Disease_Library.py  # Disease encyclopedia
│   ├── i18n/
│   │   ├── translations.py       # 600+ strings — EN / Tamil / Hindi
│   │   └── lang_utils.py         # t() lookup + session language
│   └── utils/
│       └── voice_utils.py        # gTTS TTS + Groq Whisper STT
│
├── src/                          # ML pipeline
│   ├── config/config.py          # Image size, classes, paths
│   ├── datasets/                 # PyTorch datasets + transforms
│   ├── models/                   # ResNet-18 classifier + metadata fusion
│   ├── training/                 # Training loop + evaluation
│   ├── inference/                # predict.py + Grad-CAM explain.py
│   ├── llm/                      # Groq client + advisory generator
│   └── utils/                    # Weather API, metrics, visualization
│
├── data/raw/                     # train.csv + train_images/ (not in git)
├── checkpoints/                  # best_disease_classifier.pth (not in git)
├── outputs/                      # evaluation_metrics.json
├── .env                          # GROQ_API_KEY (not in git)
├── requirements.txt
└── run_app.py                    # Launcher script
```

---

## External APIs

| API | Purpose | Key required |
|---|---|---|
| Groq `llama-3.1-8b-instant` | Advisory text in EN / Tamil / Hindi | Yes — `GROQ_API_KEY` |
| Groq `whisper-large-v3-turbo` | Voice-to-text transcription | Same key |
| OpenMeteo | Real-time weather + 3-day forecast | No |
| gTTS | Text-to-speech synthesis | No |

---

## Future Scope

- **More languages** — Telugu, Kannada, Marathi
- **Metadata fusion in UI** — wire variety + crop age into predictions for higher accuracy
- **Mobile PWA** — installable offline-capable app for low-connectivity areas
- **Voice-first mode** — full interaction via speech for low-literacy users
- **District disease map** — heatmap of active outbreaks across Tamil Nadu
- **Multi-crop support** — extend beyond paddy to wheat, maize, sugarcane
