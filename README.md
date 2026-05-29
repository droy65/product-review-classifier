# Product Review Classifier

A Machine Learning based Product Review Classifier that uses Natural Language Processing (NLP) techniques to analyze customer reviews and classify sentiments as **Positive**, **Negative**, or **Neutral**. Built using Python, Scikit-learn, Streamlit, FastAPI, Docker, HTML, CSS, and JavaScript for real-time sentiment prediction and customer feedback analysis.

---

## Features

* Sentiment Analysis using Machine Learning
* NLP-based text preprocessing
* Real-time review prediction
* Interactive Streamlit frontend
* Backend API integration
* Docker support for deployment
* Clean and scalable project structure

---

## Tech Stack

### Frontend

* Streamlit
* HTML
* CSS
* JavaScript

### Backend

* FastAPI
* Python

### Machine Learning

* Scikit-learn
* NLP
* Pickle

### Deployment

* Docker
* Docker Compose
* GitHub
* Vercel

---

## Project Structure

```bash
PRODUCT_REVIEW_CLASSIFIER/
│
├── api/
│   ├── main.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── app.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── model/
│   ├── train.py
│   ├── model.pkl
│   ├── vectorizer.pkl
│   └── requirements.txt
│
├── docker-compose.yml
└── README.md
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/product-review-classifier.git
cd product-review-classifier
```

---

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
.venv\Scripts\activate
```

### Linux / Mac

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install Dependencies

### Backend

```bash
cd api
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
pip install -r requirements.txt
```

### Model

```bash
cd model
pip install -r requirements.txt
```

---

## Run Backend Server

```bash
cd api
uvicorn main:app --reload
```

Backend URL:

```bash
http://127.0.0.1:8000
```

---

## Run Frontend

```bash
cd frontend
streamlit run app.py --server.port=8501
```

Frontend URL:

```bash
http://localhost:8501
```

---

## Docker Setup

Run the application using Docker Compose:

```bash
docker-compose up --build
```

---

## Train the Model

```bash
cd model
python train.py
```

This generates:

* `model.pkl`
* `vectorizer.pkl`

---

## Sample Predictions

| Review                                | Sentiment |
| ------------------------------------- | --------- |
| Amazing product and excellent quality | Positive  |
| Worst product I have ever used        | Negative  |
| Product is okay for the price         | Neutral   |

---

## Future Improvements

* Deep Learning integration
* Multi-language sentiment analysis
* User authentication system
* Database integration
* Analytics dashboard
* Cloud deployment support

---

## Author

**Diya Roy**

---

## License

This project is licensed under the MIT License.

