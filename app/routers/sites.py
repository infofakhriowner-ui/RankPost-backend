from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.site import WordPressSite
from app.models.user import User
from app.schemas.site import SiteCreate, SiteOut
from app.routers.auth import get_current_user
from app.services.crypto import encrypt_text
import requests

router = APIRouter()


# ---------------------------------------------------
# Utility: Validate WordPress Credentials
# ---------------------------------------------------
def check_wp_connection(url: str, user: str, app_password: str) -> bool:
    """
    Check if WordPress credentials are valid.
    """
    try:
        wp_url = str(url).rstrip("/") + "/wp-json/wp/v2/posts"

        res = requests.get(wp_url, auth=(user, app_password), timeout=10)

        # Unauthorized → invalid credentials
        if res.status_code == 401:
            return False

        # Any non-success except empty posts
        if res.status_code not in [200, 201]:
            return False

        # Should be valid JSON
        try:
            data = res.json()
        except:
            return False

        # Normal WordPress response (list of posts)
        if isinstance(data, list):
            if len(data) == 0:
                return True
            if isinstance(data[0], dict) and ("id" in data[0] or "title" in data[0]):
                return True

        # Single dictionary post
        if isinstance(data, dict) and ("id" in data or "title" in data):
            return True

        return False

    except Exception as e:
        print("WP check failed:", str(e))
        return False


# ---------------------------------------------------
# GET: List all sites for logged-in user
# ---------------------------------------------------
@router.get("/", response_model=list[SiteOut])
def list_sites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(WordPressSite).filter(WordPressSite.user_id == user.id).all()


# ---------------------------------------------------
# GET: Single site detail (REQUIRED by frontend)
# ---------------------------------------------------
@router.get("/{site_id}", response_model=SiteOut)
def get_site(site_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    site = db.query(WordPressSite).filter(
        WordPressSite.id == site_id,
        WordPressSite.user_id == user.id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    return site


# ---------------------------------------------------
# POST: Add new site
# ---------------------------------------------------
@router.post("/add", response_model=SiteOut)
def add_site(payload: SiteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    # Check duplicate
    exists = db.query(WordPressSite).filter(
        WordPressSite.user_id == user.id,
        WordPressSite.wp_url == str(payload.wp_url)
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Site already added")

    # Validate WP login
    is_valid = check_wp_connection(payload.wp_url, payload.wp_user, payload.wp_app_pass_enc)

    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid WordPress credentials or site unreachable.")

    # Save encrypted password
    site = WordPressSite(
        user_id=user.id,
        wp_url=str(payload.wp_url).rstrip("/"),
        wp_user=payload.wp_user,
        wp_app_pass_enc=encrypt_text(payload.wp_app_pass_enc),
        style=payload.style,
        site_name=payload.site_name,
    )

    db.add(site)
    db.commit()
    db.refresh(site)

    return site


# ---------------------------------------------------
# DELETE: Remove a site
# ---------------------------------------------------
@router.delete("/{site_id}")
def delete_site(site_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):

    site = db.query(WordPressSite).filter(
        WordPressSite.id == site_id,
        WordPressSite.user_id == user.id
    ).first()

    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    db.delete(site)
    db.commit()

    return {"message": "Site deleted successfully"}
