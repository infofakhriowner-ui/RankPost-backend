
# RankPost – FastAPI Backend (MVP)

This is the backend for **RankPost**, a SaaS that generates SEO blog posts with AI and publishes them to users' WordPress sites.

## Tech
- FastAPI
- SQLAlchemy (SQLite for dev)
- JWT auth (python-jose)
- Password hashing (passlib[bcrypt])
- Requests (WordPress REST)
- OpenAI API (text + optional image)

## Quick Start (Local Dev)
1) Create & activate a virtual environment:
```bash
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2) Install deps:
```bash
pip install -r requirements.txt
```

3) Copy env file and fill values:
```bash
cp .env.example .env
# then edit .env to add OPENAI_API_KEY and JWT_SECRET
```

4) Run dev server:
```bash
uvicorn app.main:app --reload
```

5) Open docs:
- http://127.0.0.1:8000/docs

## API Overview
- `POST /auth/signup` – Create account
- `POST /auth/login` – Login, returns JWT
- `POST /sites` – Add a WordPress site (auth required)
- `GET /sites` – List your sites
- `POST /articles/generate` – Get AI article JSON (title + HTML)
- `POST /publish` – Generate (or accept provided article) and publish to chosen WP site

## Notes
- SQLite is used in dev. For production use Postgres (Supabase/Neon).
- WordPress Application Passwords must be enabled on the user's site.
- Never store plaintext secrets; application passwords are encrypted at-rest using Fernet.
