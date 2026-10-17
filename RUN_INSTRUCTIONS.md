# HealthSense: Running and Research Handoff Guide

## What this project is

HealthSense is a multi-disease supervised machine-learning research prototype. It contains three separate prediction tasks:

1. Diabetes
2. Heart Disease
3. Chronic Kidney Disease (CKD)

It is an educational/research application, not a medical diagnostic, treatment, or clinical decision-support system. Model outputs are model-estimated research results, not real-world medical probabilities or diagnoses.

The saved production artifacts are already trained. Starting the application loads those artifacts; it does not retrain models.

## Required software

The verified local environment used Python 3.14.3, Node.js 24.13.1, and npm 11.8.0. Use a supported Python 3.x installation compatible with the pinned/current packages in `backend/requirements.txt`; Python 3.14.3 was the verified version. Node.js 24.13.1 and npm 11.8.0 were verified for the frontend.

No separate database server is required for the default setup. SQLite is used locally.

## Project structure

- `backend/`: FastAPI application, authentication, API routes, SQLAlchemy models, schemas, and services.
- `backend/ml/`: disease-specific training code, prediction service, model registry, validation code, and saved artifacts.
- `backend/ml/models/diabetes/`: Diabetes `research_v1` bundle and metadata.
- `backend/ml/models/heart/`: Heart Disease `research_v1` bundle and metadata.
- `backend/ml/models/ckd/`: CKD `research_v1` bundle and metadata.
- `backend/datasets/<disease>/original/`: preserved source datasets. Heart and CKD sources are included locally. Diabetes was trained from the remote Plotly CSV URL recorded in its metadata and training script; no local Diabetes CSV is currently included.
- `backend/datasets/<disease>/processed/`: processed-data locations where present.
- `experiments/`: controlled experiment runner and result files.
- `frontend/`: React/Vite application source and dependency manifests.
- `MODEL_CARD.md`, `EXPERIMENTS.md`, `EXPERIMENT_LOG.md`, `LIMITATIONS.md`, and `RESEARCH_GAP_ANALYSIS.md`: research methods, results, limitations, and proposed research interpretation.
- `backend/healthsense.db`: local SQLite database generated/updated by backend startup. Treat an existing copy as local state, not as required source data.

## Windows PowerShell setup

From the extracted project root:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
Set-Location frontend
npm install
Set-Location ..
```

If PowerShell blocks activation for the current process, run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
.\.venv\Scripts\Activate.ps1
```

Activation is optional when using the direct executable path `.\.venv\Scripts\python.exe`.

## Environment variables

The backend reads `backend/.env`. Copy the safe template before starting:

```powershell
Copy-Item backend\.env.example backend\.env
```

Edit `backend/.env` and replace the placeholder `SECRET_KEY` with a long random value. Never commit or share `backend/.env`.

Variables:

- `SECRET_KEY`: required for production; use a private random value. Development has a built-in development-only fallback, but setting this value is recommended.
- `ENVIRONMENT`: optional; use `development` locally or `production` when deploying. Production refuses to start without `SECRET_KEY`.
- `DATABASE_URL`: optional; defaults to `backend/healthsense.db`. Use a local SQLite URL or another SQLAlchemy-compatible database URL if intentionally configured.
- `ACCESS_TOKEN_EXPIRE_MINUTES`: optional; defaults to `60`.
- `FRONTEND_ORIGINS`: optional; comma-separated browser origins. The default allows `http://127.0.0.1:5173` and `http://localhost:5173`.

No secret values are included in this guide or in `backend/.env.example`.

## Models and reproducibility

Do not retrain models to run the application. The API loads:

- `backend/ml/models/diabetes/model_bundle.joblib`
- `backend/ml/models/heart/model_bundle.joblib`
- `backend/ml/models/ckd/model_bundle.joblib`

Each bundle includes the fitted preprocessing pipeline and metadata. The matching `metadata.json` and `model_comparison.json` files document the model version, feature contract, dataset, evaluation, and limitations. Do not replace these artifacts or the original datasets during ordinary application use.

## Database behavior

The default database is SQLite at `backend/healthsense.db`. On backend import/startup, SQLAlchemy creates missing tables. The application also checks the `predictions` table and adds required legacy-compatible columns when needed. User, profile, and prediction records are isolated by authenticated user ID. A fresh database is created automatically if no database file exists.

## Start the application

Open two PowerShell terminals at the project root.

Terminal 1, backend:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

Terminal 2, frontend:

```powershell
Set-Location frontend
npm run dev -- --host 127.0.0.1 --port 5173
```

Keep both terminals running. The expected application URL is:

`http://127.0.0.1:5173/`

The backend health check is:

`http://127.0.0.1:8000/health`

## Basic usage

1. Open the frontend URL.
2. Register a new account.
3. Sign in.
4. Open **Disease Assessment**.
5. Choose Diabetes, Heart Disease, or CKD from the dashboard model card or assessment route.
6. Enter only the required fields shown for that disease-specific saved model. Do not invent or reuse values for research reporting.
7. Run the assessment.
8. Review the research result, model-estimated score/class, model version, and feature importance.
9. Open **Prediction History** to review saved outputs for the current account.
10. Open **Model & Research** to inspect datasets, methodology, metrics, feature contracts, and limitations.
11. Use **Profile** for reference information and **Settings** for appearance and account controls.

Results are educational/research outputs. Do not use them to diagnose a condition, change medication or treatment, or make urgent-care decisions.

## Troubleshooting

### `Failed to fetch`

Ensure both terminals are running. Check `http://127.0.0.1:8000/health`, then reload `http://127.0.0.1:5173/`. If the frontend uses another API URL, set `VITE_API_URL` in `frontend/.env` and restart Vite.

### Backend will not start

Activate the virtual environment and reinstall `backend/requirements.txt`. Check that `backend/.env` is valid. In production, set a real private `SECRET_KEY`; never copy a secret from another environment.

### Frontend dependencies fail

From `frontend/`, run `npm install` using the included `package.json` and `package-lock.json`. Use a current supported Node.js/npm installation and retry after correcting the reported package error.

### Port already in use

Use another port for the affected service. For the frontend, update `FRONTEND_ORIGINS` and `VITE_API_URL` consistently. For example, run Vite on `5174` and allow `http://127.0.0.1:5174` in `FRONTEND_ORIGINS`.

### Missing `.env`

Copy `backend/.env.example` to `backend/.env`, set a private `SECRET_KEY`, and restart the backend. Do not put real secrets in documentation or the ZIP.

### Missing model artifact

Confirm the appropriate `model_bundle.joblib` exists under `backend/ml/models/diabetes/`, `backend/ml/models/heart/`, or `backend/ml/models/ckd/`. Restore the missing release file from the handoff copy; do not retrain or substitute another disease's model.

### Database initialization issue

Stop the backend, verify that `DATABASE_URL` points to a writable location, and restart. For a disposable local test database only, remove the generated `backend/healthsense.db` and let startup recreate it. Preserve any database needed for research records before doing this.

### Reproducibility note

The Diabetes training source is remote (`https://raw.githubusercontent.com/plotly/datasets/master/diabetes.csv`) and is recorded in the artifact metadata and training script. The release audit found no local Diabetes original CSV, so a fully offline retraining reproduction would require obtaining that source separately. This does not affect normal prediction use because the trained bundle is included.
