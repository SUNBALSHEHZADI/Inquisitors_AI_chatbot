"""
Inquisitors AI Assistant
------------------------

Conversation Memory using SQLite

Purpose:
    Store and retrieve chatbot conversation history
    persistently using SQLite.

Features:
    - SQLite database
    - Multiple chat sessions
    - User messages
    - Assistant messages
    - Retrieve conversation history
    - Clear individual sessions
    - Session creation
    - Automatic timestamps
    - Backward-compatible helper functions

Database:
    data/chat_history.db
"""

from pathlib import Path
import sqlite3
from datetime import datetime, timezone


# ============================================================
# PROJECT PATH
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DATA_DIR = PROJECT_ROOT / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)


DATABASE_PATH = (
    DATA_DIR / "chat_history.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    """
    Create a new SQLite database connection.

    A new connection is created for each operation.
    This is simple and reliable for the current
    single-server chatbot architecture.
    """

    connection = sqlite3.connect(
        str(DATABASE_PATH),
        timeout=10
    )

    connection.row_factory = sqlite3.Row

    return connection


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():
    """
    Create the required SQLite tables if they
    do not already exist.
    """

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # CHAT SESSIONS
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_sessions (

                session_id TEXT PRIMARY KEY,

                created_at TEXT NOT NULL,

                updated_at TEXT NOT NULL

            )
            """
        )

        # ----------------------------------------------------
        # CHAT MESSAGES
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_messages (

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                session_id TEXT NOT NULL,

                role TEXT NOT NULL,

                content TEXT NOT NULL,

                created_at TEXT NOT NULL,

                FOREIGN KEY (
                    session_id
                )
                REFERENCES chat_sessions (
                    session_id
                )
                ON DELETE CASCADE

            )
            """
        )

        # ----------------------------------------------------
        # INDEX
        # ----------------------------------------------------

        cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS
            idx_chat_messages_session
            ON chat_messages(session_id)
            """
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# TIMESTAMP
# ============================================================

def current_timestamp():
    """
    Return a UTC timestamp in ISO format.
    """

    return datetime.now(
        timezone.utc
    ).isoformat()


# ============================================================
# CREATE SESSION
# ============================================================

def create_session(session_id):
    """
    Create a chat session if it does not already exist.

    Returns:
        session_id
    """

    if not session_id:

        raise ValueError(
            "session_id cannot be empty."
        )

    connection = get_connection()

    try:

        timestamp = current_timestamp()

        connection.execute(
            """
            INSERT OR IGNORE INTO chat_sessions
            (
                session_id,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?)
            """,
            (
                session_id,
                timestamp,
                timestamp
            )
        )

        connection.commit()

    finally:

        connection.close()

    return session_id


# ============================================================
# SESSION EXISTS
# ============================================================

