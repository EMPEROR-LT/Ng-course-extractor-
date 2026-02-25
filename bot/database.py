"""
Database module for storing user data, search history, and favorites
Uses SQLite for simplicity and portability
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    """Database handler for bot data"""

    def __init__(self, db_file: str = "course_bot.db"):
        self.db_file = db_file
        self.init_database()

    def init_database(self):
        """Initialize database tables"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        settings TEXT DEFAULT '{}'
                    )
                ''')

                # Search history table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS search_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        query TEXT NOT NULL,
                        results_count INTEGER DEFAULT 0,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                # Favorites table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS favorites (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        title TEXT NOT NULL,
                        url TEXT NOT NULL,
                        platform TEXT,
                        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                # Rate limiting table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS rate_limits (
                        user_id INTEGER PRIMARY KEY,
                        search_count INTEGER DEFAULT 0,
                        window_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                conn.commit()
                logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Database initialization failed: {e}")

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_user_info(self, user_id: int) -> Dict:
        """Get user information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT * FROM users WHERE user_id = ?
                ''', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else {}
        except Exception as e:
            logger.error(f"Failed to get user info for {user_id}: {e}")
            return {}

    def add_or_update_user(self, user_id: int, username: str = None,
                          first_name: str = None, last_name: str = None):
        """Add or update user information"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users
                    (user_id, username, first_name, last_name, last_active)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add/update user {user_id}: {e}")

    def add_search_history(self, user_id: int, query: str, results_count: int = 0):
        """Add search to history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO search_history (user_id, query, results_count)
                    VALUES (?, ?, ?)
                ''', (user_id, query, results_count))

                # Keep only last 20 searches per user
                cursor.execute('''
                    DELETE FROM search_history
                    WHERE user_id = ? AND id NOT IN (
                        SELECT id FROM search_history
                        WHERE user_id = ?
                        ORDER BY timestamp DESC
                        LIMIT 20
                    )
                ''', (user_id, user_id))

                conn.commit()
        except Exception as e:
            logger.error(f"Failed to add search history for user {user_id}: {e}")

    def get_search_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """Get user's search history"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT query, results_count, timestamp
                    FROM search_history
                    WHERE user_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (user_id, limit))

                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get search history for user {user_id}: {e}")
            return []

    def add_favorite(self, user_id: int, title: str, url: str, platform: str = None):
        """Add link to favorites"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Check if already exists
                cursor.execute('''
                    SELECT id FROM favorites
                    WHERE user_id = ? AND url = ?
                ''', (user_id, url))

                if cursor.fetchone():
                    return False  # Already in favorites

                cursor.execute('''
                    INSERT INTO favorites (user_id, title, url, platform)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, title, url, platform))

                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to add favorite for user {user_id}: {e}")
            return False

    def get_favorites(self, user_id: int) -> List[Dict]:
        """Get user's favorites"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, title, url, platform, added_at
                    FROM favorites
                    WHERE user_id = ?
                    ORDER BY added_at DESC
                ''', (user_id,))

                return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get favorites for user {user_id}: {e}")
            return []

    def remove_favorite(self, favorite_id: int) -> bool:
        """Remove link from favorites by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM favorites
                    WHERE id = ?
                ''', (favorite_id,))

                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Failed to remove favorite ID {favorite_id}: {e}")
            return False

    def check_rate_limit(self, user_id: int, limit: int = 10, window: int = 60) -> bool:
        """Check if user has exceeded rate limit"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Clean old entries
                cursor.execute('''
                    DELETE FROM rate_limits
                    WHERE window_start < datetime('now', '-' || ? || ' seconds')
                ''', (window,))

                # Get current count
                cursor.execute('''
                    SELECT search_count FROM rate_limits
                    WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if not row:
                    # First search in window
                    cursor.execute('''
                        INSERT INTO rate_limits (user_id, search_count)
                        VALUES (?, 1)
                    ''', (user_id,))
                    conn.commit()
                    return True

                if row[0] >= limit:
                    return False  # Rate limit exceeded

                # Increment count
                cursor.execute('''
                    UPDATE rate_limits
                    SET search_count = search_count + 1
                    WHERE user_id = ?
                ''', (user_id,))

                conn.commit()
                return True

        except Exception as e:
            logger.error(f"Rate limit check failed for user {user_id}: {e}")
            return True  # Allow on error

    def get_user_settings(self, user_id: int) -> Dict:
        """Get user settings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT settings FROM users WHERE user_id = ?
                ''', (user_id,))

                row = cursor.fetchone()
                if row and row[0]:
                    return json.loads(row[0])
                return {}
        except Exception as e:
            logger.error(f"Failed to get settings for user {user_id}: {e}")
            return {}

    def update_user_settings(self, user_id: int, settings: Dict):
        """Update user settings"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET settings = ? WHERE user_id = ?
                ''', (json.dumps(settings), user_id))
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to update settings for user {user_id}: {e}")
