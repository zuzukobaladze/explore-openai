# This script implements a Streamlit chatbot application capable of handling text-based and image-based queries.
# It integrates with an OpenAI-like API for generating responses to user prompts and can store the conversation in a SQLite database.

import base64
import logging
import os
import sqlite3
import uuid

import requests
import streamlit as st
from openai import OpenAI
from pydantic import BaseModel
from dotenv import load_dotenv
load_dotenv()

# Configure basic logging to debug issues or track general flow
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# "ChatMessage" is a data model representing a single message in a conversation.
# It includes a 'sender' (either 'user' or 'bot') and the 'content' string.
class ChatMessage(BaseModel):
    sender: str  # "user" or "bot"
    content: str


# Constants representing the sender
USER = "user"
BOT = "bot"

# Display a header at the top of the Streamlit app
st.header("Chat :blue[Application]")

# The path where we store our SQLite database
DB_PATH = "chat_history.db"

# Initialize the database by creating the necessary tables if they don't exist


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a "chats" table to keep track of different chat sessions
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS chats (
            id TEXT PRIMARY KEY,
            name TEXT,
            last_message TEXT
        )"""
    )

    # Create a "messages" table to store individual messages linked to a chat
    cursor.execute(
        """CREATE TABLE IF NOT EXISTS messages (
            chat_id TEXT,
            sender TEXT,
            content TEXT,
            FOREIGN KEY(chat_id) REFERENCES chats(id)
        )"""
    )

    conn.commit()
    conn.close()


# Call the initialization function right away
init_db()

# Helper function to save or update a chat session in the "chats" table


def save_chat_to_db(chat_id, name, last_message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO chats (id, name, last_message) VALUES (?, ?, ?)",
        (chat_id, name, last_message),
    )
    conn.commit()
    conn.close()


# Helper function to save an individual message in the "messages" table


def save_message_to_db(chat_id, sender, content):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)",
        (chat_id, sender, content),
    )
    conn.commit()
    conn.close()


# Load all chat sessions from the "chats" table, including their stored messages


def load_chat_history():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chats")
    chats = cursor.fetchall()
    conn.close()

    # For each row in the "chats" table, fetch its associated messages
    return [
        {
            "id": c[0],
            "name": c[1],
            "last_message": c[2],
            "messages": load_messages(c[0]),
        }
        for c in chats
    ]


# Load all messages for a specific chat from the "messages" table


def load_messages(chat_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT sender, content FROM messages WHERE chat_id = ?", (chat_id,))
    msgs = cursor.fetchall()
    conn.close()
    return [ChatMessage(sender=m[0], content=m[1]) for m in msgs]


# Initialize session state variables for the current chat, chat history, and active chat ID
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []

if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chat_history()

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None

# Setup for the OpenAI integration
LLM = "gpt-4o"  # The model name
api_key = os.environ.get("OPENAI_API_KEY")  # Retrieve the API key from environment
client = OpenAI()  # Initialize the client

# Create a sidebar that allows users to manage multiple chat sessions
with st.sidebar:
    st.title("Chats Conversations")  # Sidebar title

    # Button to start a new chat
    if st.button("New Chat"):
        st.session_state.active_chat_id = str(uuid.uuid4())  # Unique ID for new chat
        st.session_state.current_chat = []
        new_chat = {
            "id": st.session_state.active_chat_id,
            "name": f"Chat {len(st.session_state.chat_history) + 1}",
            "messages": st.session_state.current_chat,
            "last_message": "",
        }
        st.session_state.chat_history.append(new_chat)
        # Persist new chat in the DB
        save_chat_to_db(new_chat["id"], new_chat["name"], new_chat["last_message"])

    # Show a list of existing chat sessions
    for cht in st.session_state.chat_history:
        preview = cht.get("last_message", "No messages yet")[:30]
        # If last_message is too long, add "..." for brevity
        if len(cht.get("last_message", "")) > 30:
            preview += "..."

        # Clicking a chat button loads its ID and messages into session state
        if st.button(f"{cht['name']} - {preview}"):
            st.session_state.active_chat_id = cht["id"]
            st.session_state.current_chat = cht["messages"]

# Function to ask the text-based OpenAI LLM for a streamed response
# This helps with longer outputs because it streams partial results


def ask_openai(user_question, temperature=1.0, top_p=1.0, max_tokens=256):
    resp = client.chat.completions.create(
        model=LLM,
        messages=[{"role": "user", "content": user_question}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stream=True,
    )
    return resp


# Generator function that yields partial text chunks from the LLM


def response_generator(user_question):
    streamed_text = ""
    # We iterate over the streaming response from ask_openai
    for chunk in ask_openai(user_question):
        if chunk.choices and chunk.choices[0].delta.content:
            part = chunk.choices[0].delta.content
            streamed_text += part
            yield part
    logger.info(f"Full streamed response: {streamed_text}")


# Function to ask the LLM a question that also includes an image in base64 format


def ask_openai_image(
    user_question, base64_image, temperature=1.0, top_p=1.0, max_tokens=500
):
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    # The payload includes a mix of text and image_url content for the LLM to process
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_question},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    # Log the request and the response for debugging
    logger.info("ask_openai_image payload:")
    logger.info(payload)
    logger.info(f"Status: {r.status_code}  Response: {r.json()}")

    return r


# Function to display all messages in the current chat
# If a user message contains base64 image data, we decode and display that image


def display_chat():
    print("inside display chat")  # Debugging print statement
    for msg in st.session_state.current_chat:
        if msg.sender == USER:
            # Check if the user message includes an inline base64 image
            if "data:image/jpeg;base64," in msg.content:
                splitted = msg.content.split("data:image/jpeg;base64,")
                text_part = splitted[0].strip()
                base64_part = splitted[1] if len(splitted) > 1 else None
                # If there is text before the image, we display it
                if text_part:
                    st.chat_message("human").write(text_part)
                # Then we decode and display the image, if present
                if base64_part:
                    try:
                        img_bytes = base64.b64decode(base64_part.strip())
                        st.chat_message("human").image(img_bytes)
                    except Exception as e:
                        logger.error(f"Error decoding base64 image: {e}")
                        st.chat_message("human").write("[Error decoding image]")
            else:
                # If no image is included, display text only
                st.chat_message("human").write(msg.content)
        else:
            # For bot messages, display them as AI messages
            st.chat_message("ai").write(msg.content)


# This function handles user submissions from the form, either text or an image + text


def handle_submission(prompt: str, image_file):
    if not st.session_state.active_chat_id:
        return  # If no active chat, do nothing

    # Display the existing conversation first, so new messages appear after
    display_chat()

    last_msg = ""

    # If an image was uploaded
    if image_file:
        image_bytes = image_file.read()
        b64 = base64.b64encode(image_bytes).decode("utf-8")
        # Combine prompt text and the image data as a single user message
        combined = prompt + ("\n" if prompt else "") + f"data:image/jpeg;base64,{b64}"

        # Display user's text & image
        st.chat_message("user").write(prompt)
        st.chat_message("user").image(image_bytes)

        # Save message to DB & session state
        save_message_to_db(st.session_state.active_chat_id, USER, combined)
        st.session_state.current_chat.append(ChatMessage(sender=USER, content=prompt))
        st.session_state.current_chat.append(
            ChatMessage(sender=USER, content=f"data:image/jpeg;base64,{b64}")
        )

        # Update the last message preview to reflect text + image
        if prompt.strip():
            last_msg = f"{prompt} [IMAGE]"
        else:
            last_msg = "[IMAGE]"

        # Call the LLM endpoint that handles images
        resp = ask_openai_image(prompt, b64)
        data = resp.json()
        print(f"data : {data}")  # Debugging
        ai_dict = data.get("choices", [{}])[0].get("message", {})
        print(f"ai_dict : {ai_dict}")  # Debugging
        ai_content = ai_dict.get("content", "[No content]")

        # Display AI's response
        with st.chat_message("ai"):
            ai_full_text = st.write(ai_content)

        # Append AI's message to the session state and DB
        st.session_state.current_chat.append(
            ChatMessage(sender=BOT, content=ai_content)
        )
        save_message_to_db(st.session_state.active_chat_id, BOT, ai_content)

    # If only text was provided
    elif prompt.strip():
        # Show the user's text
        st.chat_message("user").write(prompt)

        # Create a generator for streaming AI response
        out = response_generator(prompt)
        # Save user message
        st.session_state.current_chat.append(ChatMessage(sender=USER, content=prompt))
        save_message_to_db(st.session_state.active_chat_id, USER, prompt)
        last_msg = prompt

        # Stream AI response in the UI
        with st.chat_message("ai"):
            ai_full_text = st.write_stream(out)
        logger.info(f"ask_openai text response: {ai_full_text}")

        # Save AI's response in session state & DB
        st.session_state.current_chat.append(
            ChatMessage(sender=BOT, content=ai_full_text)
        )
        save_message_to_db(st.session_state.active_chat_id, BOT, ai_full_text)

    # Update the chat's "last_message" metadata
    if last_msg:
        for c in st.session_state.chat_history:
            if c["id"] == st.session_state.active_chat_id:
                c["last_message"] = last_msg
                save_chat_to_db(c["id"], c["name"], last_msg)


# Main function to orchestrate the UI


def run():
    if st.session_state.active_chat_id is None:
        # If no chat is selected or created, instruct user
        st.write("Select or create a chat from the sidebar.")
        return

    # Container for existing conversation
    chat_container = st.container()

    # Container for the input form
    form_container = st.container()

    # Present the form at the bottom
    with form_container:
        with st.form("input_form", clear_on_submit=True):
            prompt = st.text_input("Enter your prompt")
            image_file = st.file_uploader(
                "Upload an image", type=["jpg", "jpeg", "png"]
            )
            submitted = st.form_submit_button("Submit")

    # Ensure that previously displayed messages remain at the top
    with chat_container:
        if submitted:
            handle_submission(prompt, image_file)
        else:
            display_chat()


# If we're running this script directly, start the app
if __name__ == "__main__":
    run()

# ChatGPT Link
# https://chatgpt.com/share/67962c16-46e4-8010-a63d-bc1f15e15aa0
