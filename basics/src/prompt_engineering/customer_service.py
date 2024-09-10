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
    # user_question = """
    # Role: You are a customer service assistant for an online retail company that sells electronics and accessories.\n
    # Your goal is to provide prompt, helpful, and polite responses to customer inquiries and complaints.
    # \n\n
    # Context: The customer received a faulty wireless headphone that does not power on. \n
    # They purchased it a week ago and are requesting assistance with the return process. 
    # The customer is upset and needs to understand the steps for returning the item and receiving a replacement.

    # Task: Based on your expertise, craft a polite and empathetic response to the customer, providing them with clear steps to return the faulty item. In addition to the response, create a table with two columns where each row contains an action the customer should take during the return process. The first column should be the action, and the second column should provide a brief explanation of what the action entails.

    # """

    user_question = """

    Context: I do 2 hours of sport a day. I am vegetarian, and I don't like green
    vegetables. I am conscientious about eating healthily.\n
    Task: Give me a suggestion for a main course for today's lunch.
    """

  
    response: ChatCompletion = ask_openai(user_question)
    print(f"response_temp_01 : {response.choices[0].message.content}")


