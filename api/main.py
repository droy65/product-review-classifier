"""
FastAPI Backend API for Advanced Amazon Product Review Classification
Includes:
- Calibrated Sentiment Classification (Positive / Negative / Neutral)
- Explainable AI (Keyword Impact Highlights)
- Estimated Amazon Star Rating (1 to 5 Stars)
- Aspect-Based Sentiment Analysis (Quality, Price/Value, Usability, Performance, Delivery/Support)
- Real Amazon Reviews Fetcher (from genuine local dataset or Rainforest API)
- Bulk Batch Classification
- Model Metrics & Dataset Exploration Endpoints
"""

import os
import re
import json
import joblib
import pandas as pd
import numpy as np
import requests
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

app = FastAPI(
    title="Product Review Classifier AI API",
    description="Production-grade Sentiment Analysis & Review Intelligence API powered by Machine Learning on Genuine Amazon Customer Reviews",
    version="2.0.0"
)

# Enable CORS for Streamlit and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths resolution
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model.pkl")
VECTORIZER_PATH = os.path.join(BASE_DIR, "model", "vectorizer.pkl")
METRICS_PATH = os.path.join(BASE_DIR, "model", "metrics.json")
DATASET_PATH = os.path.join(BASE_DIR, "data", "amazon_reviews.csv")

# Docker fallback paths
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "/app/model/model.pkl"
    VECTORIZER_PATH = "/app/model/vectorizer.pkl"
    METRICS_PATH = "/app/model/metrics.json"
    DATASET_PATH = "/app/data/amazon_reviews.csv"

# Global state
model = None
vectorizer = None
metrics = {}
dataset_df = None

def load_resources():
    global model, vectorizer, metrics, dataset_df
    try:
        if os.path.exists(MODEL_PATH) and os.path.exists(VECTORIZER_PATH):
            model = joblib.load(MODEL_PATH)
            vectorizer = joblib.load(VECTORIZER_PATH)
            print("Loaded model and vectorizer successfully.")
    except Exception as e:
        print(f"Warning: Could not load model: {e}")

    try:
        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                metrics = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load metrics: {e}")

    try:
        if os.path.exists(DATASET_PATH):
            dataset_df = pd.read_csv(DATASET_PATH)
            print(f"Loaded genuine Amazon dataset ({len(dataset_df):,} reviews).")
    except Exception as e:
        print(f"Warning: Could not load dataset CSV: {e}")

load_resources()

# ── Aspect Dictionaries ──────────────────────────────────────────
ASPECT_KEYWORDS = {
    "Quality & Build": [
        "quality", "build", "material", "durable", "sturdy", "solid", "cheap", "broke",
        "broken", "flimsy", "plastic", "craftsmanship", "fell apart", "construction"
    ],
    "Price & Value": [
        "price", "cost", "value", "worth", "money", "expensive", "overpriced", "bargain",
        "deal", "affordable", "penny", "waste of money", "rip off"
    ],
    "Ease of Use": [
        "easy", "simple", "setup", "install", "use", "intuitive", "user-friendly",
        "complicated", "difficult", "manual", "instructions", "hard to"
    ],
    "Performance & Reliability": [
        "performance", "speed", "fast", "slow", "battery", "life", "charge", "sound",
        "audio", "bass", "screen", "display", "works", "effective", "power", "lag"
    ],
    "Shipping & Customer Support": [
        "shipping", "delivery", "arrived", "packaging", "box", "package", "service",
        "customer service", "support", "refund", "return", "warranty", "seller"
    ]
}

# ── Request / Response Models ────────────────────────────────────
class ReviewRequest(BaseModel):
    text: str

class KeywordImpact(BaseModel):
    word: str
    impact: str  # "Positive" or "Negative"
    score: float

class AspectSentiment(BaseModel):
    aspect: str
    sentiment: str
    confidence: float
    trigger_words: List[str]

class ReviewResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float
    prob_positive: float
    prob_negative: float
    estimated_stars: int
    star_display: str
    key_signals: List[KeywordImpact]
    aspects: List[AspectSentiment]

