import sqlite3
import sys

if len(sys.argv) < 2:
    print("Usage: python make_admin.py <email>")
    sys.exit(1)

email_target = sys.argv[1]

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE users
SET role = 'admin'
WHERE email = ?
""", (email_target,))

conn.commit()
conn.close()

print(f"✅ Admin set for {email_target}")