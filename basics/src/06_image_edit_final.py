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
    
    # The "rb" stands for read binary mode. Here's what it means:
    #     "r" (read mode): This opens the file for reading. The file must exist for this mode, and its contents cannot be modified.
    #     "b" (binary mode): This tells Python to open the file in binary mode, meaning the file is read as raw binary data, rather than as a text file.
    
    response = client.images.edit(
        model="dall-e-2",
        image=open(
            "../explore-open-ai/generated_image.png",
            "rb",
        ),
        mask=open(
            "../explore-open-ai/mask.png",
            "rb",
        ),
        prompt=user_question,
        size=size,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # Step 4 :
    user_question = """Dog and a cat in the forest background.
        """
    response: ChatCompletion = ask_openai(user_question)

    # Pretty print the entire response
    image_url = response.data[0].url
    print("Generated Image URL:", image_url)

    image_data = requests.get(image_url).content
    file_name = "generated_imag_edited.png"
    with open(file_name, "wb") as f:
        f.write(image_data)

    print(f"Image successfully downloaded and saved as {file_name}")
