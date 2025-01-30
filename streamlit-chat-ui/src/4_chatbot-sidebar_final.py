import uuid
import streamlit as st
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

# Sidebar for conversation management
with st.sidebar:
    st.title("Conversations")

    # Ensure session state is ready
    if "conversations" not in st.session_state:
        st.session_state["conversations"] = {}

    # Create a new conversation (on top)
    if st.button("New Chat", key="new_chat_button"):
        new_id = str(uuid.uuid4())
        st.session_state["conversations"][new_id] = {
            "messages": [
                ChatMessage(sender=BOT, content="Hello, how can I help you ?")
            ],
            "display_name": "New Chat"
        }
        st.session_state["selected_conversation"] = new_id

    # Display existing conversations
    for conversation_key, convo_data in st.session_state["conversations"].items():
        if st.button(convo_data["display_name"], key=conversation_key):
            st.session_state["selected_conversation"] = conversation_key

print(f"conversations : { st.session_state["conversations"]}")
st.header("Chat :blue[Application]")

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
    # Only show chat if a conversation is selected
    if "selected_conversation" in st.session_state:
        convo_key = st.session_state["selected_conversation"]
        convo_data = st.session_state["conversations"][convo_key]
        chat_history = convo_data["messages"]

        # Display chat history
        for history in chat_history:
            if history.sender == BOT:
                st.chat_message("ai").write(history.content)
            elif history.sender == USER:
                st.chat_message("human").write(history.content)

        # Show the chat input box once a conversation is selected
        prompt = st.chat_input("Add your prompt...")
        if prompt:
            # Display user message
            st.chat_message("human").write(prompt)
            chat_history.append(ChatMessage(content=prompt, sender=USER))

            # Generate bot response
            output = response_generator(prompt)
            with st.chat_message("ai"):
                ai_message = st.write_stream(output)

            chat_history.append(ChatMessage(content=ai_message, sender=BOT))

            # Update display name to the last user prompt
            convo_data["display_name"] = prompt

            # Update session state with the new messages and display name
            st.session_state["conversations"][convo_key] = convo_data

    else:
        st.write("Please select or start a new chat from the sidebar.")


if __name__ == "__main__":
    run()