class BatchReviewRequest(BaseModel):
    reviews: List[str]

class BatchReviewResponse(BaseModel):
    total_processed: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_confidence: float
    results: List[ReviewResponse]

class FetchRequest(BaseModel):
    product_id: Optional[str] = "B08N5WRWNW"
    category: Optional[str] = None
    count: Optional[int] = 6
    api_key: Optional[str] = None

# ── Helper Functions ─────────────────────────────────────────────
def explain_text(text: str, vec_text, pred_label: int, top_k=5) -> List[KeywordImpact]:
    """Calculates feature attribution for the input review."""
    if not model or not vectorizer:
        return []
    
    coefs = model.coef_[0]
    feature_names = vectorizer.get_feature_names_out()
    
    # Non-zero indices in the vector
    row_indices = vec_text.indices
    row_data = vec_text.data
    
    signals = []
    for idx, tfidf_val in zip(row_indices, row_data):
        token = feature_names[idx]
        weight = coefs[idx] * tfidf_val
        if abs(weight) > 0.05:
            impact_type = "Positive" if weight > 0 else "Negative"
            signals.append(KeywordImpact(
                word=token,
                impact=impact_type,
                score=round(float(abs(weight)), 3)
            ))
            
    # Sort by absolute impact
    signals.sort(key=lambda s: s.score, reverse=True)
    return signals[:top_k]

def analyze_aspects(text: str) -> List[AspectSentiment]:
    """Detects product aspects and assesses sentiment for each mentioned aspect."""
    if not model or not vectorizer:
        return []
    
    lower_text = text.lower()
    aspect_results = []
    
    # Split text into sentences for local aspect sentiment
    sentences = re.split(r'[.!?]+', text)
    
    for aspect_name, keywords in ASPECT_KEYWORDS.items():
        matched_words = [kw for kw in keywords if re.search(r'\b' + re.escape(kw) + r'\b', lower_text)]
        if matched_words:
            # Find sentences containing any matched keyword
            aspect_sentences = [
                s.strip() for s in sentences
                if any(re.search(r'\b' + re.escape(kw) + r'\b', s.lower()) for kw in matched_words)
            ]
            aspect_snippet = " ".join(aspect_sentences) if aspect_sentences else text
            
            try:
                vec = vectorizer.transform([aspect_snippet])
                probs = model.predict_proba(vec)[0]
                prob_pos = probs[1]
                
                if prob_pos > 0.58:
                    sent = "Positive"
                    conf = prob_pos
                elif prob_pos < 0.42:
                    sent = "Negative"
                    conf = 1.0 - prob_pos
                else:
                    sent = "Neutral"
                    conf = 0.50
                    
                aspect_results.append(AspectSentiment(
                    aspect=aspect_name,
                    sentiment=sent,
                    confidence=round(float(conf), 2),
                    trigger_words=matched_words[:4]
                ))
            except Exception:
                pass
                
    return aspect_results

def calculate_stars(prob_pos: float) -> (int, str):
    """Maps calibrated positive probability to Amazon 1-5 star rating."""
    if prob_pos >= 0.82:
        return 5, "⭐⭐⭐⭐⭐"
    elif prob_pos >= 0.60:
        return 4, "⭐⭐⭐⭐"
    elif prob_pos >= 0.40:
        return 3, "⭐⭐⭐"
    elif prob_pos >= 0.20:
        return 2, "⭐⭐"
    else:
        return 1, "⭐"

# ── Endpoints ────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Product Review Classifier API",
        "status": "online",
        "version": "2.0.0",
        "model_loaded": model is not None,
        "docs_url": "/docs"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "vectorizer_loaded": vectorizer is not None,
        "dataset_rows": len(dataset_df) if dataset_df is not None else 0
    }

