from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = "gpt-4o"
image_url = "https://www.invoicesimple.com/wp-content/uploads/2018/06/Sample-Invoice-printable.png"


# Call the openai chat.completions endpoint
def ask_openai(user_question: str) -> ChatCompletion:
    print(f"LLM : {LLM}")
    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # Step 4 :
    user_question = "Hello"

    response: ChatCompletion = ask_openai(user_question)
