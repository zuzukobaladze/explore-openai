import base64
import json
import os

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")
api_key = os.environ.get("OPENAI_API_KEY")


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


image_path = "src/resources/invoice-template.png"

base64_image = encode_image(image_path)


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
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
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

    response_json = response.content

    response_dict = json.loads(response_json)

    content = response_dict["choices"][0]["message"]["content"]
    print("content " + content)
    clean_content_dict = json.loads(content)
    clean_content_json = json.dumps(clean_content_dict, indent=4)
    print(clean_content_json)
