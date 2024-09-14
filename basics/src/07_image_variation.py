import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.images_response import ImagesResponse
import os
load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")

# Call the openai chat.completions endpoint
def ask_openai(size="1024x1024") -> ImagesResponse:
    print(f"LLM : {LLM}")

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    response: ImagesResponse = ask_openai()

    # Pretty print the entire response
    image_url = response.data[0].url
    print("Generated Image URL:", image_url)

    image_data = requests.get(image_url).content
    file_name = "image_variation.png"
    with open(file_name, "wb") as f:
        f.write(image_data)

    print(f"Image successfully downloaded and saved as {file_name}")
