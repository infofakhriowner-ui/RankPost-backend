from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
)
from app.models.user import User
from app.core.config import settings
import requests
import urllib.parse

router = APIRouter(prefix="/social", tags=["Social Auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


@router.get("/google/login")
def google_login():
    client_id = settings.GOOGLE_CLIENT_ID
    redirect_uri = settings.GOOGLE_REDIRECT_URI

    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent",
    }

    url = GOOGLE_AUTH_URL + "?" + urllib.parse.urlencode(params)

    return RedirectResponse(url)


@router.get("/google/callback")
def google_callback(
    code: str = Query(None),
    db: Session = Depends(get_db)
):
    client_id = settings.GOOGLE_CLIENT_ID
    client_secret = settings.GOOGLE_CLIENT_SECRET
    redirect_uri = settings.GOOGLE_REDIRECT_URI

    data = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
    }

    token_resp = requests.post(GOOGLE_TOKEN_URL, data=data)
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get tokens")

    tokens = token_resp.json()
    access_token_google = tokens.get("access_token")

    # --- GOOGLE USER INFO ---
    userinfo_resp = requests.get(
        GOOGLE_USERINFO_URL,
        headers={"Authorization": f"Bearer {access_token_google}"}
    )
    userinfo = userinfo_resp.json()

    email = userinfo.get("email")
    name = userinfo.get("name", "")

    if not email:
        raise HTTPException(status_code=400, detail="No email returned by Google")

    # ---- Find or create user ----
    user = db.query(User).filter(User.email == email).first()
    if not user:
        user = User(
            email=email,
            hashed_password=hash_password("google-temp"),
            credits=5
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    # ---- Generate JWT ----
    jwt_access = create_access_token(email)
    jwt_refresh = generate_refresh_token()
    user.refresh_token_hash = hash_password(jwt_refresh)

    db.add(user)
    db.commit()

    # ---- Redirect back to frontend ----
    frontend_url = "https://rankpost.net/callback"
    redirect = (
        f"{frontend_url}?access_token={jwt_access}"
        f"&refresh_token={jwt_refresh}"
        f"&provider=google"
    )

    return RedirectResponse(redirect)
