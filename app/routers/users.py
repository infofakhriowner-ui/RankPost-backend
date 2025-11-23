from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.routers.auth import get_current_user
from app.models.user import User

router = APIRouter(tags=["Users"])

@router.get("/me")
def get_me(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return {
        "id": user.id,
        "email": user.email,
        "credits": user.credits,
        "created_at": user.created_at,
    }
