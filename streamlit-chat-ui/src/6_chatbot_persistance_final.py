import sqlite3
import uuid

import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class ChatMessage(BaseModel):
    sender: str  # BOT, USER
    content: str


USER = "user"
BOT = "bot"

LLM = "gpt-4o"
client = OpenAI()

# -------------------------------------------------
# Database Persistence Layer
# -------------------------------------------------


def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                name TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                chat_id TEXT,
                sender TEXT,
                content TEXT
            )
        """)
        conn.commit()


def load_chats_from_db():
    """Load all chats and their messages from the DB into a dictionary."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("SELECT chat_id, name FROM chats")
        rows = c.fetchall()
        all_chats = {}
        for chat_id, name in rows:
            c.execute(
                "SELECT sender, content FROM messages WHERE chat_id=?", (chat_id,)
            )
            message_rows = c.fetchall()
            messages = [
                ChatMessage(sender=sender, content=content)
                for sender, content in message_rows
            ]
            all_chats[chat_id] = {"name": name, "messages": messages}
        return all_chats


def create_new_chat_in_db(chat_id: str, name: str, first_message: ChatMessage):
    """Create a new chat row in the DB and insert the first message."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO chats (chat_id, name) VALUES (?,?)", (chat_id, name))
        c.execute(
            "INSERT INTO messages (message_id, chat_id, sender, content) VALUES (?,?,?,?)",
            (str(uuid.uuid4()), chat_id, first_message.sender, first_message.content),
        )
        conn.commit()


def add_message_to_db(chat_id: str, message: ChatMessage):
    """Add a new message to the messages table for the given chat."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute(
            "INSERT INTO messages (message_id, chat_id, sender, content) VALUES (?,?,?,?)",
            (str(uuid.uuid4()), chat_id, message.sender, message.content),
        )
        conn.commit()


def update_chat_name_in_db(chat_id: str, new_name: str):
    """Update an existing chat's name."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("UPDATE chats SET name=? WHERE chat_id=?", (new_name, chat_id))
        conn.commit()


def get_all_messages():
    """Retrieve all messages from the DB (for demonstration purposes)."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("SELECT chat_id, sender, content FROM messages")
        return c.fetchall()


# -------------------------------------------------
# Streamlit Chat App
# -------------------------------------------------

st.header("Chat :blue[Application]")

# Initialize the DB
init_db()

# Load existing chats from the database
if "all_chats" not in st.session_state:
    st.session_state["all_chats"] = load_chats_from_db()

# Track which chat (by UUID) is currently selected
if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = None

# Sidebar: Display existing chats and a new chat button
with st.sidebar:
    st.subheader("Conversations")

    # Place 'New Chat' button at the top
    if st.button("New Chat", key="new_chat_button"):
        new_chat_uuid = str(uuid.uuid4())
        first_msg = ChatMessage(sender=BOT, content="Hello, how can I help you?")
        create_new_chat_in_db(new_chat_uuid, "New Chat", first_msg)

        st.session_state["all_chats"][new_chat_uuid] = {
            "name": "New Chat",
            "messages": [first_msg],
        }
        st.session_state["selected_chat"] = new_chat_uuid

    # Display existing chat sessions in reverse order so new ones appear at the top.
    # Add a unique key parameter to each button to avoid duplicate IDs.
    for chat_id in reversed(list(st.session_state["all_chats"].keys())):
        chat_data = st.session_state["all_chats"][chat_id]
        button_label = chat_data["name"]
        if st.button(button_label, key=f"chat_button_{chat_id}"):
            st.session_state["selected_chat"] = chat_id

print(f"conversations : {st.session_state['all_chats']}")

# If a chat is selected, display its conversation and the chat input
if st.session_state["selected_chat"]:
    chat_id = st.session_state["selected_chat"]
    chat_data = st.session_state["all_chats"][chat_id]
    chat_history = chat_data["messages"]

    # Display chat history
    for msg in chat_history:
        if msg.sender == BOT:
            st.chat_message("ai").write(msg.content)
        else:
            st.chat_message("human").write(msg.content)

    # Functions for the chatbot
    def ask_openai(
        user_question: str,
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: int = 256,
    ):
        response = client.chat.completions.create(
            model=LLM,
            messages=[
                {"role": "user", "content": user_question},
            ],
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=top_p,
            stream=True,
        )
        return response

    def response_generator(user_question):
        for chunk in ask_openai(user_question):
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content  # Stream response incrementally

    # Main app logic to handle user input
    def run():
        prompt = st.chat_input("Add your prompt...")
        if prompt:
            # Optionally, rename the conversation using the last user prompt
            st.session_state["all_chats"][chat_id]["name"] = prompt
            update_chat_name_in_db(chat_id, prompt)

            # Display user message
            st.chat_message("human").write(prompt)

            # Save user message
            user_msg = ChatMessage(content=prompt, sender=USER)
            chat_history.append(user_msg)
            add_message_to_db(chat_id, user_msg)

            # Generate response
            output = response_generator(prompt)
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)

            bot_msg = ChatMessage(content=ai_message, sender=BOT)
            chat_history.append(bot_msg)
            add_message_to_db(chat_id, bot_msg)

    if __name__ == "__main__":
        run()
else:
    st.write("Select or create a new chat from the sidebar to begin.")
