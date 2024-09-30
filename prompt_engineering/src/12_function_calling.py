import json
import os
from datetime import datetime, timezone

import requests
import yfinance as yf
from dotenv import load_dotenv
from model.Weather import OpenMeteoInput
from openai import OpenAI
from openai.types.chat.chat_completion import ChatCompletion, ChatCompletionMessage

load_dotenv()

client = OpenAI()
LLM = os.environ.get("OPEN_AI_MODEL")
system_message = """
You are a helpful assistant!
"""


def get_current_weather(openMeteoInput: OpenMeteoInput):
    """Fetch current temperature for given coordinates."""

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    # Parameters for the request
    params = {
        "latitude": openMeteoInput.latitude,
        "longitude": openMeteoInput.longitude,
        "hourly": "temperature_2m",
        "forecast_days": 1,
    }

    # Make the request
    response = requests.get(BASE_URL, params=params)

    if response.status_code == 200:
        results = response.json()
    else:
        raise Exception(f"API Request failed with status code: {response.status_code}")
    print(f"results : {results}")

    current_utc_time = datetime.now(timezone.utc)

    time_list = [
        datetime.fromisoformat(time_str.replace("Z", "+00:00")).replace(
            tzinfo=timezone.utc
        )
        for time_str in results["hourly"]["time"]
    ]
    print(f"time_list : {time_list}")
    temperature_list = results["hourly"]["temperature_2m"]

    closest_time_index = min(
        range(len(time_list)), key=lambda i: abs(time_list[i] - current_utc_time)
    )
    current_temperature = temperature_list[closest_time_index]

    return f"The current temperature is {current_temperature}°C"


def get_current_time() -> str:
    print("Getting current time")
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_current_stock_value(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    todays_data = ticker.history(period="1d")
    print(todays_data.to_string(index=False))
    return f"The stock price of {ticker_symbol} is,  {todays_data['Close'].iloc[0]}"


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


# Send the result back to the model


# def send_tool_call_response(LLM, user_input, message, tool_name, result, tool_call_id):
#     response = client.chat.completions.create(
#         model=LLM,
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": user_input},
#             message,  # The model's tool call
#             {
#                 "role": "tool",
#                 "name": tool_name,
#                 "content": result,
#                 "tool_call_id": tool_call_id,  # Include the tool_call_id
#             },
#         ],
#     )
#     return response


def app():
    while True:
        user_input = input("You: ")
        if user_input == "exit":
            break
        response = ask_openai(user_input)
        message: ChatCompletionMessage = response.choices[0].message
        print(f"response : {message.tool_calls}")
        if message.tool_calls and len(message.tool_calls) != 0:
            print(f"response : {message.tool_calls[0].function}")
            function = message.tool_calls[0].function
            tool_name = message.tool_calls[0].function.name
            tool_name = function.name
            if tool_name == "get_current_weather":
                # Extract tool name and arguments
                arguments = json.loads(
                    function.arguments
                )  # Parse JSON string to dictionary
                print(f" get_current_weather arguments : {arguments}")
                # Execute the tool
                latitude = arguments.get("latitude")
                longitude = arguments.get("longitude")
                open_meteo_input = OpenMeteoInput(
                    latitude=latitude, longitude=longitude
                )
                result = get_current_weather(open_meteo_input)
                tool_call_id = message.tool_calls[0].id  # Get the tool_call_id
                # Send the result back to the model
                second_response = send_tool_call_response(
                    LLM, user_input, message, tool_name, result, tool_call_id
                )
                # Print the model's final response
                final_message = second_response.choices[0].message.content
                print(f"Final Assistant: {final_message}")
            if tool_name == "get_current_stock_value":
                # Extract tool name and arguments
                arguments = json.loads(
                    function.arguments
                )  # Parse JSON string to dictionary
                print(f"get_current_stock_value arguments : {arguments}")
                # Execute the tool
                symbol = arguments.get("ticker_symbol")
                result = get_current_stock_value(symbol)
                tool_call_id = message.tool_calls[0].id  # Get the tool_call_id
                # Send the result back to the model
                second_response = send_tool_call_response(
                    LLM, user_input, message, tool_name, result, tool_call_id
                )
                # Print the model's final response
                final_message = second_response.choices[0].message.content
                print(f"Final Assistant: {final_message}")
            elif tool_name == "get_current_time":
                result = get_current_time()
                tool_call_id = message.tool_calls[0].id  # Get the tool_call_id
                second_response = send_tool_call_response(
                    LLM, user_input, message, tool_name, result, tool_call_id
                )
                # Print the model's final response
                final_message = second_response.choices[0].message.content
                print(f"Assistant: {final_message}")
        else:
            # If no function call, just print the assistant's message
            print(f"Assistant: {message.content}")


if __name__ == "__main__":
    # Initial prompts
    prompt = "Whats the current time?"
    # prompt = "Whats the current weather in new york?"
    # prompt = "Whats the current stock value of Tesla?"


    response: ChatCompletion = ask_openai(prompt)
    print(f"response  : {response.choices[0].message.content}")

    # Complete App
    # app()
