import base64
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")
# image_url = "https://drive.google.com/file/d/1tCgKNVxDTTivWG4LOHL1DOaaRuptztBH/edit"
image_url = "https://drive.google.com/uc?export=view&id=1tCgKNVxDTTivWG4LOHL1DOaaRuptztBH"

# Call the openai chat.completions endpoint
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
) -> ChatCompletion:
    print(f"LLM : {LLM}")

    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": user_question,
                    },
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # Step 4 :
    user_question = """
    Hello, Extract the info from this invoice image in json format.
    Do not include ```json in the response"""
    response: ChatCompletion = ask_openai(user_question)

    # Pretty print the entire response
    response = response.choices[0].message.content
    print(f"response : {response}")
