import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


def ask_openai(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response


def zero_shot_prompting():
    text = """
        The weather is beautiful today.
    """
    prompt = f"""
        Translate the following sentence within triple backticks into French.\
        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")


def zero_shot_prompting_1():
    text = """
    The product arrived on time, but it was damaged and didn’t work."

    """
    prompt = f"""
        What is the sentiment of this sentence within triple backticks ?\
        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")


if __name__ == "__main__":
    zero_shot_prompting()
    zero_shot_prompting_1()
