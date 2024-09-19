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


def zero_shot_prompting():
    text = """
        The weather is beautiful today.
    """
    prompt = f"""
        Translate the following sentence within triple backticks into French.\
        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")


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


def classify_prompt_1():
    text = """

        "We are seeking a software engineer to join our team. The ideal candidate will have experience with Python, JavaScript, and cloud technologies. Responsibilities include designing scalable systems, collaborating with cross-functional teams, and improving code quality. Candidates should have a bachelor’s degree in computer science or related field, and at least 3 years of professional experience."

    """
    prompt = f"""
        Extract the qualifications and responsibilities from the following job description within the triple ticks:

        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")


def classify_using_few_shot_prompting_1():
    text = """
    Example 1:
    Email: "Dear Mr. Smith, I am writing to request a meeting regarding the upcoming project. Please let me know your availability at your earliest convenience."
    Tone: Formal

    Example 2:
    Email: "Hey John, just wanted to check if you're free to grab lunch this week. Let me know!"
    Tone: Informal

    Example 3:
    Email: "Good morning, I hope all is well. I wanted to remind you about the upcoming deadline. Let me know if you need assistance."
    Tone: Formal

    Now, classify the tone of the following email:
    "Hi, I hope this message finds you well. I just wanted to follow up on the report you submitted last week. Could you please clarify a few points when you have time? Thanks a lot!"

    """
    prompt = f"""
        Classify the tone of the following emails within the triple ticks as formal or informal:

        ```{text}```
    """
    response = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")


if __name__ == "__main__":
    zero_shot_prompting()
    # classify_prompt()
    # classify_using_few_shot_prompting()
    classify_prompt_1()
    # classify_using_few_shot_prompting_1()
