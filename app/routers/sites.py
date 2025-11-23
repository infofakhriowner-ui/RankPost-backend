from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.site import WordPressSite
from app.models.user import User
from app.schemas.site import SiteCreate, SiteOut
from app.routers.auth import get_current_user
from app.services.crypto import encrypt_text  # ✅ Import encryption
import requests  # ✅ For checking WordPress connection

router = APIRouter()


# -------------------------
# Utility: Check WordPress credentials (strong validation)
# -------------------------
def check_wp_connection(url: str, user: str, app_password: str) -> bool:
    """
    Validates WordPress connection before saving the site.
    Ensures credentials and API access are actually working.
    """
    try:
        wp_url = str(url).rstrip("/") + "/wp-json/wp/v2/posts"
        res = requests.get(wp_url, auth=(user, app_password), timeout=10)

        # Unauthorized → invalid credentials
        if res.status_code == 401:
            return False

        # Redirects or non-OK status → invalid
        if res.status_code not in [200, 201]:
            return False

        # Ensure response is valid JSON (not HTML)
        try:
            data = res.json()
        except Exception:
            return False

        # ✅ Case 1: List of posts (normal WP response)
        if isinstance(data, list):
            if len(data) == 0:
                # empty list = valid WP site with no posts yet
                return True
            elif isinstance(data[0], dict) and ("id" in data[0] or "title" in data[0]):
                return True

        # ✅ Case 2: Single post (dict)
        if isinstance(data, dict) and ("id" in data or "title" in data):
            return True

        # ❌ Anything else = probably HTML/error
        return False

    except Exception as e:
        # Optional: print for debugging (safe to remove in production)
        print("WP check failed:", str(e))
        return False


# -------------------------
# GET list of sites for the logged-in user
# -------------------------
@router.get("/", response_model=list[SiteOut])
def list_sites(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(WordPressSite).filter(WordPressSite.user_id == user.id).all()


# -------------------------
# POST add a new WordPress site (JSON body)
# -------------------------
@router.post("/add", response_model=SiteOut)
def add_site(payload: SiteCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # 🔹 Check if site already exists for this user
    exists = db.query(WordPressSite).filter(
        WordPressSite.user_id == user.id,
        WordPressSite.wp_url == str(payload.wp_url)
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Site already added")

    # 🔹 Validate WordPress credentials before saving
    is_valid = check_wp_connection(payload.wp_url, payload.wp_user, payload.wp_app_pass_enc)
    if not is_valid:
        raise HTTPException(status_code=400, detail="Invalid WordPress credentials or site not reachable.")

    # ✅ Save password as encrypted text (no change to your logic)
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


# -------------------------
# DELETE a WordPress site
# -------------------------
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
