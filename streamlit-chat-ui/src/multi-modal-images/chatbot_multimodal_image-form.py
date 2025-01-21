import os
import sqlite3
import uuid
from typing import Optional

import streamlit as st
from openai import OpenAI
from pydantic import BaseModel


# Function to initialize the database schema
def init_db():
    conn = sqlite3.connect("chat_history.db")
    cursor = conn.cursor()
    # Create main chat history table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id TEXT PRIMARY KEY,  -- Unique ID for each chat
            name TEXT  -- Name of the chat
        )
    """)
    # Create messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,  -- Auto-increment ID for messages
            chat_id TEXT,  -- ID of the chat this message belongs to
            sender TEXT,  -- Sender of the message (user or bot)
            content TEXT,  -- Text content of the message
            image_path TEXT,  -- Path to the image file if present
            FOREIGN KEY(chat_id) REFERENCES chat_history(id)  -- Reference to chat_history table
        )
    """)
    conn.commit()
    conn.close()


# Function to save a chat and its messages to the database
def save_chat_to_db(chat_id, chat_name, messages):
    if not messages:  # Skip if there are no messages to save
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
                INSERT INTO messages (chat_id, sender, content, image_path)
                VALUES (?, ?, ?, ?)
                """,
                (chat_id, message.sender, message.content, message.image_path),
            )
    except Exception as e:
        print(f"Error saving chat to DB: {e}")
    finally:
        conn.commit()
        conn.close()


# Function to load all chats and their messages from the database
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
            "SELECT sender, content, image_path FROM messages WHERE chat_id = ?",
            (chat_id,),
        )
        messages = [
            ChatMessage(sender=row[0], content=row[1], image_path=row[2])
            for row in cursor.fetchall()
        ]
        result.append({"id": chat_id, "name": chat_name, "messages": messages})
    conn.close()
    return result


# Ensure the directory for uploaded images exists
os.makedirs("uploaded_images", exist_ok=True)

# Initialize the database at the start of the application
init_db()


# Define a data model for chat messages
class ChatMessage(BaseModel):
    sender: str  # Sender of the message (user or bot)
    content: Optional[str] = None  # Text content of the message, can be None
    image_path: Optional[str] = None  # Path to the image file if an image is uploaded


# Constants for identifying the sender
USER = "user"
BOT = "bot"

# Set up the main header of the Streamlit app
st.header("Chat :blue[Application]")

# Initialize session state variables to store chat history and active chat details
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []  # List to hold the current chat messages

if "chat_history" not in st.session_state:
    st.session_state.chat_history = (
        load_chats_from_db()
    )  # Load chat history from the database

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None  # ID of the currently active chat

# Set up the OpenAI client and model to be used
LLM = "gpt-4o"
client = OpenAI()

# Sidebar configuration for managing chats
with st.sidebar:
    st.title("Chats Conversations")
    if st.button("New Chat"):
        # Start a new chat
        st.session_state.active_chat_id = str(
            uuid.uuid4()
        )  # Generate a unique ID for the new chat
        st.session_state.current_chat = []  # Clear current chat history
        new_chat = {
            "id": st.session_state.active_chat_id,  # Save the unique ID
            "name": f"Chat {len(st.session_state.chat_history) + 1}",  # Assign a name to the chat
            "messages": st.session_state.current_chat,  # Initialize with an empty message list
        }
        st.session_state.chat_history.append(new_chat)  # Add to the chat history
        save_chat_to_db(new_chat["id"], new_chat["name"], new_chat["messages"])

    # Display existing chats in the sidebar for quick access
    for chat in st.session_state.chat_history:
        if chat["name"]:
            if st.button(chat["name"]):
                # Load the selected chat
                st.session_state.active_chat_id = chat["id"]
                st.session_state.current_chat = chat["messages"]


# Function to display the current chat messages on the screen
def display_current_chat():
    """Display all chat messages in the current chat."""
    for message in st.session_state.current_chat:
        if message.content:
            if message.sender == BOT:
                st.chat_message("ai").write(message.content)  # Display bot messages

            if message.sender == USER:
                st.chat_message("human").write(message.content)  # Display user messages

        if message.image_path:  # Check if an image is part of the message
            st.image(
                message.image_path, caption=f"Image from {message.sender}"
            )  # Display the image


# Function to interact with OpenAI's API
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
):
    """Send a question to OpenAI and receive a response."""
    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "user", "content": user_question},  # User input
        ],
        temperature=temperature,  # Control randomness of the output
        max_tokens=max_tokens,  # Limit the length of the response
        top_p=top_p,  # Limit response diversity
        stream=True,  # Enable streaming for incremental responses
    )
    return response


# Generator to stream responses incrementally
def response_generator(user_question):
    """Generate responses incrementally from OpenAI."""
    for chunk in ask_openai(user_question):
        if (
            chunk.choices and chunk.choices[0].delta.content
        ):  # Check for valid response chunks
            yield chunk.choices[0].delta.content  # Yield each chunk of content


# Main function to run the chat application
def run():
    if st.session_state.chat_history and st.session_state.active_chat_id:
        # Container for chat messages
        chat_container = st.container()
        # with chat_container:
        #     display_current_chat()

        # Input fields for user prompt and image upload at the bottom
        with st.form(key="user_input_form", clear_on_submit=True):
            prompt = st.text_input("Add your prompt...")
            uploaded_file = st.file_uploader(
                "Upload an image",
                type=["jpg", "jpeg", "png"],
                label_visibility="collapsed",
            )
            submit_button = st.form_submit_button(label="Send")

        if submit_button and (prompt or uploaded_file):
            if prompt:
                st.session_state.current_chat.append(
                    ChatMessage(
                        content=prompt, sender=USER
                    )  # Save the user's text message
                )

            if uploaded_file:
                # Save the uploaded image locally
                file_path = f"uploaded_images/{uuid.uuid4()}_{uploaded_file.name}"
                with open(file_path, "wb") as f:
                    f.write(uploaded_file.read())
                st.session_state.current_chat.append(
                    ChatMessage(
                        image_path=file_path, sender=USER
                    )  # Save the image message
                )

            if prompt:
                output = response_generator(prompt)  # Generate a response from OpenAI
                ai_message = "".join(output)  # Combine response chunks
                st.write(ai_message)

            st.session_state.current_chat.append(
                ChatMessage(content=ai_message, sender=BOT)  # Save the AI's response
            )

            # Update the database with the latest chat messages
            for chat in st.session_state.chat_history:
                if chat["id"] == st.session_state.active_chat_id:
                    chat["messages"] = st.session_state.current_chat
                    save_chat_to_db(chat["id"], chat["name"], chat["messages"])

            # Force chat container to refresh
            chat_container.empty()
            with chat_container:
                display_current_chat()
        else:
            with chat_container:
                display_current_chat()


if __name__ == "__main__":
    run()