@app.get("/model_info")
def get_model_info():
    """Returns training metrics, accuracy, vocabulary size and dataset information."""
    if not metrics and os.path.exists(METRICS_PATH):
        try:
            with open(METRICS_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return metrics if metrics else {"status": "Metrics not generated yet. Run model/train.py"}

@app.post("/predict", response_model=ReviewResponse)
def predict_review(request: ReviewRequest):
    """Classifies a single review with calibrated confidence, star rating, and explainability signals."""
    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="Machine learning model or vectorizer is not loaded.")
    
    clean_input = request.text.strip()
    if not clean_input:
        raise HTTPException(status_code=400, detail="Review text cannot be empty.")
    
    vec_text = vectorizer.transform([clean_input])
    probs = model.predict_proba(vec_text)[0]
    prob_neg = float(probs[0])
    prob_pos = float(probs[1])
    
    # Classification with neutral / mixed boundary
    if 0.46 <= prob_pos <= 0.54:
        sentiment = "Neutral"
        confidence = round(1.0 - abs(prob_pos - 0.5) * 2, 4)
    elif prob_pos > 0.54:
        sentiment = "Positive"
        confidence = round(prob_pos, 4)
    else:
        sentiment = "Negative"
        confidence = round(prob_neg, 4)
        
    stars, star_display = calculate_stars(prob_pos)
    signals = explain_text(clean_input, vec_text, 1 if prob_pos > 0.5 else 0)
    aspects = analyze_aspects(clean_input)
    
    return ReviewResponse(
        text=request.text,
        sentiment=sentiment,
        confidence=confidence,
        prob_positive=round(prob_pos, 4),
        prob_negative=round(prob_neg, 4),
        estimated_stars=stars,
        star_display=star_display,
        key_signals=signals,
        aspects=aspects
    )

@app.post("/predict_batch", response_model=BatchReviewResponse)
def predict_batch(request: BatchReviewRequest):
    """Batch classifies a list of customer reviews with aggregate summary statistics."""
    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    
    if not request.reviews:
        raise HTTPException(status_code=400, detail="Reviews list cannot be empty.")
    
    results = []
    pos_count = 0
    neg_count = 0
    neu_count = 0
    total_conf = 0.0
    
    vecs = vectorizer.transform(request.reviews)
    probs_all = model.predict_proba(vecs)
    
    for i, text in enumerate(request.reviews):
        probs = probs_all[i]
        prob_neg = float(probs[0])
        prob_pos = float(probs[1])
        
        if 0.46 <= prob_pos <= 0.54:
            sentiment = "Neutral"
            confidence = round(1.0 - abs(prob_pos - 0.5) * 2, 4)
            neu_count += 1
        elif prob_pos > 0.54:
            sentiment = "Positive"
            confidence = round(prob_pos, 4)
            pos_count += 1
        else:
            sentiment = "Negative"
            confidence = round(prob_neg, 4)
            neg_count += 1
            
        total_conf += confidence
        stars, star_display = calculate_stars(prob_pos)
        
        results.append(ReviewResponse(
            text=text,
            sentiment=sentiment,
            confidence=confidence,
            prob_positive=round(prob_pos, 4),
            prob_negative=round(prob_neg, 4),
            estimated_stars=stars,
            star_display=star_display,
            key_signals=[],
            aspects=[]
        ))
        
    avg_conf = round(total_conf / len(request.reviews), 4) if request.reviews else 0.0
    
    return BatchReviewResponse(
        total_processed=len(request.reviews),
        positive_count=pos_count,
        negative_count=neg_count,
        neutral_count=neu_count,
        average_confidence=avg_conf,
        results=results
    )

