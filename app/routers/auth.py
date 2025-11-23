from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.user import User
from app.schemas.auth import SignupIn, LoginIn, TokenOut, RefreshIn
from app.core.security import hash_password, verify_password, create_access_token, generate_refresh_token, verify_refresh_token, verify_access_token

router = APIRouter(tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

# -------------------------
# Get current user
# -------------------------
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    email = verify_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# -------------------------
# Signup
# -------------------------
@router.post("/signup", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupIn, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password)
    )

    # ⭐ Give free trial credits
    user.credits = 5  # feel free to change to 10, etc.

    refresh_token = generate_refresh_token()
    user.refresh_token_hash = hash_password(refresh_token)

    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = create_access_token(user.email)
    return TokenOut(access_token=access_token, refresh_token=refresh_token)

# -------------------------
# Login
# -------------------------
@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    access_token = create_access_token(user.email)
    refresh_token = generate_refresh_token()
    user.refresh_token_hash = hash_password(refresh_token)

    db.add(user)
    db.commit()
    return TokenOut(access_token=access_token, refresh_token=refresh_token)

# -------------------------
# Refresh Token
# -------------------------
@router.post("/refresh", response_model=TokenOut)
def refresh_token(payload: RefreshIn, db: Session = Depends(get_db)):
    if not payload.refresh_token:
        raise HTTPException(status_code=400, detail="Missing refresh token")

    users = db.query(User).all()
    for user in users:
        if user.refresh_token_hash and verify_refresh_token(payload.refresh_token, user.refresh_token_hash):
            access_token = create_access_token(user.email)
            new_refresh = generate_refresh_token()
            user.refresh_token_hash = hash_password(new_refresh)

            db.add(user)
            db.commit()
            return TokenOut(access_token=access_token, refresh_token=new_refresh)

    raise HTTPException(status_code=401, detail="Invalid refresh token")
