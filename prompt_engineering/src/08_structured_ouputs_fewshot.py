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


def extract_flight_info_few_shot():
    text = """
    Emily Thompson booked a flight on October 10, 2024. She will be flying from New York (JFK) to Los Angeles (LAX) on flight number AA123.
    The departure time is 8:00 AM, and the arrival time is 11:30 AM. She has a carry-on bag and a checked bag.
    Her ticket price was 450.00$, and she will be seated in 14A.
    """
    # text = """
    # Emily Thompson booked a flight on October 10, 2024. She will be flying from New York (JFK) to Los Angeles (LAX) on flight number AA123.
    # The departure time is 8:00 AM, and the arrival time is 11:30 AM. She has a carry-on bag and a checked bag.
    # Her ticket price was 450.00€, and she will be seated in 14A.
    # """

    # text = """
    # Li Wei booked a flight on November 5, 2024. He will be flying from Beijing (PEK) to Shanghai (PVG) on flight number CA456.
    # The departure time is 10:00 AM, and the arrival time is 12:30 PM. He has a carry-on bag and one checked bag.
    # His ticket price was ¥3,200.00, and he will be seated in 22C.
    # """

    few_shot_example = ""
    with open("resources/flight-info-fewshot.json", "r") as file:
        few_shot_example = file.read()

    prompt = f"""
    Extract the key information from the following text delimited by triple backticks and format it in JSON.
    I need details like name, booking date, flight information (flight number, origin, destination, departure/arrival times), 
    luggage details, ticket price, and seat number.

    Here is an example output of the JSON format:\n
    {few_shot_example}

    \n

    Text: ```{text}```
   
    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    return response


if __name__ == "__main__":
    response: ChatCompletion = extract_flight_info_few_shot()
    print(f"response  : {response.choices[0].message.content}")
