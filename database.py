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
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # 👑 Admins table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            permissions TEXT DEFAULT 'full',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
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

    # 💡 Solutions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS solutions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            history_id INTEGER,
            user_id INTEGER,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(history_id) REFERENCES history(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # 📝 Suggestions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            history_id INTEGER,
            user_id INTEGER,
            content TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(history_id) REFERENCES history(id),
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

    # 💬 Feedback table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            email TEXT,
            rating INTEGER,
            message TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
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
    
    history_id = cursor.lastrowid

    conn.commit()
    conn.close()
    
    return history_id


def save_solution(history_id, user_id, content):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO solutions (history_id, user_id, content) VALUES (?, ?, ?)
    """, (history_id, user_id, content))
    conn.commit()
    conn.close()


def save_suggestion(history_id, user_id, content):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO suggestions (history_id, user_id, content) VALUES (?, ?, ?)
    """, (history_id, user_id, content))
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


def save_feedback(user_id, name, email, rating, message):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO feedback (user_id, name, email, rating, message) VALUES (?, ?, ?, ?, ?)
    """, (user_id, name, email, rating, message))
    conn.commit()
    conn.close()


def get_all_feedback():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT feedback.id, users.name, feedback.name, feedback.email, feedback.rating, feedback.message, feedback.timestamp
        FROM feedback
        LEFT JOIN users ON feedback.user_id = users.id
        ORDER BY feedback.id DESC
    """)
    feedbacks = cursor.fetchall()
    conn.close()
    return feedbacks


def is_admin(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM admins WHERE user_id = ?", (user_id,))
    admin = cursor.fetchone()
    conn.close()
    return admin is not None


def make_admin(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO admins (user_id) VALUES (?)", (user_id,))
    conn.commit()
    conn.close()


def get_users_with_admin_status():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT users.id, users.name, users.email, CASE WHEN admins.id IS NOT NULL THEN 'admin' ELSE 'user' END as role
        FROM users
        LEFT JOIN admins ON users.id = admins.user_id
    """)
    users = cursor.fetchall()
    conn.close()
    return users