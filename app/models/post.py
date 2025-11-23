from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean, Text
from sqlalchemy.sql import func
from app.core.db import Base


class GeneratedPost(Base):
    """
    Represents an article auto-generated and published via RankPost.
    Stored after successful publishing to WordPress.
    """
    __tablename__ = "posts"  # ✅ Database table name remains 'posts'

    # ============ Basic Identifiers ============
    id = Column(Integer, primary_key=True, index=True)

    # ============ Relations ============
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    site_id = Column(Integer, ForeignKey("wp_sites.id"), nullable=False)

    # ============ Meta Information ============
    site_name = Column(String(255), nullable=True)  # WordPress site display name
    title = Column(String(255), nullable=False)      # Post title
    keyword = Column(String(255), nullable=False)    # Keyword used for generation
    style = Column(String(100), nullable=True)       # e.g. formal / casual / seo / storytelling

    # ============ Publishing Info ============
    wp_post_url = Column(String(500), nullable=False)  # URL of published post
    has_image = Column(Boolean, default=False)         # Whether AI-generated image was added

    # ============ Timestamps ============
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<GeneratedPost id={self.id} title={self.title} site={self.site_name}>"
