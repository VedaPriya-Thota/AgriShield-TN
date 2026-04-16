# 🌾 AgriShield-TN

**Multimodal Paddy Disease Detection & Risk Analysis System**

---

## 🚀 Overview

AgriShield-TN is an AI-powered system designed to detect paddy leaf diseases using deep learning. It combines:

* 🌿 **Image-based disease classification**
* 📊 **Metadata (variety + age) awareness**
* 🔍 **Explainable AI (Grad-CAM heatmaps)**
* 📈 Future extension: **Weather-based risk prediction**

The goal is to provide **accurate, explainable, and actionable insights** for farmers in Tamil Nadu.

---

## 🎯 Objectives

* Detect paddy diseases from leaf images
* Improve prediction using metadata (variety, age)
* Provide visual explanations (heatmaps)
* Build a scalable pipeline for future weather integration

---

## 🧱 Project Structure

```
AgriShield-TN/
│
├── data/
│   ├── raw/
│   │   ├── train_images/
│   │   ├── test_images/
│   │   ├── train.csv
│   │   └── sample_submission.csv
│   │
│   ├── processed/
│   └── metadata/
│
├── src/
│   ├── config/
│   │   └── config.py
│   │
│   ├── datasets/
│   │   ├── image_dataset.py
│   │   ├── metadata_dataset.py
│   │   ├── transforms.py
│   │   └── test_dataset_loading.py
│   │
│   ├── models/
│   │   ├── image_encoder.py
│   │   ├── disease_classifier.py
│   │   ├── metadata_encoder.py
│   │   └── metadata_classifier.py
│   │
│   ├── training/
│   │   ├── train_classifier.py
│   │   ├── train_metadata_classifier.py
│   │   └── evaluate.py
│   │
│   ├── inference/
│   │   ├── predict.py
│   │   └── explain.py
│   │
│   └── utils/
│       └── visualization.py
│
├── app/
│   └── streamlit_app.py
│
├── checkpoints/
├── outputs/
├── requirements.txt
└── README.md
```

---

## ⚙️ Setup Instructions

### 1️⃣ Create Virtual Environment

```powershell
python -m venv venv
venv\Scripts\activate
```

---

### 2️⃣ Install Dependencies

```powershell
pip install -r requirements.txt
```

---

### 3️⃣ Dataset Setup

Place dataset inside:

```
data/raw/
```

Required:

```
train.csv
train_images/
test_images/
```

---

## 🧠 Technical Architecture

### 🔹 Phase 1: Image-only Model

```
Image → CNN (ResNet18) → Feature Vector → Classifier → Disease
```

---

### 🔹 Phase 2: Metadata-aware Model

```
Image → CNN → Image Features
Metadata → Encoder → Metadata Features

           ↓
      Fusion Layer
           ↓
    Disease Prediction
```

---

### 🔹 Phase 3 (Future)

```
Image + Metadata + Weather → Fusion → Disease + Severity + Risk
```

---

## 📊 Workflow

```
Input Image
    ↓
Preprocessing (resize, normalize)
    ↓
Model (CNN)
    ↓
Prediction (Disease Class)
    ↓
Grad-CAM → Heatmap
    ↓
Streamlit UI Output
```

---

## 🧪 Commands (VERY IMPORTANT)

### ✅ 1. Test Dataset Loading

```powershell
python -m src.datasets.test_dataset_loading
```

✔ Verifies:

* images loading
* labels correct
* transformations working

---

### ✅ 2. Train Image-only Model

```powershell
python -m src.training.train_classifier
```

✔ Output:

```
checkpoints/best_disease_classifier.pth
```

---

### ⏳ Note:

Training may take time (CPU).
First epoch is always slow → **normal**

---

### ✅ 3. Evaluate Model

```powershell
python -m src.training.evaluate
```

✔ Generates:

* accuracy
* precision / recall / F1
* confusion matrix (image)

Saved in:

```
outputs/
```

---

### ✅ 4. Run Streamlit App

```powershell
streamlit run app/streamlit_app.py
```

✔ Features:

* upload image
* prediction
* confidence
* Grad-CAM heatmap

---

### ✅ 5. Train Metadata Model (Optional)

```powershell
python -m src.training.train_metadata_classifier
```

✔ Uses:

* image
* variety
* age

---

## 🔍 Explainability (Grad-CAM)

* Highlights important leaf regions
* Shows **why** model predicted disease
* Improves trust and interpretability

---

## 📈 Current Progress

✔ Dataset loading
✔ Image classification model
✔ Training pipeline
✔ Evaluation metrics
✔ Streamlit UI
✔ Grad-CAM explainability

---

## 🚧 Next Steps

* Add weather data integration
* Yield risk prediction
* Severity segmentation (heatmap masks)
* Tamil language support

---

## 💡 Key Highlights

* Uses real-world agricultural dataset
* Combines AI + domain knowledge
* Explainable AI (not black-box)
* Scalable to full AgriTech system

---

## 🧑‍💻 Author

Vedagrani Burragoni
B.Tech CSE (DS & AI)

---

## 🏁 Final Note

This project evolves step-by-step:

```
Data → Model → Evaluation → UI → Explainability → Multimodal AI
```

You have already completed the **hardest part (data pipeline + training setup)**.

---

🔥 **You are now building a real-world AI system, not just a project.**
