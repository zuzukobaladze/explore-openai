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
        model="gpt-4o",
        messages=[
            {"role": "user", "content": prompt},
        ],
    )
    return response



def classify_prompt():
    text = """
       "I am not able to login into the account. Please help me."
    """
    prompt = f"""
         Categorize the following customer support query within the triple ticks into one of the categories: Billing Issue, Technical Support, Account Management, or General Inquiry:

        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")


def classify_using_few_shot_prompting():
    text = """
       Example 1:
        Query: "I can’t log into my account, and I’ve tried resetting my password multiple times."
        Category: Account Management

        Example 2:
        Query: "My internet connection keeps dropping, and I can’t access any websites. Can you check my connection?"
        Category: Technical Support

        Example 3:
        Query: "I noticed an extra charge on my credit card for a service I didn’t sign up for."
        Category: Billing Issue

        Now, categorize the following customer support query:
        "I am not able to login into the account. Please help me."

    """
    prompt = f"""
         Categorize the following customer support query within the triple ticks into one of the categories: Billing Issue, Technical Support, Account Management, or General Inquiry:

        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")



if __name__ == "__main__":
    classify_prompt()
    # classify_using_few_shot_prompting()
