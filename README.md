# ReviewLens AI · Advanced Amazon Product Review Classifier

> **Enterprise-grade sentiment classification, aspect mining, and star rating prediction powered by Machine Learning on 35,000+ authentic Amazon customer reviews.**

---

## 🌟 Key Highlights & Major Improvements

- **Genuine, Authentic Amazon Dataset**: Replaced the previous 20-sample synthetic toy dataset with **35,000 genuine, authentic Amazon customer reviews** across 10 diverse categories with real star ratings (1–5 stars), verified purchase badges, review titles, and full review bodies.
- **High Test Accuracy (89.3%)**: Production-calibrated Logistic Regression model using sublinear TF-IDF with **unigrams + bigrams (40,000 features)** and **negation-preserving custom stopword filtering** (ensuring critical phrases like *"not good"*, *"never buy"*, and *"worth every penny"* are accurately classified).
- **Explainable AI (XAI)**: Real-time feature attribution displaying the exact keywords and n-grams driving the positive or negative classification decision.
- **Aspect-Based Sentiment Mining**: Automatically identifies and rates customer sentiment across 5 core product dimensions:
  - *Quality & Build*
  - *Price & Value*
  - *Ease of Use*
  - *Performance & Battery*
  - *Shipping & Customer Support*
- **Star Rating Prediction**: Maps calibrated class probabilities into realistic Amazon 1-to-5 star ratings (⭐ to ⭐⭐⭐⭐⭐).
- **Interactive Streamlit UI**: Completely revamped with modern dark glassmorphism, responsive metric cards, probability distribution gauges, and charts.
- **Batch CSV / Excel Classifier**: Upload any review file, run bulk inference with a live progress bar, view sentiment & star distribution charts, and download an enriched CSV.
- **Live Amazon Review Hub**: Explore genuine reviews by ASIN or category, or integrate live scraping via Rainforest API.
- **One-Click Launch**: Double-click `run_project.bat` or run `./run_project.ps1` to launch both backend and frontend together.

---

## 🏗️ Project Architecture

```text
product-review-classifier/
│
├── api/                             # FastAPI REST API Backend
│   ├── main.py                      # Endpoints (/predict, /predict_batch, /fetch_reviews, etc.)
│   ├── requirements.txt             # Backend dependencies
│   └── Dockerfile                   # Backend Docker container config
│
├── frontend/                        # Streamlit Interactive Web Application
│   ├── app.py                       # Glassmorphic multi-tab user interface
│   ├── requirements.txt             # Frontend dependencies
│   └── Dockerfile                   # Frontend Docker container config
│
├── model/                           # Machine Learning Pipeline & Artifacts
│   ├── prepare_dataset.py           # Extracts & formats 35,000 genuine Amazon reviews
│   ├── train.py                     # High-performance ML training script
│   ├── model.pkl                    # Trained Logistic Regression model
│   ├── vectorizer.pkl               # Trained 40,000-feature TF-IDF vectorizer
│   ├── metrics.json                 # Evaluated test metrics & confusion matrix
│   └── requirements.txt             # Training dependencies
│
├── data/                            # Datasets
│   ├── amazon_reviews.csv           # 35,000 genuine Amazon customer reviews (33 MB)
│   └── sample_reviews_for_testing.csv # 1,000 sample reviews for quick batch upload testing
│
├── docker-compose.yml               # Multi-container Docker deployment
├── run_project.bat                  # One-click Windows batch launcher
├── run_project.ps1                  # One-click PowerShell launcher
└── README.md                        # Project documentation
```

---

## 📊 Model Performance Scorecard

Evaluated on **7,000 real, unseen Amazon customer reviews** from the test split:

| Metric | Score |
| :--- | :--- |
| **Accuracy** | **89.26%** |
| **Precision** | **88.95%** |
| **Recall** | **89.66%** |
| **F1-Score** | **89.30%** |
| **Dataset Size** | **35,000 Genuine Reviews** |
| **Vocabulary Size** | **40,000 TF-IDF Features** |
| **N-Gram Range** | **(1, 2) Unigrams + Bigrams** |

### Confusion Matrix (Test Set: 7,000 Samples)
- **True Negatives (TN)**: 3,110
- **False Positives (FP)**: 390
- **False Negatives (FN)**: 362
- **True Positives (TP)**: 3,138

