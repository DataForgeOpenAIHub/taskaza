from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=True)
    display_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    verification_token = Column(String, unique=True, index=True, nullable=True)
    verification_token_expires = Column(DateTime, nullable=True)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
