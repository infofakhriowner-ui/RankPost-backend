# show_sites.py

import sqlite3

DB_PATH = "app/db.sqlite3"  # agar DB ka naam ya path alag ho to change kar lena

def show_sites():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Tables check
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cur.fetchall()]
    print("Tables in database:", tables)

    if "wp_sites" not in tables:
        print("⚠️ wp_sites table not found!")
        return

    # Show all sites
    try:
        cur.execute("SELECT id, site_name, wp_url, wp_user FROM wp_sites;")
        rows = cur.fetchall()
        print("\nRegistered Sites:")
        for r in rows:
            print(f"- ID: {r[0]} | Name: {r[1]} | URL: {r[2]} | User: {r[3]}")
    except Exception as e:
        print("Error reading wp_sites:", e)

    conn.close()


if __name__ == "__main__":
    show_sites()