@app.post("/fetch_reviews")
def fetch_reviews(request: FetchRequest):
    """
    Fetches genuine Amazon reviews.
    - If Rainforest API key is provided, calls Rainforest API for live data.
    - Otherwise, fetches authentic reviews from the genuine 35,000 Amazon dataset matching ASIN or category.
    """
    if request.api_key:
        params = {
            'api_key': request.api_key,
            'type': 'reviews',
            'amazon_domain': 'amazon.com',
            'asin': request.product_id
        }
        try:
            response = requests.get('https://api.rainforestapi.com/request', params=params, timeout=12)
            response.raise_for_status()
            data = response.json()
            raw_reviews = data.get('reviews', [])
            
            results = []
            for r in raw_reviews:
                text = (r.get('title', '') + " " + r.get('body', '')).strip()
                if text:
                    vec = vectorizer.transform([text])
                    probs = model.predict_proba(vec)[0]
                    prob_pos = probs[1]
                    sentiment = "Positive" if prob_pos > 0.5 else "Negative"
                    stars, star_str = calculate_stars(prob_pos)
                    results.append({
                        "title": r.get('title', ''),
                        "text": text,
                        "sentiment": sentiment,
                        "confidence": round(float(max(probs)), 3),
                        "rating": r.get('rating', stars),
                        "star_display": star_str,
                        "verified_purchase": r.get('verified_purchase', True)
                    })
            return {
                "source": "Rainforest API (Live)",
                "product_id": request.product_id,
                "count": len(results),
                "reviews": results
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Rainforest API error: {e}")
            
    # Default: fetch genuine authentic Amazon reviews from our 35,000 dataset
    if dataset_df is None or len(dataset_df) == 0:
        raise HTTPException(status_code=500, detail="Genuine Amazon dataset not loaded. Run model/train.py first.")
        
    filtered_df = dataset_df
    if request.product_id:
        asin_matches = dataset_df[dataset_df['product_id'] == request.product_id]
        if len(asin_matches) > 0:
            filtered_df = asin_matches
            
    if request.category:
        cat_matches = filtered_df[filtered_df['product_category'].str.lower() == request.category.lower()]
        if len(cat_matches) > 0:
            filtered_df = cat_matches
            
    sample_size = min(request.count or 6, len(filtered_df))
    sampled = filtered_df.sample(n=sample_size, random_state=None)
    
    results = []
    for _, row in sampled.iterrows():
        text = str(row.get('full_review', row.get('review_text', '')))
        vec = vectorizer.transform([text])
        probs = model.predict_proba(vec)[0]
        prob_pos = probs[1]
        
        if 0.46 <= prob_pos <= 0.54:
            sentiment = "Neutral"
        elif prob_pos > 0.54:
            sentiment = "Positive"
        else:
            sentiment = "Negative"
            
        stars, star_str = calculate_stars(prob_pos)
        
        results.append({
            "review_id": row.get('review_id', 'AMZN_REV'),
            "product_id": row.get('product_id', request.product_id),
            "category": row.get('product_category', 'General'),
            "title": str(row.get('review_title', '')),
            "text": str(row.get('review_text', '')),
            "sentiment": sentiment,
            "confidence": round(float(max(probs)), 3),
            "prob_positive": round(float(prob_pos), 3),
            "rating": int(row.get('star_rating', stars)),
            "star_display": star_str,
            "verified_purchase": bool(row.get('verified_purchase', True)),
            "helpful_votes": int(row.get('helpful_votes', 0))
        })
        
    return {
        "source": "Genuine Amazon Reviews Dataset (35,000 items)",
        "product_id": request.product_id,
        "count": len(results),
        "reviews": results,
        "note": "Loaded genuine authentic customer reviews from Amazon"
    }

@app.get("/dataset/sample")
def get_dataset_sample(n: int = 10, category: Optional[str] = None):
    """Returns random authentic Amazon review samples from the genuine dataset."""
    if dataset_df is None:
        raise HTTPException(status_code=500, detail="Dataset not loaded.")
        
    df = dataset_df
    if category:
        df = df[df['product_category'].str.lower() == category.lower()]
        
    samples = df.sample(n=min(n, len(df))).to_dict(orient="records")
    return {"total_available": len(dataset_df), "sample_size": len(samples), "samples": samples}

@app.get("/dataset/stats")
def get_dataset_stats():
    """Returns genuine dataset distribution stats (categories, ratings, sentiment balance)."""
    if dataset_df is None:
        raise HTTPException(status_code=500, detail="Dataset not loaded.")
        
    return {
        "total_reviews": len(dataset_df),
        "sentiment_counts": dataset_df['sentiment'].value_counts().to_dict(),
        "star_rating_counts": dataset_df['star_rating'].value_counts().to_dict(),
        "categories": dataset_df['product_category'].value_counts().to_dict(),
        "verified_purchase_pct": round(float(dataset_df['verified_purchase'].mean() * 100), 1)
    }
