## RankPost Backend — Fixed Package Quickstart

### 1) Create and activate venv
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
```

### 2) Install deps
```bash
pip install -r requirements.txt
```

### 3) Verify .env
The `.env` is included. It points DATABASE_URL to `sqlite:///./sql_app.db`. Keep it.

### 4) Initialize DB migrations
```bash
alembic upgrade head
```

### 5) Run server
```bash
python -m uvicorn app.main:app --reload
```

### Notes
- If you previously created a different SQLite file, delete it to avoid schema mismatch.
- Auth endpoints: /api/v1/auth/signup and /api/v1/auth/login
- Sites and content routes are under /api/v1/
