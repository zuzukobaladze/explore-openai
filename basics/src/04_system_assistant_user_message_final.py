import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


# Call the openai chat.completions endpoint
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
) -> ChatCompletion:
    print(f"LLM : {LLM}")

    system_message = """
        You are a helpful assistant that answers questions about Python programming!
        If the user asks any other questions then you can respond with I don't know in a funny way!
    """

    system_message = """
        You are a upset customer that is frustrated because the order is delayed!
    """

    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "system", "content": system_message},
            # {"role": "user", "content": "My name is Dilip"},
            {"role": "user", "content": user_question},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # Step 1 :
    # user_question = "How do I create a Thread in Python ?"

    # Step 2 :
    # user_question = "Share me some of the facts about python snake ?"

    # Step 3 :
    # user_question = "What's my name ?"
    # response: ChatCompletion = ask_openai(user_question)

    # Step 4 :
    user_question = "Hello"
    response: ChatCompletion = ask_openai(user_question)

    # Pretty print the entire response
    response = response.choices[0].message.content
    print(f"response : {response}")
