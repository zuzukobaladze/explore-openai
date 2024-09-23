from datetime import date, datetime, time
from enum import Enum

from pydantic import BaseModel, field_validator, model_validator


class CurrencyEnum(str, Enum):
    DOLLAR = "DOLLAR"
    EURO = "EURO"
    YUAN = "YUAN"
    CNY = "CNY"
    YEN = "YEN"
    # Add other currencies as needed


class FlightInfo(BaseModel):
    flight_number: str
    origin_airport_code: str
    origin_city: str
    destination_airport_code: str
    destination_city: str
    departure_time: time
    arrival_time: time

    @field_validator("departure_time", "arrival_time", mode="before")
    @classmethod
    def parse_time(cls, value: str) -> time:
        try:
            return datetime.strptime(value, "%I:%M %p").time()
        except ValueError:
            raise ValueError(
                f"Time '{value}' is not in the correct format 'H:MM AM/PM'."
            )


class Luggage(BaseModel):
    carry_on: int
    checked_bag: int

    @field_validator("carry_on", "checked_bag", mode="before")
    @classmethod
    def convert_to_int(cls, value: str) -> int:
        try:
            return int(value)
        except ValueError:
            raise ValueError(f"Invalid luggage count: {value}")


class TicketPrice(BaseModel):
    value: float
    currency: CurrencyEnum

    @field_validator("value", mode="before")
    @classmethod
    def convert_to_float(cls, value: str) -> float:
        try:
            return float(value)
        except ValueError:
            raise ValueError(f"Invalid ticket price value: {value}")


class Booking(BaseModel):
    name: str
    booking_date: date
    flight_info: FlightInfo
    luggage: Luggage
    ticket_price: TicketPrice
    seat_number: str

    @field_validator("booking_date", mode="before")
    @classmethod
    def parse_booking_date(cls, value: str) -> date:
        try:
            return datetime.strptime(value, "%B %d, %Y").date()
        except ValueError:
            raise ValueError(
                f"Booking date '{value}' is not in the correct format 'Month DD, YYYY'."
            )

    @model_validator(mode="after")
    def check_seat_number(cls, model):
        # Example validation: Seat number must follow pattern like '14A'
        if not (model.seat_number[:-1].isdigit() and model.seat_number[-1].isalpha()):
            raise ValueError(
                f"Seat number '{model.seat_number}' is not in the correct format 'NumberLetter'."
            )
        return model

    class Config:
        # Allow extra fields if necessary; set to 'forbid' to reject unexpected fields
        extra = "forbid"
