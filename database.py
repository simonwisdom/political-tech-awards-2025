import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import threading
from config import DB_PATH, DB_TIMEOUT

# Thread-local storage for database connections
_local = threading.local()

def _create_connection() -> sqlite3.Connection:
    """Create a new database connection with proper settings."""
    conn = sqlite3.connect(DB_PATH, timeout=DB_TIMEOUT)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def _get_thread_connection() -> sqlite3.Connection:
    """Get or create a thread-local database connection."""
    if not hasattr(_local, 'connection'):
        _local.connection = _create_connection()
    return _local.connection

@contextmanager
def get_connection():
    """Get a database connection for the current thread."""
    conn = _get_thread_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise

def initialize_db():
    """Initialize the database with required tables."""
    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                email TEXT PRIMARY KEY,
                verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS verification_tokens (
                email TEXT,
                token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                PRIMARY KEY (email, token)
            );

            CREATE TABLE IF NOT EXISTS allocations (
                email TEXT,
                project_id TEXT,
                amount INTEGER,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (email, project_id),
                FOREIGN KEY (email) REFERENCES users(email),
                CHECK (amount >= 0)
            );

            CREATE INDEX IF NOT EXISTS idx_allocations_email 
            ON allocations(email);
            
            CREATE INDEX IF NOT EXISTS idx_tokens_email_token 
            ON verification_tokens(email, token);
        """)

# User operations
def create_user(email: str) -> bool:
    """Create a new user."""
    with get_connection() as conn:
        try:
            conn.execute(
                "INSERT INTO users (email) VALUES (?)",
                (email,)
            )
            return True
        except sqlite3.IntegrityError:
            return False

def verify_user(email: str) -> bool:
    """Mark a user as verified."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE users SET verified = TRUE WHERE email = ?",
            (email,)
        )
        return cursor.rowcount > 0

def is_user_verified(email: str) -> bool:
    """Check if a user is verified."""
    with get_connection() as conn:
        result = conn.execute(
            "SELECT verified FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        return bool(result and result[0])

# Token operations
def store_verification_token(email: str, token: str, expires_in_hours: int):
    """Store a verification token."""
    expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO verification_tokens (email, token, expires_at)
               VALUES (?, ?, ?)""",
            (email, token, expires_at)
        )

def verify_token(email: str, token: str) -> bool:
    """Verify a token and return whether it's valid."""
    with get_connection() as conn:
        result = conn.execute(
            """SELECT expires_at FROM verification_tokens 
               WHERE email = ? AND token = ?""",
            (email, token)
        ).fetchone()
        
        if not result:
            return False
            
        expires_at = datetime.fromisoformat(result[0])
        return datetime.utcnow() <= expires_at

# Allocation operations
def save_allocation(email: str, project_id: str, amount: int):
    """Save or update a project allocation."""
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO allocations (email, project_id, amount, updated_at)
               VALUES (?, ?, ?, CURRENT_TIMESTAMP)
               ON CONFLICT(email, project_id) 
               DO UPDATE SET amount = ?, updated_at = CURRENT_TIMESTAMP""",
            (email, project_id, amount, amount)
        )

def get_user_allocations(email: str) -> Dict[str, int]:
    """Get all allocations for a user."""
    with get_connection() as conn:
        results = conn.execute(
            "SELECT project_id, amount FROM allocations WHERE email = ?",
            (email,)
        ).fetchall()
        return {row[0]: row[1] for row in results}

def get_total_allocated(email: str) -> int:
    """Get total amount allocated by a user."""
    with get_connection() as conn:
        result = conn.execute(
            "SELECT SUM(amount) FROM allocations WHERE email = ?",
            (email,)
        ).fetchone()
        return result[0] or 0

# Initialize the database
initialize_db() 