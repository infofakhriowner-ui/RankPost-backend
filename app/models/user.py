from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.sql import func
from app.core.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    refresh_token_hash = Column(String(255), nullable=True)  # 👈 yeh add karo

    # ⭐ NEW FIELD HERE: Credits system
    credits = Column(Integer, default=0)  # Add credits for usage based system

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User id={self.id} email={self.email}>"
