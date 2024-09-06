import base64
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from openai.resources.audio.transcriptions import Transcription
load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")

# Call the openai chat.completions endpoint
def ask_openai(
    audio_path: str,
    prompt : str = ""
) -> Transcription:
    
    print(f"LLM : {LLM}")
    #The "rb" stands for read binary mode. Here's what it means:
    #  "r" (read mode): This opens the file for reading. The file must exist for this mode, and its contents cannot be modified.
    #  "b" (binary mode): This tells Python to open the file in binary mode, meaning the file is read as raw binary data, rather than as a text file.
    

    audio_file= open(audio_path, "rb")

    transcription = client.audio.transcriptions.create(
    model="whisper-1", 
    prompt = prompt,
    file=audio_file
    )
    print(f"Response Type : {type(transcription)}")

    return transcription


if __name__ == "__main__":
    
    # audio_path = "src/resources/Taylor_Swift_Delicate.mp3"
    audio_path = "src/resources/RAG.mp3"
        # YT_Link -> https://www.youtube.com/watch?v=T-D1OfcDW1M&t=20s
    audio_path = "src/resources/generated_audio_english.mp3"
    prompt = "This audio explains the concepts about RAG"
    response: Transcription = ask_openai(audio_path=audio_path)

    # Pretty print the entire response
    transciption_text = response.text
    print(f"transciption_text : {transciption_text}")
