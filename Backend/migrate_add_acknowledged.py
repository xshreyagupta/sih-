"""
One-off migration: adds the 'acknowledged' column to the alerts table
in urban.db, without deleting any existing data.

Run this ONCE from the same folder as urban.db, with the server stopped:

    python migrate_add_acknowledged.py
"""

import sqlite3

DB_PATH = "urban.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(alerts)")
columns = [row[1] for row in cursor.fetchall()]

if "acknowledged" in columns:
    print("Column 'acknowledged' already exists on 'alerts'. Nothing to do.")
else:
    cursor.execute(
        "ALTER TABLE alerts ADD COLUMN acknowledged BOOLEAN NOT NULL DEFAULT 0"
    )
    conn.commit()
    print("Added 'acknowledged' column to 'alerts' table successfully.")

conn.close()
