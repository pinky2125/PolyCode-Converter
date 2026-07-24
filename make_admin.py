import sqlite3
import sys
from database import connect_db, make_admin

if len(sys.argv) < 2:
    print("Usage: python make_admin.py <email>")
    sys.exit(1)

email_target = sys.argv[1]

conn = connect_db()
cursor = conn.cursor()

cursor.execute("SELECT users.id FROM users JOIN profiles ON users.id = profiles.user_id WHERE profiles.email = ?", (email_target,))
user = cursor.fetchone()
conn.close()

if user:
    make_admin(user[0])
    print(f"✅ Admin set for {email_target}")
else:
    print(f"❌ User not found: {email_target}")