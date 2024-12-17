import streamlit as st
from openai import OpenAI

# from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel


class ChatMessage(BaseModel):
    sender: str
    content: str


USER = "user"
BOT = "bot"


def app_session_init():
    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = [
            ChatMessage(content="Hello, how can I help you?", sender=BOT)
        ]

    chat_history = st.session_state["chat_history"]

    for history in chat_history:
        if history.sender == BOT:
            st.chat_message("ai").write(history.content)

        if history.sender == USER:
            st.chat_message("human").write(history.content)


LLM = "gpt-4o"
client = OpenAI()


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
    st.set_page_config(page_title="Chat Application")
    st.header("Chat :blue[Application]")
    # st.selectbox("Select LLM:", get_models(), key="selected_model")

    app_session_init()
    prompt = st.chat_input("Add your prompt...")

    # selected_model = st.session_state["selected_model"]
    # print("Selected model: ", selected_model)
    # # llm = ChatOllama(model=selected_model, temperature=0.7)

    if prompt:
        st.chat_message("user").write(prompt)
        st.session_state["chat_history"] += [ChatMessage(content=prompt, sender=USER)]
        output = response_generator(prompt)

        with st.chat_message("ai"):
            ai_message = st.write_stream(output)

        st.session_state["chat_history"] += [
            ChatMessage(content=ai_message, sender=BOT)
        ]


if __name__ == "__main__":
    run()
