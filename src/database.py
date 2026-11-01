import sqlite3
from pathlib import Path
from contextlib import contextmanager

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DB_PATH = DATA_DIR / "internship_tracker.db"


@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")

    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_connection() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS users(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin','intern')),
            skills TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            active INTEGER DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            assignee_id INTEGER NOT NULL,
            priority TEXT NOT NULL
                CHECK(priority IN ('Low','Medium','High','Critical')),
            status TEXT NOT NULL DEFAULT 'To Do'
                CHECK(status IN ('To Do','In Progress','Testing','Completed')),
            due_date TEXT NOT NULL,
            required_skills TEXT DEFAULT '',
            created_by INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(assignee_id) REFERENCES users(id),
            FOREIGN KEY(created_by) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS submissions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            intern_id INTEGER NOT NULL,
            work_details TEXT NOT NULL,
            submitted_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(task_id) REFERENCES tasks(id),
            FOREIGN KEY(intern_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS activity_logs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            details TEXT DEFAULT '',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS gmail_imports(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id TEXT NOT NULL UNIQUE,
            subject TEXT DEFAULT '',
            sender TEXT DEFAULT '',
            email_date TEXT DEFAULT '',
            task_id INTEGER,
            imported_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(task_id) REFERENCES tasks(id)
        );
        """)


def log_activity(user_id, action, details=""):
    with get_connection() as con:
        con.execute(
            """
            INSERT INTO activity_logs(user_id, action, details)
            VALUES (?, ?, ?)
            """,
            (user_id, action, details)
        )


def seed_admin():
    import hashlib
    import os

    with get_connection() as con:
        exists = con.execute(
            "SELECT id FROM users WHERE username='admin'"
        ).fetchone()

        if exists is None:
            salt = os.urandom(16).hex()

            digest = hashlib.pbkdf2_hmac(
                'sha256',
                b'Admin@12345',
                bytes.fromhex(salt),
                200_000
            ).hex()

            con.execute(
                """
                INSERT INTO users
                (name, username, password_hash, salt, role, skills)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    'Demo Administrator',
                    'admin',
                    digest,
                    salt,
                    'admin',
                    ''
                )
            )