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

    system_message = """
    You are a helpful assistant who will help me with python programming related questions! If there are any other irrelevant questions are asked then you can respond with I don't know in a funny way!
    """

    # response = client.chat.completions.create(
    #     model=LLM,
    #     # Conversation as a list of messages.
    #     messages=[
    #         {"role": "system", "content": system_message},
    #         {
    #             "role": "user",
    #             "content": "Are there other measures than time complexity for an \
    #             algorithm?",
    #         },
    #         {
    #             "role": "system",
    #             "content": "Yes, there are other measures besides time complexity \
    #             for an algorithm, such as space complexity.",
    #         },
    #         {"role": "user", "content": "What is it?"},
    #     ],
    # )

    # print(f"response : {response.choices[0].message.content}")
