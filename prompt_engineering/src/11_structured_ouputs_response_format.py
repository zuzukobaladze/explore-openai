import os

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion

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
# Max'x age is 30 years


def ask_openai(
    prompt: str,
):
    # response = client.chat.completions.create(
    response = client.beta.chat.completions.parse(
        # model="gpt-4o-2024-08-06",
        messages=[
            # {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response


def extract_flight_info_system_message():
    text = """
    Emily Thompson booked a flight on October 10, 2024. She will be flying from New York (JFK) to Los Angeles (LAX) on flight number AA123.
    The departure time is 8:00 AM, and the arrival time is 11:30 AM. She has a carry-on bag and a checked bag.
    Her ticket price was 450.00$, and she will be seated in 14A.
    """

    few_shot_example = ""
    with open("resources/flight-info-fewshot.json", "r") as file:
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
    # Person Extraction
    prompt = "Max's age is 30 years"
    # person_extrction(prompt)

    # With System Message
    response: ChatCompletion = extract_flight_info_system_message()
    # json_data = response.choices[0].message.content
