import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

sqlite_path = BASE_DIR / "healthsense.db"
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{sqlite_path}")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
	if ENVIRONMENT == "production":
		raise RuntimeError("SECRET_KEY must be configured in production.")
	SECRET_KEY = "development-only-change-this-secret"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
FRONTEND_ORIGINS = [origin.strip() for origin in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:5174,http://127.0.0.1:5174").split(",") if origin.strip()]
