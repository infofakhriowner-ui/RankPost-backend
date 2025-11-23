from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.sql import func
from app.core.db import Base

class WordPressSite(Base):
    __tablename__ = "wp_sites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    wp_url = Column(String(255), nullable=False)
    wp_user = Column(String(255), nullable=False)
    wp_app_pass_enc = Column(Text, nullable=False)
    style = Column(String(100), nullable=True)
    site_name = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<WordPressSite id={self.id} url={self.wp_url} user_id={self.user_id}>"
