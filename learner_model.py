import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("studymate.db")


def _connect():
    return sqlite3.connect(DB_PATH)


def _norm(topic):
    return (topic or "").strip().lower()


def init_db():
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question_id TEXT NOT NULL,
                is_correct INTEGER NOT NULL,
                difficulty TEXT,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS mastery (
                topic TEXT PRIMARY KEY,
                mastery REAL NOT NULL DEFAULT 0.5,
                attempts INTEGER NOT NULL DEFAULT 0
            )
        """)


def save_attempt(topic, question_id, is_correct, difficulty="", source=""):
    with _connect() as conn:
        conn.execute(
            """INSERT INTO attempts
            (topic, question_id, is_correct, difficulty, source)
            VALUES (?, ?, ?, ?, ?)""",
            (_norm(topic), question_id, int(is_correct), difficulty, source),
        )


def update_mastery(topic, quiz_score):
    topic = _norm(topic)
    if not topic:
        return
    with _connect() as conn:
        row = conn.execute(
            "SELECT mastery, attempts FROM mastery WHERE topic = ?", (topic,)
        ).fetchone()
        old_mastery, attempts = row if row else (0.5, 0)
        new_mastery = 0.7 * old_mastery + 0.3 * float(quiz_score)
        conn.execute(
            """INSERT INTO mastery(topic, mastery, attempts) VALUES (?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET mastery=excluded.mastery, attempts=excluded.attempts""",
            (topic, max(0.0, min(1.0, new_mastery)), attempts + 1),
        )


def get_mastery():
    with _connect() as conn:
        rows = conn.execute(
            "SELECT topic, mastery, attempts FROM mastery ORDER BY mastery ASC"
        ).fetchall()
    return [
        {"topic": topic, "mastery": mastery, "attempts": attempts}
        for topic, mastery, attempts in rows
    ]
