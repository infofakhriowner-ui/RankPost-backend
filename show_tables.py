from app.core.db import engine
from sqlalchemy import inspect

insp = inspect(engine)
print("📋 Tables in DB:", insp.get_table_names())
