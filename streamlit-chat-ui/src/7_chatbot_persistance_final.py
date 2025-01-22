import sqlite3
import uuid

import streamlit as st
from openai import OpenAI

# from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel


# Define the structure of a chat message
class ChatMessage(BaseModel):
    sender: str  # Indicates the sender of the message, either "user" or "bot"
    content: str  # The actual content of the message


# Constants to represent the sender types
USER = "user"  # Represents messages from the user
BOT = "bot"  # Represents messages from the bot

# Set up the header for the Streamlit app
st.header("Chat :blue[Application]")  # Display application title with styling

# Initialize SQLite database
DB_PATH = "chat_history.db"  # Path to the SQLite database file


def init_db():
    """Initialize the SQLite database and create required tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""CREATE TABLE IF NOT EXISTS chats (
                        id TEXT PRIMARY KEY,
                        name TEXT,
                        last_message TEXT
                    )""")  # Create table to store chat metadata
    cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
                        chat_id TEXT,
                        sender TEXT,
                        content TEXT,
                        FOREIGN KEY(chat_id) REFERENCES chats(id)
                    )""")  # Create table to store individual messages
    conn.commit()
    conn.close()


# Initialize the database
init_db()


# Helper functions for database operations
def save_chat_to_db(chat_id, name, last_message):
    """Save or update a chat session in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO chats (id, name, last_message) VALUES (?, ?, ?)",
        (chat_id, name, last_message),
    )
    conn.commit()
    conn.close()


def save_message_to_db(chat_id, sender, content):
    """Save an individual message to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)",
        (chat_id, sender, content),
    )
    conn.commit()
    conn.close()


def load_chat_history():
    """Load all chat sessions and their metadata from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats")
    chats = cursor.fetchall()
    conn.close()
    return [
        {
            "id": chat[0],
            "name": chat[1],
            "last_message": chat[2],
            "messages": load_messages(chat[0]),
        }
        for chat in chats
    ]


def load_messages(chat_id):
    """Load all messages for a specific chat session from the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, content FROM messages WHERE chat_id = ?", (chat_id,))
    messages = cursor.fetchall()
    conn.close()
    return [ChatMessage(sender=msg[0], content=msg[1]) for msg in messages]


# Initialize the session state variables
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []  # Holds messages for the current chat session

if "chat_history" not in st.session_state:
    st.session_state.chat_history = (
        load_chat_history()
    )  # Load chat history from the database

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None  # Track the ID of the active chat session

# OpenAI model identifier
LLM = "gpt-4o"  # Specify the OpenAI model to use
# Initialize the OpenAI client
client = OpenAI()

# Sidebar for chat navigation and controls
with st.sidebar:
    st.title("Chats Conversations")  # Title for the sidebar
    if st.button("New Chat"):
        # Create a new chat session
        st.session_state.active_chat_id = str(uuid.uuid4())  # Generate a unique ID
        st.session_state.current_chat = []  # Clear the current chat session
        new_chat = {
            "id": st.session_state.active_chat_id,
            "name": f"Chat {len(st.session_state.chat_history) + 1}",
            "messages": st.session_state.current_chat,
            "last_message": "",
        }
        st.session_state.chat_history.append(new_chat)
        save_chat_to_db(new_chat["id"], new_chat["name"], new_chat["last_message"])

    for chat in st.session_state.chat_history:
        # Display each chat session with a preview of the last message
        last_message_preview = chat.get("last_message", "No messages yet")[:30] + (
            "..." if len(chat.get("last_message", "")) > 30 else ""
        )
        if st.button(f"{chat['name']} - {last_message_preview}"):
            st.session_state.active_chat_id = chat["id"]
            st.session_state.current_chat = chat["messages"]


# Function to display the messages in the current chat
def display_current_chat():
    """Render all messages in the current chat session."""
    for message in st.session_state.current_chat:
        if message.content:
            if message.sender == BOT:
                st.chat_message("ai").write(message.content)  # Display bot message
            elif message.sender == USER:
                st.chat_message("human").write(message.content)  # Display user message


# Function to send a request to OpenAI and receive a response
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
):
    """Send a user question to OpenAI and get a streamed response."""
    response = client.chat.completions.create(
        model=LLM,
        messages=[{"role": "user", "content": user_question}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stream=True,
    )
    return response


# Function to generate responses incrementally for smoother streaming
def response_generator(user_question):
    """Yield incremental responses from OpenAI for a smoother experience."""
    for chunk in ask_openai(user_question):
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# Main function to run the chat application
def run():
    """Main function to handle user interaction and chat flow."""
    display_current_chat()  # Show the current chat messages
    if st.session_state.active_chat_id:
        prompt = st.chat_input("Add your prompt...")  # Input for user messages
        if prompt:
            st.chat_message("user").write(prompt)  # Display the user input
            output = response_generator(prompt)  # Get the AI response incrementally
            st.session_state.current_chat.append(
                ChatMessage(content=prompt, sender=USER)
            )  # Save user message
            save_message_to_db(
                st.session_state.active_chat_id, USER, prompt
            )  # Persist user message
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)  # Stream and display AI response
            st.session_state.current_chat.append(
                ChatMessage(content=ai_message, sender=BOT)
            )  # Save AI response
            save_message_to_db(
                st.session_state.active_chat_id, BOT, ai_message
            )  # Persist AI response
            for chat in st.session_state.chat_history:
                if chat["id"] == st.session_state.active_chat_id:
                    chat["last_message"] = prompt  # Update last message for the chat
                    save_chat_to_db(
                        chat["id"], chat["name"], prompt
                    )  # Persist updated chat metadata


# Entry point for the application
if __name__ == "__main__":
    run()  # Start the application
