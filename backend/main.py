import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text

from backend.api.auth import router as auth_router
from backend.api.profile import router as profile_router
from backend.api.predict import router as predict_router
from backend.api.history import router as history_router
from backend.database.base import Base
from backend.database.session import SessionLocal, engine
from backend.config import FRONTEND_ORIGINS
from backend.models.user import User
from backend.services.auth import hash_password


def ensure_prediction_schema():
    inspector = inspect(engine)
    if "predictions" not in inspector.get_table_names():
        Base.metadata.create_all(bind=engine)
        return

    existing_columns = {column["name"] for column in inspector.get_columns("predictions")}
    needed_columns = {
        "disease": "VARCHAR(64) DEFAULT 'diabetes'",
        "model_name": "VARCHAR(64) DEFAULT 'research_model'",
        "model_version": "VARCHAR(64) DEFAULT 'research_v1'",
        "input_data": "JSON",
    }

    with engine.begin() as connection:
        for column_name, column_sql in needed_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE predictions ADD COLUMN {column_name} {column_sql}"))


Base.metadata.create_all(bind=engine)
ensure_prediction_schema()


def ensure_default_demo_user():
    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.email == "demo@example.com").first()
        if not existing:
            demo_user = User(
                name="Demo User",
                email="demo@example.com",
                password_hash=hash_password("demo123"),
            )
            db.add(demo_user)
            db.commit()
    finally:
        db.close()


ensure_default_demo_user()

app = FastAPI(
    title="HealthSense",
    description="Educational research prototype for three disease-specific machine-learning risk prediction tasks.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(predict_router)
app.include_router(history_router)


@app.get("/")
def root():
    return {
        "message": "This application is an educational/research prototype for machine-learning-based risk prediction. It is not a medical diagnostic or treatment tool."
    }


@app.get("/health")
def health():
    return {"status": "ok", "service": "HealthSense backend"}
