import sqlite3
from database import connect_db

conn = connect_db()
cursor = conn.cursor()

# Migrate existing admins
cursor.execute("SELECT id FROM users WHERE role = 'admin'")
admins = cursor.fetchall()

for admin in admins:
    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (admin[0],))

conn.commit()
conn.close()

print("Migration completed!")