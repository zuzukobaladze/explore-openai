import json
import os

from dotenv import load_dotenv
from model.flight_model import Booking
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion
from pydantic import ValidationError

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")
system_message = """
You are an AI assistant specialized in extracting detailed flight booking information from given text and formatting it into a structured JSON object. 

Your tasks include:

1. **Extraction Requirements:**
   - **Name:** Full name of the passenger.
   - **Booking Date:** Date when the flight was booked.
   - **Flight Information:**
     - **Flight Number**
     - **Origin Airport Code**
     - **Origin City**
     - **Destination Airport Code**
     - **Destination City**
     - **Departure Time**
     - **Arrival Time**
   - **Luggage Details:**
     - **Carry-On Bags**
     - **Checked Bags**
   - **Ticket Price:**
     - **Value**
     - **Currency**
        - Currencies should be mentioned only in text:
        Examples are:
        $ should be represented as DOLLAR
        € should be represented as EURO
   - **Seat Number**

2. **Formatting Instructions:**
   - The extracted information must be formatted in **JSON**.
   - Ensure that all fields are present and correctly named as specified above.
   - Follow the structure demonstrated in the provided few-shot examples to maintain consistency.

3. **Operational Guidelines:**
   - **Accuracy:** Ensure that all extracted data accurately reflects the information in the input text.
   - **Consistency:** Maintain consistent formatting, especially for dates, times, and numerical values.
   - **Validation:** Validate data types where applicable (e.g., dates should follow the "YYYY-MM-DD" format, prices should be numerical with appropriate currency symbols).

4. **Examples:**
   - Refer to the few-shot examples provided to understand the expected JSON structure and formatting nuances.

Please do not include json and ``` in the generated JSON.   
"""


def ask_openai(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response


def process_flight_info(json_data) -> Booking:
    # Load JSON data
    data = json.loads(json_data)

    # Parse and validate using the Booking model
    try:
        booking = Booking(**data)
        print("Validation Successful!")
        print(booking.model_dump_json(indent=4, exclude_unset=True))
        return booking
    except ValidationError as e:
        print("Validation Error:")
        print(e.json(indent=4))


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

    text = """
    Li Wei booked a flight on November 5, 2024. He will be flying from Beijing (PEK) to Shanghai (PVG) on flight number CA456.
    The departure time is 10:00 AM, and the arrival time is 12:30 PM. He has a carry-on bag and one checked bag.
    His ticket price was ¥3,200.00, and he will be seated in 22C.
    """

    additional_info = ""
    # additional_info = """
    # Currencies should be mentioned only in text:
    # Examples are:
    # $ should be represented as DOLLAR
    # € should be represented as EURO
    # """

    few_shot_example = ""
    with open("prompt_engineering/resources/flight-info-fewshot.json", "r") as file:
        few_shot_example = file.read()

    prompt = f"""
    Extract the key information from the following text delimited by triple backticks and format it in JSON.
    I need details like name, booking date, flight information (flight number, origin, destination, departure/arrival times), 
    luggage details, ticket price, and seat number.

    Please do not include json and ``` in the generated JSON.

    Here is an example output of the JSON format:\n
    {few_shot_example}

    \n
    {additional_info}

    Text: ```{text}```
   

    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    return response


def extract_flight_info_system_message():
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
    with open("prompt_engineering/resources/flight-info-fewshot.json", "r") as file:
        few_shot_example = file.read()

    prompt = f"""
    Here is an example output of the JSON format:\n
    {few_shot_example}

    Text: ```{text}```

    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    return response


if __name__ == "__main__":
    # Without System Message
    response: ChatCompletion = extract_flight_info_few_shot()
    json_data = response.choices[0].message.content
    print(f"json_data  : {json_data}")

    # With System Message
    # response: ChatCompletion = extract_flight_info_system_message()
    # json_data = response.choices[0].message.content
    # print(f"json_data  : {json_data}")

    # Call the function with the json_data
    booking = process_flight_info(json_data)
    print(f"booking : {booking}")
