"""
High-Performance Model Training Script for Amazon Product Review Classifier
Trains a production-grade Logistic Regression model with sublinear TF-IDF (unigrams + bigrams),
preserving negation tokens to correctly classify authentic Amazon reviews.
Saves model.pkl, vectorizer.pkl, and detailed metrics.json.
"""

import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, ENGLISH_STOP_WORDS
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix

# Preserving critical negation and sentiment modifiers from being stripped
NEGATION_WORDS = {
    "not", "no", "never", "neither", "nor", "none", "hardly", "scarcely",
    "barely", "cannot", "cant", "don't", "dont", "doesn't", "doesnt",
    "didn't", "didnt", "won't", "wont", "wouldn't", "wouldnt", "shouldn't",
    "shouldnt", "wasn't", "wasnt", "weren't", "werent", "ain't", "without",
    "against", "least", "less", "nothing", "nowhere"
}

CUSTOM_STOP_WORDS = list(ENGLISH_STOP_WORDS - NEGATION_WORDS)

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return text.strip()

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "data", "amazon_reviews.csv")
    
    # Check if dataset exists, if not generate it
    if not os.path.exists(data_path):
        print(f"Dataset not found at {data_path}. Running prepare_dataset.py...")
        from prepare_dataset import build_dataset
        build_dataset(num_samples=35000, output_csv="data/amazon_reviews.csv")
        
    print(f"Loading genuine Amazon reviews dataset from {data_path}...")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df):,} reviews.")
    
    # Use full review (title + text) for optimal context
    text_col = 'full_review' if 'full_review' in df.columns else 'review_text'
    df['clean_text'] = df[text_col].apply(clean_text)
    
    # Filter empty texts
    df = df[df['clean_text'].str.len() > 10].reset_index(drop=True)
    
    X = df['clean_text']
    y = df['label'].astype(int)
    
    print(f"Dataset class distribution:\n{y.value_counts()}")
    
    # 80/20 train/test split with stratification
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    print(f"Training set: {len(X_train):,} samples | Test set: {len(X_test):,} samples")
    
    print("\nVectorizing text with TF-IDF (unigrams + bigrams, negation-preserving stopwords)...")
    vectorizer = TfidfVectorizer(
        ngram_range=(1, 2),
        max_features=40000,
        min_df=3,
        sublinear_tf=True,
        stop_words=CUSTOM_STOP_WORDS,
        token_pattern=r"(?u)\b\w[\w']+\b"  # Preserve contractions like don't, won't
    )
    
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    print(f"Vocabulary size: {len(vectorizer.vocabulary_):,} features")
    
    print("\nTraining calibrated Logistic Regression model...")
    model = LogisticRegression(
        C=2.0,
        max_iter=1000,
        solver='lbfgs',
        random_state=42,
        class_weight='balanced'
    )
    model.fit(X_train_vec, y_train)
    
    print("\nEvaluating model performance on genuine Amazon test set...")
    y_pred = model.predict(X_test_vec)
    y_proba = model.predict_proba(X_test_vec)[:, 1]
    
    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    cm = confusion_matrix(y_test, y_pred).tolist()
    report = classification_report(y_test, y_pred, target_names=["Negative", "Positive"], output_dict=True)
    
    print(f"Accuracy:  {acc * 100:.2f}%")
    print(f"Precision: {prec * 100:.2f}%")
    print(f"Recall:    {rec * 100:.2f}%")
    print(f"F1-Score:  {f1 * 100:.2f}%")
    print("\nConfusion Matrix:")
    print(f"TN: {cm[0][0]} | FP: {cm[0][1]}")
    print(f"FN: {cm[1][0]} | TP: {cm[1][1]}")
    
    # Extract top positive and negative vocabulary coefficients for explainability
    feature_names = np.array(vectorizer.get_feature_names_out())
    coefs = model.coef_[0]
    
    top_pos_indices = np.argsort(coefs)[-30:][::-1]
    top_neg_indices = np.argsort(coefs)[:30]
    
    top_pos_words = [{"word": feature_names[i], "weight": round(float(coefs[i]), 3)} for i in top_pos_indices]
    top_neg_words = [{"word": feature_names[i], "weight": round(float(coefs[i]), 3)} for i in top_neg_indices]
    
    print("\nTop 5 Positive Signals:", [w["word"] for w in top_pos_words[:5]])
    print("Top 5 Negative Signals:", [w["word"] for w in top_neg_words[:5]])
    
    # Save artifacts directly inside model/ directory
    model_path = os.path.join(model_dir, "model.pkl")
    vectorizer_path = os.path.join(model_dir, "vectorizer.pkl")
    metrics_path = os.path.join(model_dir, "metrics.json")
    
    print(f"\nSaving model to: {model_path}")
    joblib.dump(model, model_path)
    
    print(f"Saving vectorizer to: {vectorizer_path}")
    joblib.dump(vectorizer, vectorizer_path)
    
    metrics_data = {
        "model_type": "Logistic Regression with Negation-Aware TF-IDF",
        "trained_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dataset_total_samples": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "vocabulary_size": len(vectorizer.vocabulary_),
        "ngram_range": [1, 2],
        "accuracy": round(float(acc), 4),
        "precision": round(float(prec), 4),
        "recall": round(float(rec), 4),
        "f1_score": round(float(f1), 4),
        "confusion_matrix": {
            "true_negative": cm[0][0],
            "false_positive": cm[0][1],
            "false_negative": cm[1][0],
            "true_positive": cm[1][1]
        },
        "classification_report": report,
        "top_positive_features": top_pos_words,
        "top_negative_features": top_neg_words
    }
    
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(metrics_data, f, indent=2)
    print(f"Saved metrics to: {metrics_path}")
    print("\nTraining successfully complete!")

if __name__ == "__main__":
    main()
