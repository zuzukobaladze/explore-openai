import streamlit as st
import uuid
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()
from pydantic import BaseModel

class ChatMessage(BaseModel):
    sender: str  # BOT, USER
    content: str

USER = "user"
BOT = "bot"

LLM = "gpt-4o"
client = OpenAI()

st.header("Chat :blue[Application]")

# Initialize a container to store multiple chats, each keyed by a UUID
if "all_chats" not in st.session_state:
    st.session_state["all_chats"] = {}

# Track which chat (by UUID) is currently selected
if "selected_chat" not in st.session_state:
    st.session_state["selected_chat"] = None

# Sidebar: Display existing chats and a new chat button
with st.sidebar:
    st.subheader("Conversations")

    # Place 'New Chat' button at the top
    if st.button("New Chat", key="new_chat_button"):
        new_chat_uuid = str(uuid.uuid4())
        st.session_state["all_chats"][new_chat_uuid] = {
            "name": "New Chat",
            "messages": [ChatMessage(sender=BOT, content="Hello, how can I help you?")]
        }
        st.session_state["selected_chat"] = new_chat_uuid

    # Display existing chat sessions in reverse order so new ones appear at the top.
    # Add a unique key parameter to each button to avoid duplicate IDs.
    for chat_id in reversed(list(st.session_state["all_chats"].keys())):
        chat_data = st.session_state["all_chats"][chat_id]
        button_label = chat_data["name"]
        if st.button(button_label, key=f"chat_button_{chat_id}"):
            st.session_state["selected_chat"] = chat_id

print(f"conversations : {st.session_state["all_chats"]}")

# If a chat is selected, display its conversation and the chat input
if st.session_state["selected_chat"]:
    chat_id = st.session_state["selected_chat"]
    chat_data = st.session_state["all_chats"][chat_id]
    chat_history = chat_data["messages"]

    # Display chat history
    for msg in chat_history:
        if msg.sender == BOT:
            st.chat_message("ai").write(msg.content)
        else:
            st.chat_message("human").write(msg.content)

    # Functions for the chatbot
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

    # Main app logic to handle user input
    def run():
        prompt = st.chat_input("Add your prompt...")
        if prompt:
            # Optionally, rename the conversation using the last user prompt
            st.session_state["all_chats"][chat_id]["name"] = prompt

            # Display user message
            st.chat_message("human").write(prompt)

            # Save user message
            chat_history.append(ChatMessage(content=prompt, sender=USER))

            # Generate response
            output = response_generator(prompt)
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)

            # Save chatbot response
            chat_history.append(ChatMessage(content=ai_message, sender=BOT))

    if __name__ == "__main__":
        run()
else:
    st.write("Select or create a new chat from the sidebar to begin.")
