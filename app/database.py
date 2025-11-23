from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

# Abhi ke liye SQLite use kar rahe hain (ek file rankpost.db banegi project ke andar)
SQLALCHEMY_DATABASE_URL = "sqlite:///./rankpost.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
