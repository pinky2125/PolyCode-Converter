import sqlite3

# Connect to database
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Create new users table without role
cursor.execute('''
CREATE TABLE users_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
''')

# Copy data from old table
cursor.execute('''
INSERT INTO users_new (id, name, email, password)
SELECT id, name, email, password FROM users
''')

# Drop old table
cursor.execute('DROP TABLE users')

# Rename new table
cursor.execute('ALTER TABLE users_new RENAME TO users')

# Commit and close
conn.commit()
conn.close()

print("✅ Users table migrated: role column removed")