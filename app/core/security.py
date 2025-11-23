from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.core.config import settings
import secrets

# -------------------------
# Config
# -------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


# -------------------------
# Password Hashing
# -------------------------
def hash_password(password: str) -> str:
    """Hash a plain password"""
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    """Verify a plain password against hashed value"""
    return pwd_context.verify(plain, hashed)


# -------------------------
# JWT Access Tokens
# -------------------------
def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    """
    Create a JWT access token
    :param subject: usually the user's email or id
    :param expires_minutes: optional expiry override
    """
    expire = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes or settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": subject, "exp": expire.timestamp()}
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=ALGORITHM)

def verify_access_token(token: str) -> str:
    """
    Decode and verify JWT token
    Returns the 'sub' if valid, raises JWTError if invalid
    """
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


# -------------------------
# Refresh Tokens
# -------------------------
def generate_refresh_token() -> str:
    """Generate a secure random refresh token"""
    return secrets.token_urlsafe(48)

def verify_refresh_token(token: str, hashed: str) -> bool:
    """Verify a refresh token against its hashed value"""
    return pwd_context.verify(token, hashed)
