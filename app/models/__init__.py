# app/models/__init__.py
from sqlalchemy.orm import declarative_base

# ✅ Base class for all models
Base = declarative_base()

# ✅ Import all models so Alembic / create_all can detect them
from .user import User
from .site import WordPressSite
from .post import GeneratedPost
