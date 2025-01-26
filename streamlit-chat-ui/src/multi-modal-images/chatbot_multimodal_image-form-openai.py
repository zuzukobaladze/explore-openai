import base64
import os
import sqlite3
import uuid
from typing import Optional

import requests
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
    print("Database initialized successfully.")


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
        print(f"Chat {chat_name} with ID {chat_id} saved to database.")
        # Save individual messages
        for message in messages:
            cursor.execute(
                """
                INSERT INTO messages (chat_id, sender, content, image_path)
                VALUES (?, ?, ?, ?)
                """,
                (chat_id, message.sender, message.content, message.image_path),
            )
            print(
                f"Message from {message.sender} saved: {message.content or 'Image message'}"
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
        print(f"Loaded chat {chat_name} with {len(messages)} messages.")
    conn.close()
    return result


# Ensure the directory for uploaded images exists
os.makedirs("uploaded_images", exist_ok=True)
print("Directory for uploaded images ensured.")

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

# Set up the OpenAI client and model to be used
LLM = "gpt-4o"
client = OpenAI()

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


# Function to encode an image as base64
def encode_image(image_path):
    print(f"Encoding image: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


# Function to interact with OpenAI's API for text and image input
def ask_openai_image(
    user_question: str,
    image_path: Optional[str] = None,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
):
    """Send a question and optional image to OpenAI and receive a response."""
    try:
        print(f"Sending question to OpenAI with image: {image_path}")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {os.getenv('OPENAI_API_KEY')}",
        }

        payload = {
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{encode_image(image_path)}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        response = requests.post(
            "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
        )

        print(f"Response type: {type(response)}")
        return response
    except Exception as e:
        print(f"Error during OpenAI API call with image: {e}")
        return {"error": str(e)}


# Function to interact with OpenAI's API for text input only
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
):
    """Send a question to OpenAI and receive a response."""
    try:
        print(f"Sending question to OpenAI: {user_question}")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": user_question},  # User input
            ],
            temperature=temperature,  # Control randomness of the output
            max_tokens=max_tokens,  # Limit the length of the response
            top_p=top_p,  # Limit response diversity
            stream=True,  # Enable streaming for incremental responses
        )
        print("Response streaming initialized.")
        return response
    except Exception as e:
        print(f"Error during OpenAI API call: {e}")
        return {"error": str(e)}


# Function to display the current chat messages on the screen
def display_current_chat():
    """Display all chat messages in the current chat."""
    print("Displaying current chat messages.")
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


# Generator to stream responses incrementally
def response_generator(user_question, image_path=None):
    """Generate responses incrementally from OpenAI with optional image input."""
    try:
        print(
            f"Generating response for question: {user_question} with image: {image_path}"
        )
        if image_path:
            response = ask_openai_image(user_question, image_path=image_path)
            if response.status_code == 200:
                response_data = response.json()
                if "choices" in response_data and response_data["choices"]:
                    yield response_data["choices"][0]["message"]["content"]
                else:
                    yield "Error: Unexpected response format."
            else:
                yield f"Error: API call failed with status code {response.status_code}"
        else:
            for chunk in ask_openai(user_question):
                if (
                    chunk.choices and chunk.choices[0].delta.content
                ):  # Check for valid response chunks
                    print(f"Received chunk: {chunk.choices[0].delta.content}")
                    yield chunk.choices[0].delta.content  # Yield each chunk of content
    except Exception as e:
        print(f"Error during response generation: {e}")
        yield f"Error: {e}"


# Main function to run the chat application
def run():
    print("Running chat application.")
    # Sidebar for managing chats
    with st.sidebar:
        st.title("Chats Conversations")
        if st.button("New Chat"):
            # Start a new chat
            st.session_state.active_chat_id = str(
                uuid.uuid4()
            )  # Generate a new unique ID
            st.session_state.current_chat = []  # Clear current chat history
            new_chat = {
                "id": st.session_state.active_chat_id,  # Save the unique ID
                "name": f"Chat {len(st.session_state.chat_history) + 1}",  # Assign a name to the chat
                "messages": st.session_state.current_chat,  # Initialize with an empty message list
            }
            st.session_state.chat_history.append(new_chat)  # Add to the chat history
            save_chat_to_db(new_chat["id"], new_chat["name"], new_chat["messages"])
            print(f"Started new chat: {new_chat['name']} with ID {new_chat['id']}.")

        # Display existing chats in the sidebar for quick access
        for chat in st.session_state.chat_history:
            if chat["name"]:
                if st.button(chat["name"]):
                    # Load the selected chat
                    st.session_state.active_chat_id = chat["id"]
                    st.session_state.current_chat = chat["messages"]
                    print(f"Loaded chat: {chat['name']} with ID {chat['id']}.")

    if st.session_state.chat_history and st.session_state.active_chat_id:
        # Container for chat messages
        chat_container = st.container()

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
            print(
                f"Form submitted with prompt: {prompt} and uploaded file: {uploaded_file}"
            )
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
                print(f"Uploaded file saved to: {file_path}")
                st.session_state.current_chat.append(
                    ChatMessage(
                        image_path=file_path, sender=USER
                    )  # Save the image message
                )

            if prompt:
                # Open a chat message context for the AI response
                with st.chat_message("ai"):
                    # Stream and display the response chunk by chunk
                    for chunk in response_generator(
                        prompt, image_path=file_path if uploaded_file else None
                    ):
                        st.markdown(chunk, unsafe_allow_html=True)
                        # Add to current chat incrementally
                        if chunk.strip():
                            st.session_state.current_chat.append(
                                ChatMessage(content=chunk, sender=BOT)
                            )

            # Update the database with the latest chat messages
            for chat in st.session_state.chat_history:
                if chat["id"] == st.session_state.active_chat_id:
                    chat["messages"] = st.session_state.current_chat
                    save_chat_to_db(chat["id"], chat["name"], chat["messages"])
                    print(f"Chat {chat['name']} updated in database.")

            # Force chat container to refresh
            chat_container.empty()
            with chat_container:
                display_current_chat()
        else:
            with chat_container:
                display_current_chat()


if __name__ == "__main__":
    run()
