import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'instance', 'app.db')
if not os.path.exists(db_path):
    print("instance/app.db not found, trying app.db")
    db_path = os.path.join(os.path.dirname(__file__), 'app.db')

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE opportunity ADD COLUMN is_urgent BOOLEAN DEFAULT 0")
    conn.commit()
    print("Added is_urgent column successfully.")
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
