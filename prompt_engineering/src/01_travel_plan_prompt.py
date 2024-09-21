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
    system_message = """
        You are a professional travel planner with extensive knowledge of worldwide destinations, 
        including cultural attractions, accommodations, and travel logistics.
        Provide better lodging options too that supports the family.
    """

    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response


def ask_openai_without_system_message(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model=LLM,
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response


def travel_prompt(input: str):
    prompt = f"""
        \n
        input : ```{input}```
        """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    print(f"response  : {response.choices[0].message.content}")


def travel_prompt_no_system_message(input: str):
    prompt = f"""
        \n
        input : ```{input}```
        """
    response = ask_openai_without_system_message(prompt=prompt)
    # Print the Type and Response
    print(f"response  : {response.choices[0].message.content}")


if __name__ == "__main__":
    print("\n With Task : \n")
    task = """
    "Create a 5-day itinerary that balances sightseeing, child-friendly activities, and authentic local dining. 
    Include recommendations for morning, afternoon, and evening activities each day."
    """
    travel_prompt_no_system_message(input=task)

    # print("\n With Context and Task : \n")
    # context_task = """
    
    # A family of three (two adults and a 4-year-old child) is planning a 5-day vacation to Paris, France. 
    # They want a mix of family-friendly activities, local cuisine experiences, and some relaxation time."

    # "Create a 5-day itinerary that balances sightseeing, child-friendly activities, and authentic local dining. 
    # Include recommendations for morning, afternoon, and evening activities each day."

    # """
    # travel_prompt_no_system_message(input=context_task)

    # print("\n With Role, Context and Task : \n")
    # travel_prompt(context_task)
