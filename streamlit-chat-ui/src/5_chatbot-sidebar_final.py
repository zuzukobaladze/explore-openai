import uuid

import streamlit as st
from openai import OpenAI

# from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel


# Define the structure of a chat message
class ChatMessage(BaseModel):
    sender: str  # Indicates the sender of the message, either "user" or "bot"
    content: str  # The actual content of the message


# Constants to represent the sender types
USER = "user"
BOT = "bot"

# Set up the header for the Streamlit app
st.header("Chat :blue[Application]")

# Initialize the session state variable to hold the current chat if not already present.
if "current_chat" not in st.session_state:
    st.session_state.current_chat = []  # Current chat history

# This variable stores all past chat sessions, allowing users to revisit previous conversations.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []  # List of all chats

# Initialize the session state variable to hold the active chat ID if not already present.
# The active_chat_id is used to track the chat session currently in use by the user.
if "active_chat_id" not in st.session_state:
    st.session_state.active_chat_id = None  # Active chat ID

# OpenAI model identifier
LLM = "gpt-4o"
# Initialize the OpenAI client
client = OpenAI()

# Sidebar for chat navigation and controls
with st.sidebar:
    # This is where the sidebar is defined for displaying chat history and controls.
    st.title("Chats Conversations")
    if st.button("New Chat"):
        # Clicking this button starts a new chat session by generating a unique ID and resetting the current chat.
        st.session_state.active_chat_id = str(uuid.uuid4())  # Generate a new unique ID
        st.session_state.current_chat = []  # Clear current chat
        st.session_state.chat_history.append(
            {
                "id": st.session_state.active_chat_id,  # Save the current active chat ID
                "name": f"Chat {len(st.session_state.chat_history) + 1}",
                "messages": st.session_state.current_chat,
                "last_message": "",
            }
        )

    # To Display the chats in the sidebar with last message preview
    for chat in st.session_state.chat_history:
        print("Chat: ", chat)  # Debugging output for chat details
        if chat["name"]:
            # Display the last message preview with truncation if necessary
            last_message_preview = chat.get("last_message", "No messages yet")[:30] + (
                "..." if len(chat.get("last_message", "")) > 30 else ""
            )
            if st.button(f"{chat['name']} - {last_message_preview}"):
                print("Chat ID: ", chat["id"])  # Debugging output for chat ID
                # Load a saved chat into current chat
                st.session_state.active_chat_id = chat["id"]
                st.session_state.current_chat = chat["messages"]


# Function to display the messages in the current chat
def display_current_chat():
    """Display all chat messages in the current chat."""
    for message in st.session_state.current_chat:
        # Check if the message has content
        if message.content:
            if message.sender == BOT:
                st.chat_message("ai").write(message.content)  # Display bot messages

            if message.sender == USER:
                st.chat_message("human").write(message.content)  # Display user messages


# Function to send a request to OpenAI and receive a response
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
):
    """
    Send a question to OpenAI and get a streamed response.

    Args:
        user_question (str): The question to send to the OpenAI API.
        temperature (float): Sampling temperature for randomness.
        top_p (float): Nucleus sampling for diversity.
        max_tokens (int): Maximum tokens in the response.

    Returns:
        response: The OpenAI response object.
    """
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


# Function to generate responses incrementally for smoother streaming
def response_generator(user_question):
    """
    Generate responses incrementally from OpenAI for smoother streaming.

    Args:
        user_question (str): The user's input question to be sent to the OpenAI API.

    Yields:
        str: Incremental chunks of the response content from OpenAI.
    """
    for chunk in ask_openai(user_question):
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content  # Stream response incrementally


# Main function to run the chat application
def run():
    """Run the chat application."""
    display_current_chat()  # Display existing chat messages

    if st.session_state.chat_history:
        prompt = st.chat_input("Add your prompt...")  # Input box for user prompts

        if prompt:
            st.chat_message("user").write(prompt)  # Display user input
            output = response_generator(prompt)  # Generate AI response
            st.session_state.current_chat.append(
                ChatMessage(content=prompt, sender=USER)  # Save user message
            )

            with st.chat_message("ai"):
                ai_message = st.write_stream(output)  # Stream and display AI response

            st.session_state.current_chat.append(
                ChatMessage(content=ai_message, sender=BOT)  # Save AI message
            )

            # Update the last message for the current chat in chat history
            for chat in st.session_state.chat_history:
                if chat["id"] == st.session_state.active_chat_id:
                    chat["last_message"] = prompt


# Entry point for the application
if __name__ == "__main__":
    run()
    # ChatGPT - Conversation Link
    #  https://chatgpt.com/share/678f8213-1cb8-8010-ad7b-6821a5c5214e
