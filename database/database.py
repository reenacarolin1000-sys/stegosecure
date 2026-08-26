import sqlite3
from pathlib import Path
from datetime import datetime


# Get the main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Database file
DB_PATH = BASE_DIR / "stegosecure.db"


def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_PATH)


def initialize_database():
    """Create the required database tables."""

    connection = get_connection()
    cursor = connection.cursor()

    # -------------------------------
    # USERS TABLE
    # -------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # -------------------------------
    # STEGO HISTORY TABLE
    # -------------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stego_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            original_filename TEXT NOT NULL,
            stego_filename TEXT,
            message_length INTEGER,
            psnr REAL,
            ssim REAL,
            mse REAL,
            created_at TEXT NOT NULL,

            FOREIGN KEY (user_id)
            REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def create_user(username, email, password_hash):
    """Create a new user."""

    connection = get_connection()
    cursor = connection.cursor()

    try:

        cursor.execute("""
            INSERT INTO users
            (username, email, password_hash, created_at)
            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            datetime.now().isoformat()
        ))

        connection.commit()

        return True

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def get_user(username):
    """Retrieve a user using their username."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            username,
            email,
            password_hash
        FROM users
        WHERE username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    return user


def add_stego_history(
    user_id,
    original_filename,
    stego_filename,
    message_length,
    psnr=None,
    ssim=None,
    mse=None
):
    """Store information about a generated stego image."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO stego_history
        (
            user_id,
            original_filename,
            stego_filename,
            message_length,
            psnr,
            ssim,
            mse,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id,
        original_filename,
        stego_filename,
        message_length,
        psnr,
        ssim,
        mse,
        datetime.now().isoformat()
    ))

    connection.commit()
    connection.close()


def get_user_history(user_id):
    """Retrieve stego images created by a particular user."""

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            original_filename,
            stego_filename,
            message_length,
            psnr,
            ssim,
            mse,
            created_at
        FROM stego_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    history = cursor.fetchall()

    connection.close()

    return history
if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")