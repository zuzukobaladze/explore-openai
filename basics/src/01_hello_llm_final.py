import json
import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")

# Call open-ai model using chat completion create.
response = client.chat.completions.create(
    model=LLM,
    messages=[
        # {"role": "user", "content": "Hi LLM ?"}
        {"role": "user", "content": "What is an LLM ?"}
        # {"role": "user", "content": "Generate the code for the sum of n numbers"}
    ],
)


# Print the Type and Response
print(f"response type : {type(response)}")
# print(f"response : {response}")

# Pretty print the entire response
response_dict = response.to_dict()
print(json.dumps(response_dict, indent=4))


print(f"response_content : {response.choices[0].message.content}")


def ask_openai(
    user_question: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user", "content": user_question},
        ],
    )
    return response


if __name__ == "__main__":
    user_question = "What is an LLM ?"
    response = ask_openai(user_question)
    # Print the Type and Response
    print(f"response type : {type(response)}")
    # print(f"response : {response}")

    # Pretty print the entire response
    response_dict = response.to_dict()
    print(json.dumps(response_dict, indent=4))
