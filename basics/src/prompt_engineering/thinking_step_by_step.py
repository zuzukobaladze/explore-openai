import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


def ask_openai(
    user_question: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: int = 500,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "user", "content": user_question},
        ],
        temperature=temperature,
        max_tokens=max_tokens,
        top_p=top_p,
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    user_question = """
    How much is  3999*1234564?
    """
    #\[ 3999 \times 1234564 = 4938061236. \]
    
    user_question = """
    How much is  3999*1234564?
        Let's think step by step.
        """
    # Correct-> 4,937,021,436    
    

  
    response: ChatCompletion = ask_openai(user_question)
    print(f"response_temp_01 : {response.choices[0].message.content}")


