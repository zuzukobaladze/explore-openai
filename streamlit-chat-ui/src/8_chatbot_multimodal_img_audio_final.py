import base64
import os
import sqlite3
import tempfile  # --- NEW/UPDATED CODE ---
import uuid
from typing import Union  # --- NEW/UPDATED CODE ---

import requests
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()


class ChatMessage(BaseModel):
    sender: str  # BOT, USER
    content: str
    image: Union[str, None] = None  # For storing base64 image if provided
    audio: Union[str, None] = (
        None  # --- NEW/UPDATED CODE --- For storing base64 audio if provided
    )


USER = "user"
BOT = "bot"

LLM = "gpt-4o"
client = OpenAI()

api_key = os.environ.get("OPENAI_API_KEY")

# -------------------------------------------------
# Database Persistence Layer
# -------------------------------------------------


def init_db():
    """Initialize the SQLite database and create tables if they don't exist."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS chats (
                chat_id TEXT PRIMARY KEY,
                name TEXT
            )
        """
        )
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                message_id TEXT PRIMARY KEY,
                chat_id TEXT,
                sender TEXT,
                content TEXT
            )
        """
        )
        # Attempt to add an image column if it doesn't exist
        try:
            c.execute("ALTER TABLE messages ADD COLUMN image TEXT")
        except:
            pass

        # --- NEW/UPDATED CODE ---
        # Attempt to add an audio column if it doesn't exist
        try:
            c.execute("ALTER TABLE messages ADD COLUMN audio TEXT")
        except:
            pass

        conn.commit()


def load_chats_from_db():
    """Load all chats and their messages from the DB into a dictionary."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("SELECT chat_id, name FROM chats")
        rows = c.fetchall()
        all_chats = {}
        for chat_id, name in rows:
            # --- UPDATED CODE to also fetch audio column ---
            c.execute(
                "SELECT sender, content, image, audio FROM messages WHERE chat_id=?",
                (chat_id,),
            )
            message_rows = c.fetchall()
            messages = []
            for sender, content, image_b64, audio_b64 in message_rows:
                messages.append(
                    ChatMessage(
                        sender=sender, content=content, image=image_b64, audio=audio_b64
                    )
                )
            all_chats[chat_id] = {"name": name, "messages": messages}
        return all_chats


def create_new_chat_in_db(chat_id: str, name: str, first_message: ChatMessage):
    """Create a new chat row in the DB and insert the first message."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO chats (chat_id, name) VALUES (?,?)", (chat_id, name))
        c.execute(
            """
            INSERT INTO messages (message_id, chat_id, sender, content, image, audio)
            VALUES (?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                chat_id,
                first_message.sender,
                first_message.content,
                first_message.image,
                first_message.audio,  # --- NEW/UPDATED CODE ---
            ),
        )
        conn.commit()


