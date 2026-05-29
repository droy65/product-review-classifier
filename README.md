# Product Review Classifier

A Machine Learning based Product Review Classifier application that predicts sentiment/review category using a FastAPI backend and Streamlit frontend.

---

# Tech Stack

* Python
* FastAPI
* Streamlit
* Scikit-learn
* Docker
* Docker Compose

---

# Project Structure

```text
product_review_classifier/
│
├── api/                 # FastAPI backend
├── frontend/            # Streamlit frontend
├── model/               # Trained ML models
├── docker-compose.yml
├── README.md
```

---

# Features

* Product review classification
* FastAPI REST backend
* Streamlit interactive UI
* Dockerized application
* Easy deployment and setup

---

# Clone Repository

```bash
git clone https://github.com/droy65/product-review-classifier.git
```

Move into project folder:

```bash
cd product-review-classifier
```

---

# Run Using Docker (Recommended)

## Prerequisites

Install:

* Docker Desktop

Check Docker installation:

```bash
docker --version
docker compose version
```

---

## Start Application

```bash
docker compose up --build
```

---

## Access Application

### Frontend (Streamlit)

```text
http://localhost:8501
```

### Backend API

```text
http://localhost:8000
```

---

## Stop Containers

Press:

```text
Ctrl + C
```

Then run:

```bash
docker compose down
```

---

# Manual Setup (Without Docker)

## Create Virtual Environment

### Windows

```bash
python -m venv .venv
```

Activate environment:

```bash
.\.venv\Scripts\activate
```

---

# Install Dependencies

## Backend Requirements

```bash
pip install -r api/requirements.txt
```

## Frontend Requirements

```bash
pip install -r frontend/requirements.txt
```

---

# Run Backend

Move to API folder:

```bash
cd api
```

Start FastAPI server:

```bash
uvicorn main:app --reload
```

Backend runs on:

```text
http://127.0.0.1:8000
```

---

# Run Frontend

Open a NEW terminal.

Move to project folder:

```bash
cd product-review-classifier
```

Activate environment:

```bash
.\.venv\Scripts\activate
```

Run Streamlit app:

```bash
streamlit run frontend/app.py --server.port=8501
```

Frontend runs on:

```text
http://localhost:8501
```

---

# API Endpoint

## Predict Review

```http
POST /predict
```


# Example Technologies Used

* FastAPI
* Streamlit
* Scikit-learn
* Pandas
* NumPy
* Docker



GitHub:
https://github.com/droy65
