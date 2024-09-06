import requests
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = "gpt-4o"


# Call the openai chat.completions endpoint
def ask_openai(user_question: str, size="1024x1024") -> ChatCompletion:
    print(f"LLM : {LLM}")

    response = client.images.generate(
        model="dall-e-3",
        prompt=user_question,
        size=size,
        quality="standard",
        n=1,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # Step 4 :
    user_question = "A dog and cat sitting together"
    size = "1024x1024"
    response: ChatCompletion = ask_openai(user_question, size=size)

    # Pretty print the entire response
    image_url = response.data[0].url
    print("Generated Image URL:", image_url)

    image_data = requests.get(image_url).content
    with open("generated_image.png", "wb") as f:
        f.write(image_data)

    print("Image successfully downloaded and saved as 'generated_image.png'")