def add_message_to_db(chat_id: str, message: ChatMessage):
    """Add a new message to the messages table for the given chat."""
    with sqlite3.connect("chat.db") as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO messages (message_id, chat_id, sender, content, image, audio)
            VALUES (?,?,?,?,?,?)
            """,
            (
                str(uuid.uuid4()),
                chat_id,
                message.sender,
                message.content,
                message.image,
                message.audio,  # --- NEW/UPDATED CODE ---
            ),
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
        c.execute(
            "SELECT chat_id, sender, content, image, audio FROM messages"
        )  # --- NEW/UPDATED CODE ---
        return c.fetchall()


# Helper function to encode image


def encode_image(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


# --- NEW/UPDATED CODE ---
# Helper function to encode audio
def encode_audio(uploaded_file) -> str:
    if uploaded_file is None:
        return ""
    return base64.b64encode(uploaded_file.read()).decode("utf-8")


# -------------------------------------------------
# OpenAI Calls
# -------------------------------------------------


def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
):
    """Send a user question to OpenAI and stream the completion response."""
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


def ask_openai_image(
    user_question: str,
    base64_image: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
) -> requests.Response:
    """Send user text + image to an LLM endpoint and return a requests.Response."""
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

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
    return response


def response_generator(user_question: str):
    for chunk in ask_openai(user_question):
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content  # Stream response incrementally


# --- NEW/UPDATED CODE ---
# Audio-specific function provided
def ask_openai_audio(audio_path: str, prompt: str = ""):
    """
    Uses whisper-1 via client.audio.transcriptions.create to process the audio file.
    """
    print(f"LLM : {LLM}")
    audio_file = open(audio_path, "rb")
    transcription = client.audio.transcriptions.create(
        model="whisper-1", prompt=prompt, file=audio_file
    )
    print(f"Response Type : {type(transcription)}")
    return transcription


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


def display_chat_history(chat_history):
    for msg in chat_history:
        if msg.sender == BOT:
            with st.chat_message("ai"):
                st.write(msg.content)
        else:
            with st.chat_message("human"):
                if msg.content:
                    st.write(msg.content)
                if msg.image:
                    # Display the image in conversation
                    st.image(base64.b64decode(msg.image), use_container_width=True)
                # --- NEW/UPDATED CODE ---
                # Display audio if present
                if msg.audio:
                    st.audio(base64.b64decode(msg.audio))


# If a chat is selected, display its conversation and the chat input
if st.session_state["selected_chat"]:
    chat_id = st.session_state["selected_chat"]
    chat_data = st.session_state["all_chats"][chat_id]
    chat_history = chat_data["messages"]

    # Main app logic to handle user input (text + optional image/audio)
    def run():
        # Container for existing conversation
        chat_container = st.container()

        # Container for the input form
        form_container = st.container()

        with form_container:
            with st.form("user_input_form", clear_on_submit=True):
                prompt = st.text_input("Add your prompt...")
                uploaded_img = st.file_uploader(
                    "Upload an image", type=["png", "jpg", "jpeg"]
                )
                # --- NEW/UPDATED CODE ---
                # Additional file uploader for audio
                uploaded_audio = st.file_uploader(
                    "Upload an audio file", type=["mp3", "wav", "ogg", "m4a", "flac"]
                )
                submit_button = st.form_submit_button("Send")

        print(f"submit_button: {submit_button}")
        with chat_container:
            if submit_button:
                display_chat_history(chat_history=chat_history)

                # Show spinner
                spinner_text = "Processing your request..."
                if uploaded_img is not None and uploaded_audio is None:
                    spinner_text = "Uploading image and waiting for AI response..."
                elif uploaded_audio is not None and uploaded_img is None:
                    spinner_text = "Uploading audio and waiting for AI response..."
                elif uploaded_audio is not None and uploaded_img is not None:
                    spinner_text = (
                        "Uploading image + audio and waiting for AI response..."
                    )

                with st.spinner(spinner_text):
                    # Optionally, rename the conversation using the last user prompt if prompt is not empty
                    if prompt:
                        st.session_state["all_chats"][chat_id]["name"] = prompt
                        update_chat_name_in_db(chat_id, prompt)

                    # Encode the image if provided
                    img_b64 = None
                    if uploaded_img is not None:
                        img_b64 = encode_image(uploaded_img)

                    # --- NEW/UPDATED CODE ---
                    # Encode the audio if provided
                    audio_b64 = None
                    if uploaded_audio is not None:
                        audio_b64 = encode_audio(uploaded_audio)

                    # Display user message in the chat
                    with st.chat_message("human"):
                        if prompt:
                            st.write(prompt)
                        if img_b64:
                            st.image(base64.b64decode(img_b64), use_column_width=True)
                        # --- NEW/UPDATED CODE ---
                        if audio_b64:
                            st.audio(base64.b64decode(audio_b64))

                    # Save user message to DB
                    user_msg = ChatMessage(
                        content=prompt if prompt else "",
                        sender=USER,
                        image=img_b64,
                        audio=audio_b64,  # --- NEW/UPDATED CODE ---
                    )
                    chat_history.append(user_msg)
                    add_message_to_db(chat_id, user_msg)

                    # Decide which OpenAI call to make:
                    # 1) If audio is present (with or without prompt) => ask_openai_audio
                    # 2) else if image is present => ask_openai_image
                    # 3) else use ask_openai
                    if audio_b64:
                        # --- NEW/UPDATED CODE ---
                        # Write the base64 audio to a temporary file and call ask_openai_audio
                        with tempfile.NamedTemporaryFile(
                            suffix=".wav", delete=False
                        ) as tmp_file:
                            tmp_file.write(base64.b64decode(audio_b64))
                            tmp_file_path = tmp_file.name

                        response = ask_openai_audio(tmp_file_path, prompt)
                        # Here, 'response.text' is replaced by 'response' for the transcription object
                        # We typically get back a 'Transcription' object from the whisper endpoint
                        if response and hasattr(response, "text"):
                            bot_content = response.text
                            with st.chat_message("ai"):
                                st.write(bot_content)

                            bot_msg = ChatMessage(content=bot_content, sender=BOT)
                            chat_history.append(bot_msg)
                            add_message_to_db(chat_id, bot_msg)
                        else:
                            with st.chat_message("ai"):
                                st.write("Error: Could not retrieve transcription.")
                            bot_msg = ChatMessage(
                                content="Error: Could not retrieve transcription.",
                                sender=BOT,
                            )
                            chat_history.append(bot_msg)
                            add_message_to_db(chat_id, bot_msg)

                    elif img_b64 and prompt:
                        # If there's an image and prompt
                        response = ask_openai_image(prompt, img_b64)
                        if response.status_code == 200:
                            data = response.json()
                            bot_content = data["choices"][0]["message"]["content"]

                            with st.chat_message("ai"):
                                st.write(bot_content)

                            bot_msg = ChatMessage(content=bot_content, sender=BOT)
                            chat_history.append(bot_msg)
                            add_message_to_db(chat_id, bot_msg)
                        else:
                            with st.chat_message("ai"):
                                st.write(
                                    f"Error: {response.status_code} - {response.text}"
                                )

                            bot_msg = ChatMessage(
                                content=f"Error: {response.status_code}",
                                sender=BOT,
                            )
                            chat_history.append(bot_msg)
                            add_message_to_db(chat_id, bot_msg)

                    elif prompt:
                        # If only prompt (no image, no audio)
                        output = response_generator(prompt)
                        with st.chat_message("ai"):
                            ai_message = st.write_stream(output)

                        bot_msg = ChatMessage(content=ai_message, sender=BOT)
                        chat_history.append(bot_msg)
                        add_message_to_db(chat_id, bot_msg)
                    else:
                        st.warning(
                            "Please enter a prompt, upload an image, or upload an audio."
                        )
            else:
                # Display chat history
                display_chat_history(chat_history=chat_history)

    if __name__ == "__main__":
        run()
else:
    st.write("Select or create a new chat from the sidebar to begin.")
