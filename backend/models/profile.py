from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship

from backend.database.base import Base
from backend.models.user import User


class PatientProfile(Base):
    __tablename__ = "patient_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(32), nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    smoking = Column(String(8), nullable=True)
    alcohol = Column(String(8), nullable=True)
    activity = Column(String(32), nullable=True)
    family_history = Column(String(8), nullable=True)

    user = relationship("User", backref="profile")
