import sqlite3

from model.chats_models import ChatMessage


# SQLite database setup
def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            name TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id TEXT,
            sender TEXT,
            message TEXT,
            FOREIGN KEY (chat_id) REFERENCES chats (id)
        )
    """)
    print("DB Tables created!")
    conn.commit()
    conn.close()


def save_chat(chat_id, chat_name):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()

    # Save chat metadata
    cursor.execute(
        "INSERT OR IGNORE INTO chats (id, name) VALUES (?, ?)", (chat_id, chat_name)
    )
    conn.commit()
    conn.close()
    print("Saved the chat!")


def save_messages(chat_id, messages: list[ChatMessage]):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    # Save chat messages
    print(f"messages : {messages}")
    for msg in messages:
        print(f"msg : {msg}")
        cursor.execute(
            """
            INSERT INTO messages (chat_id, sender, message)
            VALUES (?, ?, ?)
            """,
            (chat_id, msg.sender, msg.content),
        )
    conn.commit()
    conn.close()
    print("Saved the messages!")


def load_chats():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM chats")
    chats = cursor.fetchall()
    conn.close()
    print(f"Loaded chats : {chats}")
    return chats


# Load chat messages by chat ID
def load_messages(chat_id):
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    cursor.execute("SELECT sender, message FROM messages WHERE chat_id = ?", (chat_id,))
    messages = []
    for row in cursor.fetchall():
        sender, message = row
        messages.append(ChatMessage(sender=sender, content=message))
    conn.close()
    print(f"Loaded messages : {messages}")
    return messages
