"""
Optimized Database Module with Context Managers and Proper Error Handling
"""
import sqlite3
import logging
from contextlib import contextmanager
from typing import List, Tuple, Optional, Any

logger = logging.getLogger(__name__)

DATABASE_PATH = 'database.db'

@contextmanager
def get_db():
    """Context manager for database connections - ensures proper cleanup"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    except sqlite3.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def create_tables():
    """Create all necessary database tables"""
    with get_db() as conn:
        cursor = conn.cursor()

        # 👤 Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_verified INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # 👤 Profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                name TEXT NOT NULL,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                bio TEXT,
                phone TEXT,
                avatar_url TEXT,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 👑 Admins table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                permissions TEXT DEFAULT 'full',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 🔁 Conversion history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                source_language TEXT NOT NULL,
                target_language TEXT NOT NULL,
                source_code TEXT NOT NULL,
                converted_code TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 💡 Solutions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(history_id) REFERENCES history(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 📝 Suggestions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(history_id) REFERENCES history(id) ON DELETE CASCADE,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # 🌐 Languages table
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
                name TEXT NOT NULL,
                email TEXT NOT NULL,
                rating INTEGER CHECK(rating >= 1 AND rating <= 5),
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')

        # Add indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_feedback_user ON feedback(user_id)')

        # Insert default languages
        cursor.execute("INSERT OR IGNORE INTO languages (name, icon, version) VALUES (?, ?, ?)", 
                      ('python', '🐍', '3.12'))
        cursor.execute("INSERT OR IGNORE INTO languages (name, icon, version) VALUES (?, ?, ?)", 
                      ('java', '☕', '17'))
        cursor.execute("INSERT OR IGNORE INTO languages (name, icon, version) VALUES (?, ?, ?)", 
                      ('c', '⚙️', 'C99'))
        cursor.execute("INSERT OR IGNORE INTO languages (name, icon, version) VALUES (?, ?, ?)", 
                      ('cpp', '🅲++', '17'))

        conn.commit()
        logger.info("Database tables created successfully")


def save_history(user_id: int, source_lang: str, target_lang: str, 
                source_code: str, converted_code: str) -> Optional[int]:
    """Save conversion history and return history ID"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history 
                (user_id, source_language, target_language, source_code, converted_code)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, source_lang, target_lang, source_code, converted_code))
            conn.commit()
            history_id = cursor.lastrowid
            logger.info(f"Conversion history saved with ID: {history_id}")
            return history_id
    except sqlite3.Error as e:
        logger.error(f"Error saving history: {e}")
        return None


def save_solution(history_id: int, user_id: int, content: str) -> bool:
    """Save optimized solution"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO solutions (history_id, user_id, content) VALUES (?, ?, ?)
            """, (history_id, user_id, content))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving solution: {e}")
        return False


def save_suggestion(history_id: int, user_id: int, content: str) -> bool:
    """Save code improvement suggestion"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO suggestions (history_id, user_id, content) VALUES (?, ?, ?)
            """, (history_id, user_id, content))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving suggestion: {e}")
        return False


def get_history(user_id: int, limit: int = 50) -> List[Tuple]:
    """Get user's conversion history"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM history
                WHERE user_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            """, (user_id, limit))
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving history: {e}")
        return []


def delete_history(history_id: int, user_id: int) -> bool:
    """Delete one history record and any linked items."""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM solutions WHERE history_id = ?", (history_id,))
            cursor.execute("DELETE FROM suggestions WHERE history_id = ?", (history_id,))
            cursor.execute("DELETE FROM history WHERE id = ? AND user_id = ?", (history_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error deleting history: {e}")
        return False


def get_languages() -> List[Tuple]:
    """Get all supported programming languages"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, icon, version FROM languages ORDER BY name")
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving languages: {e}")
        return []


def save_feedback(user_id: Optional[int], name: str, email: str, 
                 rating: int, message: str) -> bool:
    """Save user feedback"""
    if not 1 <= rating <= 5:
        logger.warning(f"Invalid rating: {rating}")
        return False
    
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO feedback (user_id, name, email, rating, message)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, name, email, rating, message))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error saving feedback: {e}")
        return False


def get_all_feedback() -> List[Tuple]:
    """Get all feedback (admin only)"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM feedback
                ORDER BY timestamp DESC
            """)
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving feedback: {e}")
        return []


def is_admin(user_id: int) -> bool:
    """Check if user is admin"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM admins WHERE user_id = ?", (user_id,))
            return cursor.fetchone() is not None
    except sqlite3.Error as e:
        logger.error(f"Error checking admin status: {e}")
        return False


def make_admin(user_id: int) -> bool:
    """Promote user to admin"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR IGNORE INTO admins (user_id, permissions)
                VALUES (?, 'full')
            """, (user_id,))
            conn.commit()
            return True
    except sqlite3.Error as e:
        logger.error(f"Error making admin: {e}")
        return False


def get_users_with_admin_status() -> List[Tuple]:
    """Get all users with their admin status"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.*, CASE WHEN a.id IS NOT NULL THEN 1 ELSE 0 END as is_admin
                FROM users u
                LEFT JOIN admins a ON u.id = a.user_id
                ORDER BY u.created_at DESC
            """)
            return cursor.fetchall()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving users: {e}")
        return []


def get_profile(user_id: int) -> Optional[Tuple]:
    """Get user profile"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM profiles WHERE user_id = ?", (user_id,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving profile: {e}")
        return None


def get_profile_by_username(username: str) -> Optional[Tuple]:
    """Get user and profile by username"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT users.id, users.password, profiles.name, profiles.username, profiles.email
                FROM users
                JOIN profiles ON users.id = profiles.user_id
                WHERE profiles.username = ?
            """, (username,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving profile: {e}")
        return None


def get_profile_by_email(email: str) -> Optional[Tuple]:
    """Get user and profile by email"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT users.id, users.password, profiles.name, profiles.username, profiles.email
                FROM users
                JOIN profiles ON users.id = profiles.user_id
                WHERE profiles.email = ?
            """, (email,))
            return cursor.fetchone()
    except sqlite3.Error as e:
        logger.error(f"Error retrieving profile: {e}")
        return None


def update_profile(user_id: int, name: str, bio: str, phone: str) -> bool:
    """Update user profile"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE profiles 
                SET name = ?, bio = ?, phone = ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ?
            """, (name, bio, phone, user_id))
            conn.commit()
            return cursor.rowcount > 0
    except sqlite3.Error as e:
        logger.error(f"Error updating profile: {e}")
        return False
