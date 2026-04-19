import sqlite3
import json
import os

def init_db():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    db_path = os.path.join(base_dir, "DB.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Usuario (
            Id_Usuario INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            correo TEXT,
            Numero TEXT
        )
    """)
    conn.commit()
    conn.close()
    print("Database DB.db initialized with Usuario table.")

if __name__ == "__main__":
    init_db()
