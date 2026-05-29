import os
import joblib
import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI(title="Product Review Classifier API")

# Load model and vectorizer at startup
model = None
vectorizer = None

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../model/model.pkl")
VECTORIZER_PATH = os.path.join(os.path.dirname(__file__), "../model/vectorizer.pkl")

# In Docker, paths might be different, let's adjust for Docker if they don't exist
if not os.path.exists(MODEL_PATH):
    MODEL_PATH = "/app/model/model.pkl"
    VECTORIZER_PATH = "/app/model/vectorizer.pkl"

try:
    model = joblib.load(MODEL_PATH)
    vectorizer = joblib.load(VECTORIZER_PATH)
except Exception as e:
    print(f"Warning: Model or vectorizer not found. {e}")

class ReviewRequest(BaseModel):
    text: str

class ReviewResponse(BaseModel):
    text: str
    sentiment: str
    confidence: float

class FetchRequest(BaseModel):
    product_id: str
    # Amazon API key if available
    api_key: str = None

@app.post("/predict", response_model=ReviewResponse)
def predict_review(request: ReviewRequest):
    if not model or not vectorizer:
        raise HTTPException(status_code=500, detail="Model is not loaded.")
    
    vec_text = vectorizer.transform([request.text])
    prediction = model.predict(vec_text)[0]
    probabilities = model.predict_proba(vec_text)[0]
    
    sentiment = "Positive" if prediction == 1 else "Negative"
    confidence = float(max(probabilities))
    
    return ReviewResponse(text=request.text, sentiment=sentiment, confidence=confidence)

@app.post("/fetch_reviews")
def fetch_reviews(request: FetchRequest):
    """
    Fetches real-time Amazon product reviews. 
    If a real API key for Rainforest API is provided, uses it.
    Otherwise, returns some mock reviews for demonstration.
    """
    if request.api_key:
        # Example using Rainforest API (Amazon Data API)
        params = {
            'api_key': request.api_key,
            'type': 'reviews',
            'amazon_domain': 'amazon.com',
            'asin': request.product_id
        }
        try:
            response = requests.get('https://api.rainforestapi.com/request', params=params)
            response.raise_for_status()
            data = response.json()
            reviews = data.get('reviews', [])
            
            results = []
            for r in reviews:
                text = r.get('title', '') + " " + r.get('body', '')
                if text.strip():
                    vec_text = vectorizer.transform([text])
                    pred = model.predict(vec_text)[0]
                    sentiment = "Positive" if pred == 1 else "Negative"
                    results.append({
                        "text": text,
                        "sentiment": sentiment,
                        "rating": r.get('rating')
                    })
            return {"product_id": request.product_id, "reviews": results}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    else:
        # Return mock Amazon reviews to simulate the API response
        mock_reviews = [
            "This product is amazing! Totally changed my life. 5 stars.",
            "Terrible quality, broke after one day of use.",
            "It's okay, not the best but it gets the job done.",
            "I love the design and it works perfectly. Highly recommend.",
            "Do not buy this. Complete waste of money."
        ]
        
        results = []
        for text in mock_reviews:
            vec_text = vectorizer.transform([text])
            pred = model.predict(vec_text)[0]
            sentiment = "Positive" if pred == 1 else "Negative"
            results.append({
                "text": text,
                "sentiment": sentiment
            })
            
        return {"product_id": request.product_id, "reviews": results, "note": "Mocked data (no API key provided)"}
