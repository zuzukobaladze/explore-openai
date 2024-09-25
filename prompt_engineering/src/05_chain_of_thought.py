import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")


def ask_openai(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response


def simple_puzzle():
    prompt = """
        If each student in a classroom has 3 pencils and there are 15 students in total,
        how many pencils are there in the classroom?
            """
    response = ask_openai(prompt=prompt)
    print(f"response  : {response.choices[0].message.content}")


def simple_puzzle_cot():
    prompt = """
        If each student in a classroom has 3 pencils and there are 15 students in total,
        how many pencils are there in the classroom?

        Can you explain the reasoning step by step and before arriving to the result?
        """
    response = ask_openai(prompt=prompt)
    print(f"response  : {response.choices[0].message.content}")


def simple_puzzle1():
    prompt = """
        "If Alex is taller than Bob, and Bob is taller than Charlie, who is the shortest?"
            """
    response = ask_openai(prompt=prompt)
    print(f"response  : {response.choices[0].message.content}")


def simple_puzzle1_cot():
    prompt = """
        "If Alex is taller than Bob, and Bob is taller than Charlie, who is the shortest?"

        Can you explain the reasoning step by step and before arriving to the result?
        """
    response = ask_openai(prompt=prompt)
    print(f"response  : {response.choices[0].message.content}")


def simple_math():
    # 455,715
    prompt = """
        "How much is 369 * 1235?"
            """
    response = ask_openai(prompt=prompt)
    print(f"response  : {response.choices[0].message.content}")


def simple_math_cot():
    # 455,715
    # "How much is 369 * 1235 ?"

    prompt = """
        "How much is 369 * 1235 ?"
        Let's think step by step.
            """
    response = ask_openai(prompt=prompt)
    print(f"response  : {response.choices[0].message.content}")


if __name__ == "__main__":
    # COT Example 1
    simple_puzzle()
    # simple_puzzle_cot()

    # COT Example 2
    # simple_puzzle1()
    # simple_puzzle1_cot()

    # Math Example
    # simple_math()
    # simple_math_cot()
