import sqlite3
from typing import List

from src.model.chats_models import ChatMessage


def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    # Create main chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            sender TEXT,
            content TEXT,
            FOREIGN KEY(chat_id) REFERENCES chat_history(id)
        )
    """)
    conn.commit()
    conn.close()


def save_chat_to_db(chat_id, chat_name, messages: List[ChatMessage]):
    if not messages:  # Check if messages are empty or None
        print("No messages to save. Skipping database save operation.")
        return

    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    try:
        # Save or update the chat record
        cursor.execute(
            """
            INSERT OR REPLACE INTO chat_history (id, name)
            VALUES (?, ?)
            """,
            (chat_id, chat_name),
        )
        # Save individual messages
        for message in messages:
            cursor.execute(
                """
                INSERT INTO messages (chat_id, sender, content)
                VALUES (?, ?, ?)
                """,
                (chat_id, message.sender, message.content),
            )
    except Exception as e:
        print(f"Error saving chat to DB: {e}")
    finally:
        conn.commit()
        conn.close()


def load_chats_from_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    # Load chat history
    cursor.execute("SELECT id, name FROM chat_history")
    chats = cursor.fetchall()
    result = []
    for chat in chats:
        chat_id, chat_name = chat
        # Load messages for the chat
        cursor.execute(
            "SELECT sender, content FROM messages WHERE chat_id = ?", (chat_id,)
        )
        messages = [
            ChatMessage(sender=row[0], content=row[1]) for row in cursor.fetchall()
        ]
        result.append({"id": chat_id, "name": chat_name, "messages": messages})
    conn.close()
    return result
