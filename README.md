
# 🌾 AgriShield-TN  
### AI-Based Crop Health Diagnosis & Multilingual Decision Support System

---

## 📌 Overview

AgriShield-TN is an AI-powered system designed to assist farmers in detecting paddy crop diseases from leaf images and providing meaningful insights for decision-making.

Unlike basic image classification projects, this system focuses on:

- Disease detection  
- Explainability (why the model predicted)  
- Risk awareness (weather-based extension)  
- Actionable guidance (AI advisory layer)  
- 🌍 **Multilingual accessibility for real-world farmers**

The project is built for **real agricultural use**, specifically targeting **Indian farming conditions**, with strong support for **regional languages**.

---

## 🎯 Objective

The primary objectives of this project are:

- Detect paddy leaf diseases using deep learning  
- Provide explainable predictions using Grad-CAM  
- Improve trust in AI predictions  
- Extend diagnosis with contextual data (weather + metadata)  
- Deliver AI insights in **native farmer languages**  
- Transition from classifier → **decision support system**

---

## 🌍 Multilingual System (NEW 🚀)

AgriShield-TN now supports:

- 🇬🇧 English  
- 🇮🇳 Tamil (தமிழ்)  
- 🇮🇳 Hindi (हिन्दी)  

### 🔥 Why this matters

- Most farmers are **not comfortable with English**  
- Language is a **major barrier to adoption**  
- This makes the system **usable in real villages**

---

### ⚙️ Multilingual Implementation

#### 1. Centralized i18n System
- `app/i18n/translations.py` → 600+ translated strings  
- `app/i18n/lang_utils.py` → translation utility  

```python
t("home.title")
````

✔ Handles:

* Nested translations
* Language switching
* Automatic fallback

---

#### 2. Smart Fallback Mechanism

* Missing translations → fallback to English
* Prevents UI breakage

---

#### 3. UI Integration

* Language selector (radio-based UI)
* Applied across:

  * Home
  * Analyze Leaf
  * Disease Library

✔ Improved:

* Visibility
* Contrast
* Accessibility

---

#### 4. Font & Script Support

* Noto Sans Tamil
* Noto Sans Devanagari

✔ Ensures:

* Correct rendering
* Native readability

---

#### 5. Full App Localization

| Page            | Status |
| --------------- | ------ |
| Home            | ✅      |
| Analyze Leaf    | ✅      |
| Disease Library | ✅      |

---

#### 6. AI Advisory in Local Languages 🤖

* Groq API integrated with language context
* AI responds in:

  * Tamil
  * Hindi
  * English

✔ Covers:

* Disease explanation
* Treatment steps
* Prevention guidance

---

#### 7. Session-Based Language Persistence

```python
st.session_state
```

✔ Maintains language across pages

---

## ⚙️ Tech Stack

### AI / ML

* Python
* PyTorch
* Torchvision
* OpenCV
* Albumentations
* NumPy, Pandas

### Explainability

* Grad-CAM
* Matplotlib

### Frontend

* Streamlit

### APIs

* Groq API (AI advisory)
* Weather APIs

### Utilities

* scikit-learn
* tqdm

---

## 🧠 Project Workflow

```text
Image Upload
   ↓
Preprocessing
   ↓
CNN Model (ResNet-18)
   ↓
Disease Prediction
   ↓
Grad-CAM Heatmap
   ↓
Weather Risk Analysis
   ↓
AI Advisory (Groq)
   ↓
Multilingual Output (EN / TA / HI)
```

---

## 🏗️ Technical Architecture

### 1. Input Layer

* Leaf image
* Metadata (optional)

### 2. Image Encoder

* ResNet-18

### 3. Classification Head

* Disease prediction

### 4. Explainability Layer

* Grad-CAM

### 5. Metadata Encoder (Optional)

* Crop variety, age

### 6. Decision Support Layer

* Weather risk analysis
* AI advisory

---

## 📁 Project Structure

```text
AgriShield-TN/
│
├── app/
│   ├── streamlit_app.py
│   ├── i18n/
│   │   ├── translations.py
│   │   └── lang_utils.py
│   └── pages/
│
├── src/
│   ├── models/
│   ├── datasets/
│   ├── training/
│   ├── inference/
│   ├── llm/
│   │   └── agri_insight.py
│   └── utils/
│
├── data/
├── outputs/
├── checkpoints/
└── README.md
```

---

## ⚙️ Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repo-url>
cd AgriShield-TN
```

---

### 2. Create Virtual Environment

```bash
python -m venv venv
```

**Activate:**

PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

CMD:

```cmd
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Place Dataset

```text
data/raw/
├── train.csv
├── train_images/
├── test_images/
```

---

## ▶️ Commands to Run

### 1. Test Dataset Loading

```bash
python -m src.datasets.test_dataset_loading
```

✔ Verifies:

* Image loading
* Label correctness
* Transformations working

---

### 2. Train Image-only Model

```bash
python -m src.training.train_classifier
```

✔ Output:

```
checkpoints/best_disease_classifier.pth
```

⏳ Note:

* Training takes time (CPU)
* First epoch is slow → normal

---

### 3. Evaluate Model

```bash
python -m src.training.evaluate
```

✔ Generates:

* Accuracy
* Precision / Recall / F1
* Confusion Matrix

✔ Saved in:

```
outputs/
```

---

### 4. Run Streamlit App

```bash
streamlit run app/streamlit_app.py
```

or

```bash
python -m streamlit run app/streamlit_app.py
```

✔ Features:

* Image upload
* Disease prediction
* Confidence score
* Grad-CAM heatmap
* 🌍 Multilingual support

---

### 5. Train Metadata Model (Optional)

```bash
python -m src.training.train_metadata_classifier
```

✔ Uses:

* Image
* Variety
* Age

---

## 📊 Current Progress

### ✅ Completed

* Full ML pipeline
* Grad-CAM explainability
* Streamlit UI
* Weather integration
* Groq AI advisory
* 🌍 Multilingual system

---

### 🚧 In Progress

* Advanced UI redesign
* Mobile optimization

---

## ⚠️ Challenges Faced

* Dataset structure mismatch
* File path issues
* Grad-CAM complexity
* Streamlit UI limitations
* Multilingual rendering issues
* Low contrast UI problems

---

## 🔮 Future Scope

* More languages (Telugu, Kannada, Marathi)
* Voice interaction 🎤
* Offline mode
* Disease severity detection
* Mobile app

---

## 💡 Key Takeaway

This project evolves into a:

👉 **Multilingual Crop Health Decision Support System**

---

## 🌟 Final Impact

> Designed not just for developers,
> but for **real farmers in real fields**


