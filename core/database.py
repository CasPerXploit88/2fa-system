import sqlite3
import os
from config import Config


def get_connection():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    os.makedirs(os.path.dirname(Config.DATABASE_PATH), exist_ok=True)
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                username        TEXT    NOT NULL UNIQUE,
                email           TEXT    NOT NULL UNIQUE,
                password_hash   TEXT    NOT NULL,
                otp_secret      TEXT    NOT NULL,
                login_attempts  INTEGER NOT NULL DEFAULT 0,
                locked_until    TEXT,
                created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS otp_sessions (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                token           TEXT    NOT NULL UNIQUE,
                attempts        INTEGER NOT NULL DEFAULT 0,
                created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                used            INTEGER NOT NULL DEFAULT 0
            );
        """)


def fetch_user_by_username(username: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def fetch_user_by_id(user_id: int):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE id = ?", (user_id,)
        ).fetchone()


def insert_user(username: str, email: str, password_hash: str, otp_secret: str):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, email, password_hash, otp_secret) VALUES (?, ?, ?, ?)",
            (username, email, password_hash, otp_secret),
        )


def increment_login_attempts(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET login_attempts = login_attempts + 1 WHERE id = ?",
            (user_id,),
        )


def lock_user(user_id: int, until: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET locked_until = ? WHERE id = ?",
            (until, user_id),
        )


def reset_login_attempts(user_id: int):
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET login_attempts = 0, locked_until = NULL WHERE id = ?",
            (user_id,),
        )


def create_otp_session(user_id: int, token: str):
    with get_connection() as conn:
        conn.execute("DELETE FROM otp_sessions WHERE user_id = ?", (user_id,))
        conn.execute(
            "INSERT INTO otp_sessions (user_id, token) VALUES (?, ?)",
            (user_id, token),
        )


def fetch_otp_session(token: str):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM otp_sessions WHERE token = ? AND used = 0",
            (token,),
        ).fetchone()


def increment_otp_attempts(token: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE otp_sessions SET attempts = attempts + 1 WHERE token = ?",
            (token,),
        )


def invalidate_otp_session(token: str):
    with get_connection() as conn:
        conn.execute(
            "UPDATE otp_sessions SET used = 1 WHERE token = ?",
            (token,),
        )
