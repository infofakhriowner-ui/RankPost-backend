from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.post import GeneratedPost
from app.models.user import User
from app.routers.auth import get_current_user

router = APIRouter(tags=["Posts"])

# ==========================
# 📌 Get All Posts for Logged-In User
# ==========================
@router.get("/", response_model=list[dict])
def list_posts(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    posts = (
        db.query(GeneratedPost)
        .filter(GeneratedPost.user_id == user.id)
        .order_by(GeneratedPost.created_at.desc())
        .all()
    )

    return [
        {
            "id": p.id,
            "title": p.title,
            "keyword": p.keyword,
            "style": p.style,
            "wp_post_url": p.wp_post_url,
            "site_name": p.site_name,
            "has_image": p.has_image,
            "created_at": p.created_at,
        }
        for p in posts
    ]

# ==========================
# 📌 Save Post After Publishing
# (Called automatically from /content/auto-publish)
# ==========================
def save_generated_post(
    db: Session,
    user_id: int,
    site_id: int,
    site_name: str,
    title: str,
    keyword: str,
    style: str,
    wp_post_url: str,
    has_image: bool,
):
    """
    Utility function to save a newly published post to the database.
    This will be imported and called from content.py
    """
    post = GeneratedPost(
        user_id=user_id,
        site_id=site_id,
        site_name=site_name,
        title=title,
        keyword=keyword,
        style=style,
        wp_post_url=wp_post_url,
        has_image=has_image,
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return post
