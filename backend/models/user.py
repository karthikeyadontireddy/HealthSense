from sqlalchemy import Column, Integer, String
from backend.database.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(128), nullable=False)
    email = Column(String(256), nullable=False, unique=True, index=True)
    password_hash = Column(String(256), nullable=False)
