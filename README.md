# HealthSense

HealthSense is a supervised machine-learning healthcare analytics research prototype for diabetes, heart disease, and chronic kidney disease risk prediction. It is designed for educational and experimental use; it is not an AI/LLM system and is not a medical diagnostic tool.

> This application is an educational/research prototype for machine-learning-based risk prediction. It is not a medical diagnostic or treatment tool.

## Features

- User registration and login
- Patient profile management
- Manual health data entry
- Disease-specific prediction for Diabetes, Heart Disease, and Chronic Kidney Disease
- Saved model metadata, evaluation metrics, and feature-importance transparency
- Prediction history tracking
- Research-oriented dashboard with model status and assessment history

## Production model reproducibility

The API loads three independently trained bundles from
`backend/ml/models/<disease>/model_bundle.joblib`. Prediction never trains a
model. Each bundle contains its fitted preprocessing pipeline and metadata.

### Diabetes

- Source: `https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv`
- Target: `Outcome` (binary classification)
- Features, in order: `Glucose`, `BloodPressure`, `Insulin`, `BMI`, `Age`
- Dataset size: 768 rows; stratified 80/20 train/test split (614/154 rows)
- Selected model: Logistic Regression, version `research_v1`

Heart Disease and CKD use their own feature contracts, preprocessing pipelines,
datasets, and `research_v1` artifacts. Their complete features, sample counts,
metrics, methodology, and limitations are available in the Model & Research
screen and in `MODEL_CARD.md`.

All reported outputs are model-estimated results for research and educational
use. Calibration has not been fitted, so scores must not be interpreted as
real-world medical probabilities or a medical diagnosis.

## Tech Stack

- Frontend: React, Vite, Tailwind CSS
- Backend: FastAPI
- ML: Python, Scikit-learn, Pandas, Joblib
- Database: SQLite

## Folder Structure

- `frontend/` - React application
- `backend/` - FastAPI server and ML utilities

Original datasets are immutable and stored under `backend/datasets/<disease>/original/`.
Each disease has an independent offline training pipeline and saved model artifact.
Models are not trained automatically by the API, and metrics are reported only
after an actual training run.

## Getting Started

### Backend

1. Install dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
2. Use the default SQLite configuration in `backend/config.py` unless you intentionally override `DATABASE_URL`.
3. Start the backend server:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend

1. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
2. Start the frontend dev server:
   ```bash
   npm run dev
   ```

### Default Backend URL

The frontend uses `http://127.0.0.1:8000` by default. Update `frontend/.env` or `VITE_API_URL` if needed.
