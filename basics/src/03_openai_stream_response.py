import os

from dotenv import load_dotenv
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk
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

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    user_question = """
        Generate the content for creating a course on python programming.
        """
    response: ChatCompletion = ask_openai(user_question)