def session_exists(session_id):
    """
    Check whether a session exists.
    """

    if not session_id:
        return False

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT 1
            FROM chat_sessions
            WHERE session_id = ?
            LIMIT 1
            """,
            (session_id,)
        )

        return cursor.fetchone() is not None

    finally:

        connection.close()


# ============================================================
# ADD MESSAGE
# ============================================================

def add_message(
    role,
    content,
    session_id="default-session"
):
    """
    Store one conversation message.

    Example:

        add_message(
            "user",
            "What internships are available?",
            "web-123"
        )

    Roles normally include:

        user
        assistant
        system
    """

    if not role:

        raise ValueError(
            "Message role cannot be empty."
        )

    if content is None:

        raise ValueError(
            "Message content cannot be None."
        )

    content = str(content).strip()

    if not content:

        raise ValueError(
            "Message content cannot be empty."
        )

    # Make sure session exists.
    create_session(
        session_id
    )

    connection = get_connection()

    try:

        timestamp = current_timestamp()

        connection.execute(
            """
            INSERT INTO chat_messages
            (
                session_id,
                role,
                content,
                created_at
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                session_id,
                role,
                content,
                timestamp
            )
        )

        connection.execute(
            """
            UPDATE chat_sessions
            SET updated_at = ?
            WHERE session_id = ?
            """,
            (
                timestamp,
                session_id
            )
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# GET HISTORY
# ============================================================

def get_history(
    session_id="default-session",
    limit=20
):
    """
    Retrieve recent conversation history.

    Returns a list compatible with the
    Groq/OpenAI chat message format:

        [
            {
                "role": "user",
                "content": "..."
            },
            {
                "role": "assistant",
                "content": "..."
            }
        ]

    The oldest message is returned first.
    """

    if not session_id:

        return []

    try:

        limit = int(limit)

    except (TypeError, ValueError):

        limit = 20

    limit = max(
        1,
        min(limit, 100)
    )

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT
                role,
                content,
                created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id DESC
            LIMIT ?
            """,
            (
                session_id,
                limit
            )
        )

        rows = cursor.fetchall()

        # Query returns newest first.
        # Reverse so LLM receives chronological order.
        rows = list(reversed(rows))

        return [
            {
                "role": row["role"],
                "content": row["content"]
            }
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# GET FULL HISTORY
# ============================================================

def get_full_history(
    session_id
):
    """
    Retrieve the complete conversation history
    for a session.

    Useful for the frontend history endpoint.
    """

    if not session_id:

        return []

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT
                id,
                role,
                content,
                created_at
            FROM chat_messages
            WHERE session_id = ?
            ORDER BY id ASC
            """,
            (session_id,)
        )

        rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "role": row["role"],
                "content": row["content"],
                "created_at": row["created_at"]
            }
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# MESSAGE COUNT
# ============================================================

def get_message_count(
    session_id
):
    """
    Return number of messages in a session.
    """

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT COUNT(*) AS total
            FROM chat_messages
            WHERE session_id = ?
            """,
            (session_id,)
        )

        row = cursor.fetchone()

        return int(
            row["total"]
        )

    finally:

        connection.close()


# ============================================================
# CLEAR HISTORY
# ============================================================

def clear_history(
    session_id="default-session"
):
    """
    Delete all messages and the session itself.
    """

    if not session_id:

        return

    connection = get_connection()

    try:

        connection.execute(
            """
            DELETE FROM chat_messages
            WHERE session_id = ?
            """,
            (session_id,)
        )

        connection.execute(
            """
            DELETE FROM chat_sessions
            WHERE session_id = ?
            """,
            (session_id,)
        )

        connection.commit()

    finally:

        connection.close()


# ============================================================
# LIST SESSIONS
# ============================================================

def list_sessions(
    limit=50
):
    """
    Return recent chat sessions.

    Useful later if we want a chat-history sidebar
    in the frontend.
    """

    connection = get_connection()

    try:

        cursor = connection.execute(
            """
            SELECT
                session_id,
                created_at,
                updated_at
            FROM chat_sessions
            ORDER BY updated_at DESC
            LIMIT ?
            """,
            (limit,)
        )

        rows = cursor.fetchall()

        return [
            {
                "session_id": row["session_id"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
            for row in rows
        ]

    finally:

        connection.close()


# ============================================================
# DATABASE INITIALIZATION
# ============================================================

initialize_database()


# ============================================================
# MAIN TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("INQUISITORS SQLITE MEMORY TEST")
    print("=" * 60)

    test_session = "memory-test-001"

    # Start clean.
    clear_history(
        test_session
    )

    # Create session.
    create_session(
        test_session
    )

    # Add messages.
    add_message(
        "user",
        "What internship domains are available?",
        test_session
    )

    add_message(
        "assistant",
        "Artificial Intelligence, Machine Learning, Data Science, Research, Web Development, Content Writing, Graphic Design, and Digital Marketing.",
        test_session
    )

    # Read history.
    history = get_history(
        test_session
    )

    print(
        f"\nDatabase:\n{DATABASE_PATH}"
    )

    print(
        f"\nSession:\n{test_session}"
    )

    print(
        f"\nMessages stored:\n{len(history)}"
    )

    print("\nConversation:")

    for message in history:

        print(
            f"{message['role']}: "
            f"{message['content']}"
        )

    print()
    print("=" * 60)
    print("SQLITE MEMORY TEST COMPLETED")
    print("=" * 60)