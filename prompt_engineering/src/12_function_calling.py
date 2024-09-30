import json
import os
from datetime import datetime, timezone

import requests
import yfinance as yf
from dotenv import load_dotenv
from model.weather_model import OpenMeteoInput
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

system_message = """You are an intelligent assistant capable of performing a wide variety of tasks using predefined functions. 
These functions include retrieving real-time data such as weather information, stock prices, and time and more.
Always choose the appropriate function based on the user’s query. Ensure that responses are clear, accurate, and only invoke functions when required. 
If the task cannot be completed using the available functions, politely inform the user.
"""

system_message = """You are a helpful assistant!"""


def ask_openai(
    custom_messages: list,
) -> ChatCompletion:
    messages = [{"role": "system", "content": system_message}]
    messages.extend(custom_messages)
    print(f"messages : {messages}")
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
    )
    return response


if __name__ == "__main__":
    # Initial promptsç
    prompt = "Whats the current time?"
    # prompt = "Whats the current weather in new york?"
    # prompt = "Whats the current stock value of Tesla?"

    user_message = [{"role": "user", "content": prompt}]
    response: ChatCompletion = ask_openai(user_message)
    print(f"response  : {response.choices[0].message.content}")

    # Complete App
    # app()
