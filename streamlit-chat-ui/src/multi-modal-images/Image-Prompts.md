

## Step 1 : Give the context of the app

```
I have a streamlit app that stores and retrieves conversation in the DB.

Here is the code :

Steamlit code : streamlit_chatbot.py
```python

import uuid

import streamlit as st
from db_utils import init_db, load_chats_from_db, save_chat_to_db
from openai import OpenAI
from pydantic import BaseModel

init_db()


class ChatMessage(BaseModel):
    sender: str
    content: str


USER = "user"
BOT = "bot"

st.header("Chat :blue[Application]")

if "current_chat" not in st.session_state:
    st.session_state.current_chat = []  # Current chat history

if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chats_from_db()  # Load from DB

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None  # Active chat ID

LLM = "gpt-4o"
client = OpenAI()

with st.sidebar:
    st.title("Chats Conversations")
    if st.button("New Chat"):
        # Start a new chat
        st.session_state.active_chat_id = str(uuid.uuid4())  # Generate a new unique ID
        st.session_state.current_chat = []  # Clear current chat
        new_chat = {
            "id": st.session_state.active_chat_id,  # Save the current active chat ID
            "name": f"Chat {len(st.session_state.chat_history) + 1}",
            "messages": st.session_state.current_chat,
        }
        st.session_state.chat_history.append(new_chat)
        save_chat_to_db(new_chat["id"], new_chat["name"], new_chat["messages"])

    # To Display the chats in the sidebar
    for chat in st.session_state.chat_history:
        if chat["name"]:
            if st.button(chat["name"]):
                st.session_state.active_chat_id = chat["id"]
                st.session_state.current_chat = chat["messages"]


def display_current_chat():
    """Display all chat messages in the current chat."""
    for message in st.session_state.current_chat:
        if message.content:
            if message.sender == BOT:
                st.chat_message("ai").write(message.content)

            if message.sender == USER:
                st.chat_message("human").write(message.content)


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


def run():
    display_current_chat()

    if st.session_state.chat_history and st.session_state.active_chat_id:
        prompt = st.chat_input("Add your prompt...")

        if prompt:
            st.chat_message("user").write(prompt)
            output = response_generator(prompt)
            st.session_state.current_chat.append(
                ChatMessage(content=prompt, sender=USER)
            )

            with st.chat_message("ai"):
                ai_message = "".join(output)
                st.write(ai_message)

            st.session_state.current_chat.append(
                ChatMessage(content=ai_message, sender=BOT)
            )

            # Update the database with the latest chat
            for chat in st.session_state.chat_history:
                if chat["id"] == st.session_state.active_chat_id:
                    chat["messages"] = st.session_state.current_chat
                    save_chat_to_db(chat["id"], chat["name"], chat["messages"])


if __name__ == "__main__":
    run()
```
Db Code : db_utils.py

```python
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
```

## Step 2 : Introduce Multimodality

```
I want to make the app to be  multimodal.  Can you please update the Streamlit code to support image upload and the db to save message the images ?
```

## Step 3 : Explain the code 

```
Can you please explain the newly added code ?
```

## Step 4 :  Debugging Errors

- These are the different errors that I experience while doing this exercise myself.

### Error - 1


```
I get this error when i tried to upload the file.
FileNotFoundError: [Errno 2] No such file or directory: 'uploaded_images/e437f427-3885-4ff1-bb1c-96865a590b85_lion.jpeg'
```

### Error - 2

```
I keep getting this error 
pydantic_core._pydantic_core.ValidationError: 1 validation error for ChatMessage content Input should be a valid string [type=string_type, input_value=None, input_type=NoneType] For further information visit https://errors.pydantic.dev/2.10/v/string_type
```
## Step 5 : Aligning the input elements

### Prompt 1 

```
Can you  please place the upload button right above the chat_input field.
```

### Prompt 2

```
I want to move the file uploader to the bottom of the page.
```

![](../../images/1.png)


## Step 6 : Passing images to openai

``` python

Here is the function that already have the code to pass image information to the openai.

Now I want the streamlit app to take the image and the prompt. Pass this info to OpenAI and then display the result in the chatbot.

Please alter the code accordingly.

# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = "src/resources/invoice-template.png"

base64_image = encode_image(image_path)


# Call the openai chat.completions endpoint
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
) -> requests.Response:
    print(f"LLM : {LLM}")

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

    print(f"response  type : {type(response)}")
    return response
```