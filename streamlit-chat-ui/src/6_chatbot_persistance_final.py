import streamlit as st
import uuid
import sqlite3
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel

# Initialize SQLite DB or connect to existing database named 'chats.db'.
# 'check_same_thread=False' allows use of the same connection across multiple threads.
conn = sqlite3.connect('chats.db', check_same_thread=False)
c = conn.cursor()

# Create 'chats' table if it doesn't exist.
# Each chat has a unique id (UUID) and a user-defined name.
c.execute('''
CREATE TABLE IF NOT EXISTS chats (
    id TEXT PRIMARY KEY,
    name TEXT
)
''')

# Create 'messages' table if it doesn't exist.
# Each message is associated with a chat, has a sender, content, and timestamp.
c.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id TEXT,
    sender TEXT,
    content TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Commit these changes so our table structures are guaranteed.
conn.commit()

class ChatMessage(BaseModel):
    # Pydantic model to represent a single chat message.
    # sender can be either 'BOT' or 'USER'.
    sender: str  # BOT, USER
    content: str

# Constants to help with code readability.
USER = "user"
BOT = "bot"

# This is the model name for OpenAI's GPT.
LLM = "gpt-4o"
client = OpenAI()

# Streamlit app heading.
st.header("Chat :blue[Application]")

# Helper functions to interact with the SQLite database.

def load_all_chats():
    """Load all chats and messages into session_state from the database."""
    # Clear current in-memory chats.
    st.session_state["all_chats"] = {}

    # Retrieve every chat record from 'chats' table.
    c.execute("SELECT id, name FROM chats")
    for row in c.fetchall():
        chat_id, chat_name = row
        # For each chat, fetch its messages from 'messages' table, ordered by ID.
        c.execute("SELECT sender, content FROM messages WHERE chat_id=? ORDER BY id", (chat_id,))
        msgs = [ChatMessage(sender=m[0], content=m[1]) for m in c.fetchall()]
        # Store them in session_state under the specific chat_id.
        st.session_state["all_chats"][chat_id] = {
            "name": chat_name,
            "messages": msgs
        }

def create_new_chat():
    """Create a new chat record in both the DB and session_state."""
    # Generate a new UUID for our new chat.
    new_chat_uuid = str(uuid.uuid4())

    # Insert into 'chats' table with a default name 'New Chat'.
    c.execute("INSERT INTO chats (id, name) VALUES (?, ?)", (new_chat_uuid, "New Chat"))

    # Insert the default BOT greeting message into 'messages' table.
    c.execute("INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)", (new_chat_uuid, BOT, "Hello, how can I help you?"))

    # Save the changes to the database.
    conn.commit()

    # Reflect the changes in the session_state so the UI can see them.
    st.session_state["all_chats"][new_chat_uuid] = {
        "name": "New Chat",
        "messages": [ChatMessage(sender=BOT, content="Hello, how can I help you?")]
    }

    # Set the newly created chat as the active, selected chat.
    st.session_state["selected_chat"] = new_chat_uuid

def save_message_to_db(chat_id, sender, content):
    """Save a single message to the database."""
    # Insert the user or bot message into the 'messages' table, linked by chat_id.
    c.execute("INSERT INTO messages (chat_id, sender, content) VALUES (?, ?, ?)", (chat_id, sender, content))
    conn.commit()


def rename_chat_in_db(chat_id, new_name):
    """Update the chat name in the database."""
    # Update the name of the chat in the 'chats' table.
    c.execute("UPDATE chats SET name=? WHERE id=?", (new_name, chat_id))
    conn.commit()


# Ensure session_state is initialized with data from the database.
if "all_chats" not in st.session_state:
    load_all_chats()

# Keep track of which chat is currently selected.
if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = None

# Sidebar: Display existing chats and a button to create a new one.
with st.sidebar:
    st.subheader("Conversations")

    # If user clicks 'New Chat' button, call create_new_chat().
    if st.button("New Chat", key="new_chat_button"):
        create_new_chat()

    # Display existing chat sessions in reverse order so new ones appear at the top.
    # Each chat is a clickable button.
    for chat_id in reversed(list(st.session_state["all_chats"].keys())):
        chat_data = st.session_state["all_chats"][chat_id]
        button_label = chat_data["name"]
        if st.button(button_label, key=f"chat_button_{chat_id}"):
            st.session_state["selected_chat"] = chat_id

# Debug: Print all chats to the console (useful for development purposes).
print(f"conversations : {st.session_state['all_chats']}")

# Functions for interacting with OpenAI.
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

def response_generator(user_question):
    """Yield the OpenAI response incrementally, for streaming display."""
    for chunk in ask_openai(user_question):
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content  # Stream response incrementally

# Main app logic to handle user input and display the conversation.
def run():
    # If a chat is selected, display its conversation.
    if st.session_state["selected_chat"]:
        chat_id = st.session_state["selected_chat"]
        chat_data = st.session_state["all_chats"][chat_id]
        chat_history = chat_data["messages"]

        # Display each message in the chat in the correct style (ai or human).
        for msg in chat_history:
            if msg.sender == BOT:
                st.chat_message("ai").write(msg.content)
            else:
                st.chat_message("human").write(msg.content)

        # Provide a text input for the user at the bottom of the chat.
        prompt = st.chat_input("Add your prompt...")
        if prompt:
            # Optionally rename the conversation using the last user prompt.
            st.session_state["all_chats"][chat_id]["name"] = prompt
            rename_chat_in_db(chat_id, prompt)

            # Display the user message in the chat.
            st.chat_message("human").write(prompt)

            # Save user message in memory and database.
            chat_history.append(ChatMessage(content=prompt, sender=USER))
            save_message_to_db(chat_id, USER, prompt)

            # Generate response by calling OpenAI.
            output = response_generator(prompt)
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)
            chat_history.append(ChatMessage(content=ai_message, sender=BOT))
            # Save chatbot response
            save_message_to_db(chat_id, BOT, ai_message)
                                    
    else:
        # If no chat is selected, prompt the user to create or select one.
        st.write("Select or create a new chat from the sidebar to begin.")

# Call run() to execute the Streamlit app.
run()
