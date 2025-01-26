import uuid

import streamlit as st
from db.chat_db import init_db, load_chats, load_messages, save_chat, save_messages
from model.chats_models import ChatMessage
from openai import OpenAI

# from langchain_core.messages import AIMessage, HumanMessage

init_db()


USER = "user"
BOT = "bot"

if "current_chat" not in st.session_state:
    st.session_state.current_chat = []  # Current chat history


if "chat_history" not in st.session_state:
    st.session_state.chat_history = load_chats()  # List of all chats

if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None
# Active chat ID

LLM = "gpt-4o"
client = OpenAI()


def display_sidebar():
    st.session_state.active_chat_id = str(uuid.uuid4())  # Generate a new unique ID
    st.session_state.current_chat = []  # Clear current chat
    save_chat(
        st.session_state.active_chat_id,
        f"Chat {len(st.session_state.chat_history) + 1}",
    )
    st.session_state.chat_history = load_chats()


def load_and_display_chat_by_id(chat_id, chat_name):
    if chat_name:
        # This the code places the button in the sidebar
        if st.button(chat_name):
            print("Chat ID: ", chat_id)
            # Load a saved chat into current chat
            st.session_state.active_chat_id = chat_id
            st.session_state.current_chat = load_messages(chat_id)


with st.sidebar:
    st.title("Chats Conversations")
    if st.button("New Chat"):
        # Start a new chat
        display_sidebar()

    for chat_id, chat_name in st.session_state.chat_history:
        load_and_display_chat_by_id(chat_id, chat_name)


def display_current_chat():
    """Display all chat messages in the current chat."""
    for message in st.session_state.current_chat:
        # print("Message in display_current_chat: ", message)
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
    # st.set_page_config(page_title="Chat Application")
    st.header("Chat :blue[Application]")
    # st.selectbox("Select LLM:", get_models(), key="selected_model")

    # app_session_init()
    display_current_chat()

    if st.session_state.chat_history:
        prompt = st.chat_input("Add your prompt...")

        if prompt:
            st.chat_message("user").write(prompt)
            output = response_generator(prompt)
            st.session_state.current_chat.append(
                ChatMessage(content=prompt, sender=USER)
            )

            with st.chat_message("ai"):
                ai_message = st.write_stream(output)

            st.session_state.current_chat.append(
                ChatMessage(content=ai_message, sender=BOT)
            )
            save_messages(
                st.session_state.active_chat_id, st.session_state.current_chat
            )


if __name__ == "__main__":
    run()
