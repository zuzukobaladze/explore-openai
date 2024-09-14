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

    response = client.images.create_variation(
        model="dall-e-2",
        image=open(
            "src/resources/generated_image.png",
            "rb",
        ),
        n=1,
        size=size,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    response: ImagesResponse = ask_openai()

    # Pretty print the entire response
    image_url = response.data[0].url
    print("Generated Image URL:", image_url)

    image_data = requests.get(image_url).content
    file_name = "src/resources/image_variation-result.png"
    with open(file_name, "wb") as f:
        f.write(image_data)

    print(f"Image successfully downloaded and saved as {file_name}")
