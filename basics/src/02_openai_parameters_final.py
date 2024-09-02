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
    max_tokens: int = 256,
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
    # temperature
    # 0.2 -> Deterministic
    # 1 and above  -> non deterministic
    # 2. top_p example
    user_question = """
        Can you complete the sentence ?

        My dog is playful and love to
        """
    # response: ChatCompletion = ask_openai(user_question, temperature=2.0)
    # print(f"response_temp_01 : {response.choices[0].message.content}")

    # top_p
    # Start with 1, -> run around in the park, chasing after balls and playing with other dogs.
    #  0.5-> My dog is playful and loves to chase after balls in the park.
    #  0.2-> My dog is playful and loves to chase after balls in the park.
    response: ChatCompletion = ask_openai(user_question, top_p=0.2)
    print(f"response_temp_01 : {response.choices[0].message.content}")

    # user_question = "Why is python is recommended for AI development ?."
    # response_temp_0: ChatCompletion = ask_openai(user_question, temperature=0.0)
    # print("\n*** Temperature 00 ***\n")
    # print(f"response_0 : {response_temp_0.choices[0].message.content}")

    # response_temp_01: ChatCompletion = ask_openai(user_question, temperature=1.0)
    # print("\n***Temperature 01 ***\n")
    # print(f"response_temp_01 : {response_temp_01.choices[0].message.content}")

    # response_temp_02: ChatCompletion = ask_openai(user_question, temperature=2.0)
    # print("\n***Temperature 02 ***\n")
    # print(f"response_temp_02 : {response_temp_02.choices[0].message.content}")
