import base64
import json
import os

import requests
from dotenv import load_dotenv

load_dotenv()

LLM = os.environ.get("OPEN_AI_MODEL")
api_key = os.environ.get("OPENAI_API_KEY")

image_path = "src/resources/invoice-template.png"

# Call the openai chat.completions endpoint
def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
) -> requests.Response:
    print(f"LLM : {LLM}")

    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": user_question},
                    {
                        "type": "image_url",
                    },
                ],
            }
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # Step 4 :
    user_question = """Hello, Extract the info from this invoice image in json format.
    Do not include ```json in the response.
    """

    response = ask_openai(user_question)
