import streamlit as st
from openai import OpenAI

# from langchain_core.messages import AIMessage, HumanMessage


LLM = "gpt-4o"
client = OpenAI()

st.header("Chat :blue[Application]")

# chat_history = [AI Message, UserMessage, AIMessage, UserMessage]


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
    st.chat_message("ai").write("Hello, how can I help you ?")
    prompt = st.chat_input("Add your prompt...")

    if prompt:
        st.chat_message("human").write(prompt)

        with st.chat_message("ai"):
            st.write_stream(response_generator(prompt))


if __name__ == "__main__":
    run()
