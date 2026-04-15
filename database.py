import sqlite3

def connect_db():
    conn = sqlite3.connect('database.db')
    return conn


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # 👤 Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user'
        )
    ''')

    # 🔁 Conversion history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            source_language TEXT,
            target_language TEXT,
            source_code TEXT,
            converted_code TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # 🌐 Languages table (NEW 🔥)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS languages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        icon TEXT,
        version TEXT
    )
''')

    # ✅ Default languages insert (important)
    cursor.execute("""
    INSERT OR IGNORE INTO languages (name, icon, version)
    VALUES ('python', '🐍', '3.12')
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO languages (name, icon, version)
    VALUES ('java', '☕', '17')
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO languages (name, icon, version)
    VALUES ('c', '⚙️', 'C99')
    """)
    cursor.execute("""
    INSERT OR IGNORE INTO languages (name, icon, version)
    VALUES ('cpp', '🅲++', '17')
    """)

    conn.commit()
    conn.close()


def save_history(user_id, source_lang, target_lang, source_code, converted_code):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO history 
        (user_id, source_language, target_language, source_code, converted_code)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, source_lang, target_lang, source_code, converted_code))

    conn.commit()
    conn.close()


def get_history(user_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    rows = cursor.fetchall()
    conn.close()
    return rows


# 🔥 NEW FUNCTION (languages get karne ke liye)
def get_languages():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM languages")
    languages = cursor.fetchall()

    conn.close()
    return languages