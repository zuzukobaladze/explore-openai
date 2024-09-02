import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


# Call the openai chat.completions endpoint
def ask_openai(
    user_question: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": user_question},
        ],
    )

    print(f"response  type : {type(response)}")
    return response


if __name__ == "__main__":
    # temperature
    # 0.2 -> Deterministic
    # 1 and above  -> non deterministic
    user_question = """
        Can you complete the sentence ?

        My dog is playful and love to
        """

    # top_p
    # Start with 1, -> run around in the park, chasing after balls and playing with other dogs.
    #  0.5-> My dog is playful and loves to chase after balls in the park.
    #  0.2-> My dog is playful and loves to chase after balls in the park.
    response: ChatCompletion = ask_openai(user_question, top_p=0.2)
    print(f"response_temp_01 : {response.choices[0].message.content}")
