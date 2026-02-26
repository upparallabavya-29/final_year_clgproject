import sqlite3
import os

db_path = os.path.join('data', 'scan_history.db')
conn = sqlite3.connect(db_path)
c = conn.cursor()
try:
    c.execute("ALTER TABLE scans ADD COLUMN image_path TEXT DEFAULT ''")
    conn.commit()
    print('Column image_path added successfully!')
except Exception as e:
    print('Error:', e)
conn.close()
