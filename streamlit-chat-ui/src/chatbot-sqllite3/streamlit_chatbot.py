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
