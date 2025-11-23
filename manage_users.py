import sqlite3

DB = "rankpost.db"

def list_users(cur):
    cur.execute("SELECT id, email FROM users ORDER BY id;")
    rows = cur.fetchall()
    if not rows:
        print("⚠️ No users found.")
        return []
    print("\n📋 Current Users:")
    for r in rows:
        print(f"[{r[0]}] {r[1]}")
    return rows

def delete_users(cur, ids_to_delete):
    for uid in ids_to_delete:
        cur.execute("SELECT id, email FROM users WHERE id = ?", (uid,))
        row = cur.fetchone()
        if row:
            print("🗑️ Deleting:", row)
            cur.execute("DELETE FROM users WHERE id = ?", (uid,))
        else:
            print(f"⚠️ User ID {uid} not found.")

def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()

    rows = list_users(cur)
    if not rows:
        return

    choice = input("\n👉 Enter user IDs to delete (comma separated, e.g. 2,3,5): ").strip()
    if choice:
        try:
            ids_to_delete = [int(x.strip()) for x in choice.split(",") if x.strip().isdigit()]
            if ids_to_delete:
                delete_users(cur, ids_to_delete)
                conn.commit()
                print("\n✅ Delete process complete.")
            else:
                print("⚠️ No valid IDs entered.")
        except Exception as e:
            print("❌ Error:", e)

    conn.close()

if __name__ == "__main__":
    main()
