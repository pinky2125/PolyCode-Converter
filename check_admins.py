import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# Check admins
c.execute('SELECT users.name, users.email FROM users JOIN admins ON users.id = admins.user_id')
admins = c.fetchall()

print('Current Admins:')
if admins:
    for admin in admins:
        print(f'- {admin[0]} ({admin[1]})')
else:
    print('No admins found in database')

# Check total users
c.execute('SELECT COUNT(*) FROM users')
user_count = c.fetchone()[0]
print(f'\nTotal Users: {user_count}')

conn.close()