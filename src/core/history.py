"""
SQLite-backed Download History Manager.
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from ..config import HISTORY_DB_FILE


class HistoryManager:
    """Manages persistent record keeping of downloaded files."""

    def __init__(self, db_path=HISTORY_DB_FILE):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Creates the history table if it doesn't already exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS download_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    type TEXT NOT NULL,
                    quality TEXT,
                    format TEXT,
                    file_size INTEGER DEFAULT 0,
                    file_path TEXT,
                    status TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_record(
        self,
        title: str,
        url: str,
        download_type: str,
        quality: str,
        output_format: str,
        file_size: int = 0,
        file_path: str = "",
        status: str = "Completed"
    ) -> int:
        """Inserts a new record into download history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO download_history
                (title, url, type, quality, format, file_size, file_path, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                title or "Untitled",
                url,
                download_type,
                quality,
                output_format,
                file_size,
                file_path,
                status,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            return cursor.lastrowid

    def update_status(
        self,
        record_id: int,
        status: str,
        file_path: Optional[str] = None,
        file_size: Optional[int] = None
    ):
        """Updates status, path, and size for an existing record."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            query = "UPDATE download_history SET status = ?"
            params: List[Any] = [status]

            if file_path is not None:
                query += ", file_path = ?"
                params.append(file_path)
            if file_size is not None:
                query += ", file_size = ?"
                params.append(file_size)

            query += " WHERE id = ?"
            params.append(record_id)

            cursor.execute(query, params)
            conn.commit()

    def get_history(self, search_query: Optional[str] = None, limit: int = 300) -> List[Dict[str, Any]]:
        """Retrieves history records, optionally filtered by title or URL."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if search_query and search_query.strip():
                pattern = f"%{search_query.strip()}%"
                cursor.execute("""
                    SELECT * FROM download_history
                    WHERE title LIKE ? OR url LIKE ?
                    ORDER BY id DESC LIMIT ?
                """, (pattern, pattern, limit))
            else:
                cursor.execute("""
                    SELECT * FROM download_history
                    ORDER BY id DESC LIMIT ?
                """, (limit,))

            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_record(self, record_id: int):
        """Deletes a single record by ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM download_history WHERE id = ?", (record_id,))
            conn.commit()

    def clear_all(self):
        """Clears all records from download history."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM download_history")
            conn.commit()


# Singleton instance
history_manager = HistoryManager()
