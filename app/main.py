from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.core.db import Base, engine
from app.core.config import settings

# Import models in correct order
from app.models.user import User
from app.models.site import WordPressSite
from app.models.post import GeneratedPost

# Import routers
from app.routers import auth, sites, content, utils, posts, users  # 👈 added users here

# Create tables
Base.metadata.create_all(bind=engine)

# FastAPI app init
app = FastAPI(
    title="RankPost Backend",
    version="0.1.0",
    description="Backend for RankPost SaaS 🚀"
)

origins = [
    "https://rankpost.net",
    "https://www.rankpost.net",
    "https://rank-post-frontend.vercel.app",
]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler
@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc) or "Internal Server Error"}
    )

# Include Routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(sites.router, prefix="/api/v1/sites", tags=["Sites"])
app.include_router(content.router, prefix="/api/v1/content", tags=["Content"])
app.include_router(utils.router, prefix="/api/v1/utils", tags=["Utils"])
app.include_router(posts.router, prefix="/api/v1/posts", tags=["Posts"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])  # 👈 add this

# Root
@app.get("/")
def root():
    return {
        "ok": True,
        "app": "RankPost Backend is running 🚀",
        "version": "0.1.0",
    }
