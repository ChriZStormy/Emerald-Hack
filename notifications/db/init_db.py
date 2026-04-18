import sqlite3
import json
import os

def init_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "BD.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            frecuencia TEXT NOT NULL,
            flags TEXT NOT NULL
        )
    """)
    # Insert test data
    try:
        cursor.execute(
            "INSERT INTO Usuario (email, frecuencia, flags) VALUES (?, ?, ?)",
            ("roberleonlan@gmail.com", "semanal", json.dumps(["competencia", "tendencias"]))
        )
    except sqlite3.IntegrityError:
        pass # Already exists
    
    conn.commit()
    conn.close()
    print("Database BD.db initialized with Usuario table.")

if __name__ == "__main__":
    init_db()
