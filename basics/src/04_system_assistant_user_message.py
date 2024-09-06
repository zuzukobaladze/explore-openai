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

    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "user", "content": user_question},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    user_question = "Hello"
    response: ChatCompletion = ask_openai(user_question)

    # Pretty print the entire response
    response = response.choices[0].message.content
    print(f"response : {response}")
