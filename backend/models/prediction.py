from datetime import datetime

from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import relationship

from backend.database.base import Base
from backend.models.user import User


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    disease = Column(String(64), nullable=False, default="diabetes")
    glucose = Column(Float, nullable=False)
    blood_pressure = Column(Float, nullable=False)
    insulin = Column(Float, nullable=False)
    bmi = Column(Float, nullable=False)
    hba1c = Column(Float, nullable=True)
    risk_percentage = Column(Float, nullable=False)
    risk_level = Column(String(32), nullable=False)
    model_name = Column(String(64), nullable=False, default="research_model")
    model_version = Column(String(64), nullable=False, default="research_v1")
    created_at = Column(DateTime, default=datetime.utcnow)
    input_data = Column(JSON, nullable=True)

    user = relationship("User", backref="predictions")
