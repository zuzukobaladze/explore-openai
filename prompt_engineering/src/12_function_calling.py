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
You are a helpful assistant!
"""


def get_current_weather(city: str, unit: str = "celsius"):
    """
    Get the current weather in a given city.
    Args:
        city (str): The city to get the weather for.
        unit (str): The unit of temperature. Can be "celsius" or "fahrenheit".
    Returns:
        str: A string describing the current weather.
    """
    # For demonstration, we'll return a mock response.
    # In a real application, you'd integrate with a weather API like OpenWeatherMap.
    weather_data = {
        "New York": {"temperature": 25, "unit": "celsius", "description": "Sunny"},
        "London": {"temperature": 18, "unit": "celsius", "description": "Cloudy"},
        "Tokyo": {"temperature": 30, "unit": "celsius", "description": "Rainy"},
    }

    data = weather_data.get(
        city, {"temperature": 20, "unit": "celsius", "description": "Partly cloudy"}
    )
    temperature = data["temperature"]
    description = data["description"]

    if unit == "fahrenheit":
        temperature = temperature * 9 / 5 + 32

    return f"The current temperature in {city} is {temperature}°{ 'F' if unit == 'fahrenheit' else 'C' } with {description}."


functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city to get the weather for.",
                },
                "unit": {
                    "type": "string",
                    "description": "The unit of temperature. Can be 'celsius' or 'fahrenheit'.",
                    "enum": ["celsius", "fahrenheit"],
                },
            },
            "required": ["city"],
        },
    }
]


def ask_openai(
    prompt: str,
) -> ChatCompletion:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": prompt},
        ],
        functions=functions,
        function_call="auto",
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


def main():
    while True:
        user_input = input("You: ")
        if user_input == "exit":
            break
        response = ask_openai(user_input)
        # Rest of the code...
        message = response.choices[0].message
        print(f"function_call: {message.function_call}")

        if message.function_call:
            # Extract function name and arguments
            function_name = message.function_call.name
            arguments = json.loads(message.function_call.arguments)

            # Execute the function
            if function_name == "get_current_weather":
                city = arguments.get("city")
                unit = arguments.get("unit", "celsius")
                result = get_current_weather(city, unit)

                # Send the result back to the model
                second_response = client.chat.completions.create(
                    model=LLM,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": user_input},
                        message,  # The model's function call
                        {"role": "function", "name": function_name, "content": result},
                    ],
                )
                # Print the model's final response
                final_message = second_response.choices[0].message.content
                print(f"Assistant: {final_message}")
        else:
            # If no function call, just print the assistant's message
            print(f"Assistant: {message.content}")


if __name__ == "__main__":
    response: ChatCompletion = ask_openai("Whats the current time in new york?")
    print(f"response  : {response.choices[0].message.content}")

    # main()
