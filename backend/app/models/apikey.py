from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.db.session import Base


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    hashed_key = Column(String, unique=True, nullable=False, index=True)
    prefix = Column(String, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    revoked = Column(Boolean, default=False, nullable=False)
    last_used_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")
