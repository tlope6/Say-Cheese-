"""
SQLite event logger for tracking all interactions.
"""

import sqlite3
import os
import time
from datetime import datetime


class EventLogger:
    def __init__(self, db_path="data/events.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                detail TEXT,
                created_at REAL
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS captures (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                filepath TEXT NOT NULL,
                effect TEXT,
                trigger_type TEXT
            )
        """)
        self.conn.commit()

    def log(self, event_type, detail=None):
        """Log a general event."""
        now = datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO events (timestamp, event_type, detail, created_at) VALUES (?, ?, ?, ?)",
            (now, event_type, detail, time.time())
        )
        self.conn.commit()

    def log_capture(self, filepath, effect="none", trigger_type="manual"):
        """Log a photo capture."""
        now = datetime.now().isoformat()
        self.conn.execute(
            "INSERT INTO captures (timestamp, filepath, effect, trigger_type) VALUES (?, ?, ?, ?)",
            (now, filepath, effect, trigger_type)
        )
        self.conn.commit()

    def get_recent_events(self, limit=20):
        """Get recent events for display."""
        cursor = self.conn.execute(
            "SELECT timestamp, event_type, detail FROM events ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()

    def get_captures(self, limit=50):
        """Get recent captures."""
        cursor = self.conn.execute(
            "SELECT timestamp, filepath, effect FROM captures ORDER BY id DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()

    def get_stats(self):
        """Get summary statistics."""
        events_count = self.conn.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        captures_count = self.conn.execute("SELECT COUNT(*) FROM captures").fetchone()[0]
        return {"total_events": events_count, "total_captures": captures_count}

    def close(self):
        self.conn.close()