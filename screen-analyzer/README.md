
# Screen Analyzer - Cross Platform AI Coach

A fully local, privacy-first AI screen analyzer for MacOS & Windows.

- Real-time screen OCR
- Context detection (Programming, Video, Reading, etc.)
- Sentiment analysis
- Idle time detection
- Trigger logic for interventions

---

## 📂 Project Structure

screen-analyzer/
  ├── shared/
  │   ├── ocr.py
  │   ├── context.py
  │   ├── sentiment.py
  │   ├── chrome_tab.py
  │   └── requirements.txt
  ├── mac/
  │   ├── test_live.py
  │   ├── mac_capture.py
  │   ├── mac_window.py
  │   ├── idle_tracker.py
  │   └── requirements_mac.txt
  ├── windows/
  │   ├── test_live.py
  │   ├── win_capture.py
  │   ├── win_window.py
  │   ├── idle_tracker_win.py
  │   └── requirements_win.txt

---

## 🚨 VERY IMPORTANT:

Always run `test_live.py` from the root directory .

### For Mac:

```

cd screen-analyzer
python mac/test_live.py

```

### For Windows:

```

cd screen-analyzer
python windows/test_live.py

```

---

## ⚙ Environment Setup Instructions

### 1️⃣ Create Conda Environment (Recommended)

```

conda create -n screenai python=3.11 or 3.9
conda activate screenai

```

---

### 2️⃣ Install Shared Dependencies

Navigate to shared folder:

```

cd shared
pip install -r requirements.txt

```

---

### 3️⃣ MacOS Installation

Navigate to mac folder:

```

cd ../mac
pip install -r requirements_mac.txt

```

---

### 4️⃣ Windows Installation

Navigate to windows folder:

```

cd ../windows
pip install -r requirements_win.txt

```

---

## ✅ Features Summary

- Screen OCR using Tesseract + OpenCV
- Context Classification (rule-based NLP)
- Sentiment Detection (VADER)
- Idle Detection (Quartz on Mac, LastInputInfo on Windows)
- Trigger logic for AI-Coach interventions
- Fully local, privacy-first

---

