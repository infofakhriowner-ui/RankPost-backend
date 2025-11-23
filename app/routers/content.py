from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.db import get_db
from app.routers.auth import get_current_user
from app.models.site import WordPressSite
from app.models.post import GeneratedPost  # Updated model name
from app.services.openai_client import generate_article, generate_image_b64
from app.services.wordpress import upload_post
from app.services.crypto import decrypt_text

router = APIRouter(tags=["Content"])


# -------------------------
# Request Schema
# -------------------------
class AutoPublishRequest(BaseModel):
    keyword: str
    style: Optional[str] = "formal"
    site_id: int
    with_image: bool = True


# -------------------------
# Auto Publish Article
# -------------------------
@router.post("/auto-publish")
def auto_publish_endpoint(
    req: AutoPublishRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    # ---------------- Credit Check ----------------
    if user.credits is None or user.credits < 1:
        raise HTTPException(status_code=400, detail="NOT_ENOUGH_CREDITS")

    # ---------------- Validate site ----------------
    site = (
        db.query(WordPressSite)
        .filter(WordPressSite.id == req.site_id, WordPressSite.user_id == user.id)
        .first()
    )
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    # ---------------- Generate Article ----------------
    article = generate_article(req.keyword, req.style)
    if not article or not article.get("title") or not article.get("content"):
        raise HTTPException(status_code=500, detail="Failed to generate article")

    title = article["title"]
    content_html = article["content"]

    # ---------------- Generate Image (optional) ----------------
    image_b64 = None
    has_image = False
    if req.with_image:
        try:
            image_b64 = generate_image_b64(req.keyword)
            has_image = bool(image_b64)
        except Exception as e:
            print("Image generation failed:", e)

    # ---------------- Publish to WordPress ----------------
    wp_pass = decrypt_text(site.wp_app_pass_enc)
    url = upload_post(
        wp_url=site.wp_url.rstrip("/"),
        user=site.wp_user,
        app_pass=wp_pass,
        title=title,
        content_html=content_html,
        image_b64=image_b64,
    )

    if not url:
        raise HTTPException(status_code=500, detail="Failed to publish post")

    # ---------------- Deduct 1 Credit ----------------
    user.credits -= 1
    db.commit()

    # ---------------- Save Post in Database ----------------
    new_post = GeneratedPost(
        user_id=user.id,
        site_id=site.id,
        site_name=site.site_name,
        title=title,
        keyword=req.keyword,
        style=req.style,
        wp_post_url=url,
        has_image=has_image,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    # ---------------- Return Response ----------------
    return {
        "url": url,
        "title": title,
        "site": site.site_name,
        "has_image": has_image,
        "remaining_credits": user.credits,  # Useful for frontend update
    }
