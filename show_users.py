import sqlite3

# RankPost DB file ka path
DB_PATH = "rankpost.db"   # agar sql_app.db use ho raha ho to isko change kar lena

def main():
    # DB connect karo
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Pehle sab tables dekh lo (debugging ke liye)
    print("Tables in database:")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for t in tables:
        print("-", t[0])

    print("\nTrying to fetch emails...\n")

    # Common table names check karte hain
    possible_tables = ["users", "user", "auth_user"]
    for table in possible_tables:
        try:
            cursor.execute(f"SELECT id, email FROM {table} LIMIT 5;")
            rows = cursor.fetchall()
            if rows:
                print(f"✅ Found data in table: {table}")
                cursor.execute(f"SELECT id, email FROM {table} ORDER BY id DESC;")
                all_rows = cursor.fetchall()
                for r in all_rows:
                    print(r)
                break
        except Exception as e:
            # Agar table nahi mila to ignore
            pass
    else:
        print("⚠️ Could not find users table. Check table list above.")

    conn.close()

if __name__ == "__main__":
    main()
