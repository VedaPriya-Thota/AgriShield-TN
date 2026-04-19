# 🌾 AgriShield-TN  
### AI-Based Crop Health Diagnosis & Decision Support System

---

## 📌 Overview

AgriShield-TN is an AI-powered system designed to assist farmers in detecting paddy crop diseases from leaf images and providing meaningful insights for decision-making.

Unlike basic image classification projects, this system focuses on:

- Disease detection  
- Explainability (why the model predicted)  
- Risk awareness (weather-based extension)  
- Actionable guidance (future AI advisory layer)

The project is designed with a **real-world agricultural use case in mind**, specifically targeting **Tamil Nadu paddy farming conditions**.

---

## 🎯 Objective

The primary objectives of this project are:

- Detect paddy leaf diseases using deep learning  
- Provide explainable predictions using Grad-CAM  
- Improve trust in AI predictions  
- Extend diagnosis with contextual information (metadata & weather)  
- Move from simple classification → decision support system  

---

## ⚙️ Tech Stack

### AI / ML
- Python
- PyTorch
- Torchvision
- OpenCV
- Albumentations
- NumPy, Pandas

### Explainability
- Grad-CAM
- Matplotlib

### Frontend
- Streamlit

### Utilities
- scikit-learn
- tqdm



### Key features
- Weather APIs
- Groq API (AI advisory)

---

## 🧠 Project Workflow

```text
Image Upload
   ↓
Preprocessing (resize, normalize)
   ↓
CNN Model (ResNet-18)
   ↓
Disease Prediction + Confidence
   ↓
Grad-CAM Heatmap (Explainability)
   ↓
 Weather Risk Analysis
   ↓
 AI Advisory (Groq)
   ↓
Frontend Output
````

---

## 🏗️ Technical Architecture

The system follows a modular architecture:

### 1. Input Layer

* Leaf image
* Metadata (variety, age) *(optional)*

### 2. Image Encoder

* Pretrained **ResNet-18**
* Extracts deep visual features

### 3. Classification Head

* Predicts disease class

### 4. Explainability Layer

* Grad-CAM highlights important regions

### 5. Metadata Encoder (Optional)

* Encodes crop variety and age
* Fuses with image features

### 6. Key features

* Weather-based risk modeling
* AI advisory using LLMs

---

## 📁 Project Structure

```text
AgriShield-TN/
│
├── app/
│   └── streamlit_app.py
│
├── data/
│   └── raw/
│       ├── train_images/
│       ├── test_images/
│       ├── train.csv
│       └── sample_submission.csv
│
├── src/
│   ├── config/
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
├── checkpoints/
├── outputs/
├── requirements.txt
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

#### Windows (PowerShell)

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

#### Windows (CMD)

```cmd
python -m venv venv
venv\Scripts\activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Place Dataset

Ensure dataset is placed correctly:

```text
data/raw/
├── train.csv
├── train_images/
│   ├── bacterial_leaf_blight/
│   ├── blast/
│   ├── brown_spot/
│   └── ...
└── test_images/
```

---

## ▶️ Commands to Run

### 1. Test Dataset Loading

```bash
python -m src.datasets.test_dataset_loading
```

✔ Verifies:

* image loading
* label correctness
* transformations working

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

* Training may take time (CPU)
* First epoch is slower → normal behavior

---

### 3. Evaluate Model

```bash
python -m src.training.evaluate
```

✔ Generates:

* Accuracy
* Precision / Recall / F1-score
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

* Upload image
* Disease prediction
* Confidence score
* Grad-CAM heatmap

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

* Dataset pipeline (image + metadata)
* Image classification model (ResNet-18)
* Training & evaluation pipeline
* Grad-CAM explainability
* Basic Streamlit UI
* Modular project structure
* Groq AI advisory integration
* Weather-based risk analysis

---

### 🚧 In Progress

* Advanced frontend redesign (product-level UI)
---

## ⚠️ Challenges Faced

* Dataset structure mismatch (class-wise folders vs CSV)
* File path issues (image_id handling)
* Integrating Grad-CAM correctly
* Slow CPU training performance
* Virtual environment path issues (Streamlit launcher error)
* Transitioning from “model project” → “product system”

---

## 🔮 Future Scope

* Disease severity estimation (percentage or segmentation)
* Multi-language support (Tamil, Hindi)
* Mobile-friendly interface
* Voice interaction for farmers
* Offline support for low connectivity

---

## 💡 Key Takeaway

This project evolves beyond a simple classifier into a:

👉 **Crop Health Decision Support System**

Combining:

* Computer Vision
* Explainable AI
* Context Awareness
* AI-driven guidance

---
