# delete_old_site.py
from app.core.db import SessionLocal
from app.models.site import WordPressSite

db = SessionLocal()

site = db.query(WordPressSite).filter(WordPressSite.id == 1).first()
if site:
    db.delete(site)
    db.commit()
    print("✅ Old site with ID=1 deleted successfully.")
else:
    print("⚠️ No site found with ID=1.")

db.close()
