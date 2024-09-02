import os

from dotenv import load_dotenv
from openai import OpenAI, Stream
from openai.types.chat.chat_completion_chunk import ChatCompletionChunk

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


# Call the openai chat.completions endpoint
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 256,
) -> Stream[ChatCompletionChunk]:
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
    response: Stream[ChatCompletionChunk] = ask_openai(user_question)
    # print(f"response_temp_01 : {response.choices[0].message.content}")
    for chunk in response:
        # Extract the chunk text
        chunk_message = chunk.choices[0].delta.content  # Access the content directly
        if chunk_message:
            print(chunk_message, end="", flush=True)
