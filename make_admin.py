import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
UPDATE users
SET role = 'admin'
WHERE email = 'reshmapal5131@gmail.com'
""")

conn.commit()
conn.close()

print("✅ Admin set ho gaya")