import sqlite3
import os

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
db_path = os.path.join(base_dir, "BD.db")
db = sqlite3.connect(db_path)
c = db.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = c.fetchall()
print('Tables:', tables)
for t in tables:
    c.execute(f"PRAGMA table_info({t[0]})")
    print(t[0], c.fetchall())
    c.execute(f"SELECT * FROM {t[0]} LIMIT 2")
    print("Data:", c.fetchall())
db.close()
