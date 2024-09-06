import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = "gpt-4o"


# Call the openai chat.completions endpoint
def ask_openai(size="1024x1024") -> ChatCompletion:
    print(f"LLM : {LLM}")

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    response: ChatCompletion = ask_openai()

    # Pretty print the entire response
    image_url = response.data[0].url
    print("Generated Image URL:", image_url)

    image_data = requests.get(image_url).content
    file_name = "image_variation.png"
    with open(file_name, "wb") as f:
        f.write(image_data)

    print(f"Image successfully downloaded and saved as {file_name}")
