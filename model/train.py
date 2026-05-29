import os
import joblib
import pandas as pd
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

def main():
    print("Loading amazon_polarity dataset...")
    print("Generating synthetic Amazon review data for demonstration...")
    # Generate some positive and negative Amazon-style reviews
    positive_reviews = [
        "This product is amazing! Totally changed my life. 5 stars.",
        "I love the design and it works perfectly. Highly recommend.",
        "Great quality and fast shipping. Will buy again.",
        "Exactly what I was looking for. Very satisfied.",
        "Fantastic purchase. The battery life is incredible.",
        "Super easy to set up and use. Excellent value for money.",
        "I was pleasantly surprised by how well this works.",
        "Best purchase I've made all year. Highly recommended!",
        "Fits perfectly and looks great. Very happy with it.",
        "Customer service was excellent and the product is top notch."
    ] * 500  # Multiply to get enough data for TF-IDF

    negative_reviews = [
        "Terrible quality, broke after one day of use.",
        "Do not buy this. Complete waste of money.",
        "Arrived damaged and customer service was unhelpful.",
        "Very disappointed. Doesn't work as advertised.",
        "Too expensive for what it is. Would not recommend.",
        "Fell apart within a week. Poor construction.",
        "The battery dies after 10 minutes. Useless.",
        "Save your money. This is a scam.",
        "It stopped working completely after a month.",
        "Worst product ever. Returning it immediately."
    ] * 500
    
    train_texts = positive_reviews + negative_reviews
    train_labels = [1] * len(positive_reviews) + [0] * len(negative_reviews)
    
    train_df = pd.DataFrame({'text': train_texts, 'label': train_labels})
    
    # Shuffle the dataset
    train_df = train_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Split into train and test
    split_idx = int(0.8 * len(train_df))
    
    X_train = train_df['text'][:split_idx]
    y_train = train_df['label'][:split_idx]
    
    X_test = train_df['text'][split_idx:]
    y_test = train_df['label'][split_idx:]
    
    print("Vectorizing text using TF-IDF...")
    vectorizer = TfidfVectorizer(max_features=10000, stop_words='english')
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training Logistic Regression model...")
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train_vec, y_train)
    
    print("Evaluating model...")
    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"Accuracy: {acc:.4f}")
    print("Classification Report:")
    print(classification_report(y_test, y_pred, target_names=["Negative", "Positive"]))
    
    print("Saving model and vectorizer...")
    os.makedirs(os.path.dirname(os.path.abspath(__file__)), exist_ok=True)
    joblib.dump(model, 'model.pkl')
    joblib.dump(vectorizer, 'vectorizer.pkl')
    print("Done! Model and vectorizer saved as model.pkl and vectorizer.pkl")

if __name__ == "__main__":
    main()
