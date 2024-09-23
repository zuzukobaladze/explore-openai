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
"""


def ask_openai(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            # {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
    )
    return response


def extract_order_details():
    text = """
    "John Doe placed an order on September 20, 2024, for 2 items: 
    A pair of Wireless Headphones costing $99.99 and a Laptop Stand priced at $29.99. 
    The order was shipped to 123 Elm Street, Springfield, IL, and was expected to be delivered by September 25, 2024."
    """

    prompt = f"""
    Extract the key information from the following text delimited by triple backticks and format it in JSON.
    I need details like name, order date, product names, quantities, prices, shipping address, and delivery date.

    Text: ```{text}```
   

    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    return response


def extract_flight_info():
    text = """
    Emily Thompson booked a flight on October 10, 2024. She will be flying from New York (JFK) to Los Angeles (LAX) on flight number AA123. 
    The departure time is 8:00 AM, and the arrival time is 11:30 AM. She has a carry-on bag and a checked bag. 
    Her ticket price was $450.00, and she will be seated in 14A.
    """

    prompt = f"""
    Extract the key information from the following text delimited by triple backticks and format it in JSON.
    I need details like name, booking date, flight information (flight number, origin, destination, departure/arrival times), 
    luggage details, ticket price, and seat number.

    Text: ```{text}```
   

    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    return response


def article_summary():
    text = """
    Tesla announced its third-quarter earnings report on October 19, 2024. 
    The electric vehicle company reported a revenue of $23.3 billion, slightly below analysts' expectations of $24 billion. 
    Despite the revenue miss, Tesla's net income increased by 12% compared to the previous quarter, reaching $2.8 billion.
    CEO Elon Musk attributed the growth to strong vehicle sales, particularly in Europe and China. 
    Tesla also announced plans to expand its Gigafactory in Berlin and accelerate the production of the Cybertruck.
    However, Musk warned that rising material costs could impact future profitability.
    """

    prompt = f"""
    Extract the key information from the following text delimited by triple backticks and and provide a summary in JSON format.
    Include details such as the company name, earnings report date, revenue, net income, reasons for growth, future plans, and any warnings.

    Text: ```{text}```
   

    """
    response = ask_openai(prompt=prompt)
    # Print the Type and Response
    return response


if __name__ == "__main__":
    # Retail - Retrieve Order Detail
    response: ChatCompletion = extract_order_details()
    print(f"response  : {response.choices[0].message.content}")

    # Travel - Retrieve Flight Info
    # response: ChatCompletion = extract_flight_info()
    # print(f"response  : {response.choices[0].message.content}")

    # Finance - Article Summary
    # response: ChatCompletion = article_summary()
    # print(f"response  : {response.choices[0].message.content}")
