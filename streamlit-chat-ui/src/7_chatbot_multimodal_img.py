import base64
import os
import sqlite3
import uuid
from typing import Optional

import requests
import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

# Initialize SQLite DB or connect to existing database named 'chats.db'.
# 'check_same_thread=False' allows use of the same connection across multiple threads.
conn = sqlite3.connect("chats.db", check_same_thread=False)
c = conn.cursor()

# Attempt to create 'chats' table if it doesn't exist.
c.execute(
    """\nCREATE TABLE IF NOT EXISTS chats (\n    id TEXT PRIMARY KEY,\n    name TEXT\n)\n"""
)

# Attempt to create 'messages' table if it doesn't exist.
# We add an "image" column to store base64-encoded images if present.
c.execute(
    """\nCREATE TABLE IF NOT EXISTS messages (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    chat_id TEXT,\n    sender TEXT,\n    content TEXT,\n    image TEXT,\n    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP\n)\n"""
)

# Commit these changes so our table structures are guaranteed.
conn.commit()


class ChatMessage(BaseModel):
    # Pydantic model to represent a single chat message.
    # sender can be either 'BOT' or 'USER'.
    sender: str  # BOT, USER
    content: str
    image: Optional[str] = None  # store base64-encoded image if any


USER = "user"
BOT = "bot"

# This is the model name for OpenAI's GPT.
LLM = "gpt-4o"

from openai import OpenAI

client = OpenAI()

st.header("Chat :blue[Application]")

# Helper functions to interact with the SQLite database.


def load_all_chats():
    st.session_state["all_chats"] = {}
    c.execute("SELECT id, name FROM chats")
    for row in c.fetchall():
        chat_id, chat_name = row
        c.execute(
            "SELECT sender, content, image FROM messages WHERE chat_id=? ORDER BY id",
            (chat_id,),
        )
        msgs = []
        for m in c.fetchall():
            sender, content, image = m
            content = content if content else ""
            msgs.append(ChatMessage(sender=sender, content=content, image=image))
        st.session_state["all_chats"][chat_id] = {"name": chat_name, "messages": msgs}


def create_new_chat():
    new_chat_uuid = str(uuid.uuid4())
    c.execute("INSERT INTO chats (id, name) VALUES (?, ?)", (new_chat_uuid, "New Chat"))
    c.execute(
        "INSERT INTO messages (chat_id, sender, content, image) VALUES (?, ?, ?, ?)",
        (new_chat_uuid, BOT, "Hello, how can I help you?", None),
    )
    conn.commit()

    st.session_state["all_chats"][new_chat_uuid] = {
        "name": "New Chat",
        "messages": [ChatMessage(sender=BOT, content="Hello, how can I help you?")],
    }
    st.session_state["selected_chat"] = new_chat_uuid


def save_message_to_db(chat_id, sender, content, image=None):
    c.execute(
        "INSERT INTO messages (chat_id, sender, content, image) VALUES (?, ?, ?, ?)",
        (chat_id, sender, content, image),
    )
    conn.commit()


def rename_chat_in_db(chat_id, new_name):
    c.execute("UPDATE chats SET name=? WHERE id=?", (new_name, chat_id))
    conn.commit()


# Initialize session state
if "all_chats" not in st.session_state:
    load_all_chats()

if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = None

# Sidebar
with st.sidebar:
    st.subheader("Conversations")

    if st.button("New Chat", key="new_chat_button"):
        create_new_chat()

    for chat_id in reversed(list(st.session_state["all_chats"].keys())):
        chat_data = st.session_state["all_chats"][chat_id]
        button_label = chat_data["name"]
        if st.button(button_label, key=f"chat_button_{chat_id}"):
            st.session_state["selected_chat"] = chat_id

print(f"conversations : {st.session_state['all_chats']}")

# The streaming LLM call


def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
):
    response = client.chat.completions.create(
        model=LLM,
        messages=[{"role": "user", "content": user_question}],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
        stream=True,
    )
    return response


# Base64 encode/decode


def encode_image(file_bytes: bytes) -> str:
    return base64.b64encode(file_bytes).decode("utf-8")


def decode_image(base64_str: str) -> bytes:
    return base64.b64decode(base64_str)


# The function to handle image-based requests.
def ask_openai_image(
    user_question: str,
    base64_image: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
) -> str:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY')}",
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
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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

    if response.status_code == 200:
        resp_json = response.json()
        return resp_json["choices"][0]["message"]["content"]
    else:
        return f"Error: {response.status_code}, {response.text}"


# Main app


def run():
    if st.session_state["selected_chat"]:
        chat_id = st.session_state["selected_chat"]
        chat_data = st.session_state["all_chats"][chat_id]
        chat_history = chat_data["messages"]

        # Container for chat messages.
        with st.container():
            for msg in chat_history:
                if msg.sender == BOT:
                    with st.chat_message("ai"):
                        if msg.content:
                            st.write(msg.content)
                        if msg.image:
                            try:
                                st.image(decode_image(msg.image))
                            except Exception as e:
                                st.write(f"[Error displaying image: {e}]")
                else:
                    with st.chat_message("human"):
                        if msg.content:
                            st.write(msg.content)
                        if msg.image:
                            try:
                                st.image(decode_image(msg.image))
                            except Exception as e:
                                st.write(f"[Error displaying image: {e}]")

        # Container pinned at bottom for user input.
        with st.container():
            with st.form("user_input_form", clear_on_submit=True):
                prompt = st.text_input(
                    "Enter your prompt:"
                )  # text_input allows pressing Enter to submit
                image_file = st.file_uploader(
                    "Upload an image (optional)", type=["png", "jpg", "jpeg"]
                )
                submitted = st.form_submit_button("Send")

            if submitted:
                # rename conversation
                if prompt:
                    st.session_state["all_chats"][chat_id]["name"] = prompt
                    rename_chat_in_db(chat_id, prompt)

                # multimodal path
                if prompt and image_file is not None:
                    file_bytes = image_file.read()
                    image_b64 = encode_image(file_bytes)

                    with st.chat_message("human"):
                        st.write(prompt)
                        st.image(file_bytes)

                    # Save user text message
                    user_text_msg = ChatMessage(content=prompt, sender=USER)
                    chat_history.append(user_text_msg)
                    save_message_to_db(chat_id, USER, prompt, None)

                    # Save user image message
                    user_img_msg = ChatMessage(content="", sender=USER, image=image_b64)
                    chat_history.append(user_img_msg)
                    save_message_to_db(chat_id, USER, "", image_b64)

                    # Bot response
                    bot_response = ask_openai_image(prompt, image_b64)
                    with st.chat_message("ai"):
                        st.write(bot_response)
                    bot_msg = ChatMessage(content=bot_response, sender=BOT)
                    chat_history.append(bot_msg)
                    save_message_to_db(chat_id, BOT, bot_response, None)

                elif prompt and image_file is None:
                    # text-only path
                    with st.chat_message("human"):
                        st.write(prompt)

                    user_msg = ChatMessage(content=prompt, sender=USER)
                    chat_history.append(user_msg)
                    save_message_to_db(chat_id, USER, prompt)

                    # stream LLM response
                    output = ask_openai(prompt)
                    with st.chat_message("ai"):
                        ai_message = st.write_stream(output)

                    bot_msg = ChatMessage(content=ai_message, sender=BOT)
                    chat_history.append(bot_msg)
                    save_message_to_db(chat_id, BOT, ai_message)

                else:
                    pass

    else:
        st.write("Select or create a new chat from the sidebar to begin.")


run()
