# init_db.py
import sqlite3

DB_PATH = "app/db.sqlite3"

schema = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS wp_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    site_url TEXT NOT NULL,
    wp_user TEXT NOT NULL,
    app_password TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS generated_posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    site_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    published_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id),
    FOREIGN KEY(site_id) REFERENCES wp_sites(id)
);
"""

if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript(schema)
    conn.commit()
    conn.close()
    print("✅ Database initialized with users, wp_sites, and generated_posts tables.")
