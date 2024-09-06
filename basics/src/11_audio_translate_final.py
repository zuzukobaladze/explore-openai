import base64
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.resources.audio.translations import Translation
load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")

# Call the openai chat.completions endpoint
def ask_openai(
    audio_path: str,
    prompt : str = ""
) -> Translation:
    
    print(f"LLM : {LLM}")
    #The "rb" stands for read binary mode. Here's what it means:
    #  "r" (read mode): This opens the file for reading. The file must exist for this mode, and its contents cannot be modified.
    #  "b" (binary mode): This tells Python to open the file in binary mode, meaning the file is read as raw binary data, rather than as a text file.
    

    audio_file= open(audio_path, "rb")

    translation = client.audio.translations.create(
    model="whisper-1", 
    prompt = prompt,
    file=audio_file
    )
    print(f"Response Type : {type(translation)}")

    return translation


if __name__ == "__main__":
    
    audio_path = "src/resources/french_audio.mp3"
    response: Translation = ask_openai(audio_path=audio_path)

    # Pretty print the entire response
    translation_text = response.text
    print(f"translation : {translation_text}")