---

## 🚀 Quick Start Guide

### Option 1: One-Click Launch (Windows)

Simply double-click:
```cmd
run_project.bat
```
or run in PowerShell:
```powershell
.\run_project.ps1
```
This automatically verifies dependencies, launches the FastAPI backend on port 8000, and opens the Streamlit frontend on port 8501.

---

### Option 2: Manual Setup

#### 1. Activate Virtual Environment
```bash
# Windows
.\.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

#### 2. Install Dependencies
```bash
pip install -r api/requirements.txt
pip install -r frontend/requirements.txt
pip install -r model/requirements.txt
```

#### 3. (Optional) Re-train the Model
The repository comes pre-trained with `model/model.pkl` and `model/vectorizer.pkl`. If you wish to retrain from scratch:
```bash
python model/train.py
```

#### 4. Run Backend API
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be available at: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 5. Run Frontend UI (In a new terminal)
```bash
streamlit run frontend/app.py --server.port 8501
```
Access the application at: [http://localhost:8501](http://localhost:8501)

---

### Option 3: Run with Docker Compose

Ensure Docker Desktop is running, then execute:
```bash
docker compose up --build
```
- **Streamlit Frontend**: [http://localhost:8501](http://localhost:8501)
- **FastAPI Backend**: [http://localhost:8000](http://localhost:8000)

To stop the containers:
```bash
docker compose down
```

---

## 🔌 API Endpoints Reference

### 1. Single Review Prediction
- **`POST /predict`**
  - **Payload**: `{"text": "The battery life is amazing and sound is crystal clear!"}`
  - **Response**:
    ```json
    {
      "text": "The battery life is amazing and sound is crystal clear!",
      "sentiment": "Positive",
      "confidence": 0.926,
      "prob_positive": 0.926,
      "prob_negative": 0.074,
      "estimated_stars": 5,
      "star_display": "⭐⭐⭐⭐⭐",
      "key_signals": [
        {"word": "amazing", "impact": "Positive", "score": 1.217},
        {"word": "crystal clear", "impact": "Positive", "score": 0.63}
      ],
      "aspects": [
        {
          "aspect": "Performance & Reliability",
          "sentiment": "Positive",
          "confidence": 0.91,
          "trigger_words": ["battery", "sound"]
        }
      ]
    }
    ```

### 2. Batch Review Prediction
- **`POST /predict_batch`**
  - **Payload**: `{"reviews": ["review 1...", "review 2..."]}`
  - **Response**: Summary counts (`positive_count`, `negative_count`, `average_confidence`) and per-review predictions.

### 3. Fetch Amazon Reviews
- **`POST /fetch_reviews`**
  - **Payload**: `{"product_id": "B08N5WRWNW", "count": 6}`
  - Returns verified Amazon reviews with ratings, titles, bodies, and predicted sentiments from the genuine dataset (or live via Rainforest API if an API key is provided).

### 4. Dataset & Model Analytics
- **`GET /dataset/stats`**: Returns total counts, rating distribution, category spread, and verified purchase ratio.
- **`GET /dataset/sample`**: Returns raw review samples for auditing.
- **`GET /model_info`**: Returns model architecture, accuracy, precision, recall, and top predictive n-grams.
- **`GET /health`**: Health status check.

---

## 🎨 UI Features Walkthrough

1. **⚡ Live Review Analyzer**: Type or paste any review or select from authentic Amazon review presets. Instantly reveals sentiment badge, confidence percentage, 1–5 star rating, feature attribution chips, and aspect analysis.
2. **🛒 Amazon Product Review Hub**: Browse verified reviews for flagship gadgets (AirPods Pro, Sony Headphones, Kindle, Instant Pot) or enter custom ASINs. View real-time Customer Satisfaction Index and Net Sentiment Scores.
3. **📂 Batch CSV Classifier**: Upload any CSV or Excel file or load the built-in 100-review sample. Process hundreds of reviews in seconds with live progress tracking, sentiment and star distribution charts, and one-click enriched CSV download.
4. **📊 Genuine Dataset & Model Intelligence**: Deep dive into the 35,000-review dataset with category and rating charts, full model metrics, and top predictive vocabulary words.

---

## 📄 License

MIT License. Open-source for academic, educational, and commercial development.
