from pydantic import BaseModel, Field


class OpenMeteoInput(BaseModel):
    latitude: float = Field(
        ..., description="Latitude of the location to fetch weather data for"
    )
    longitude: float = Field(
        ..., description="Longitude of the location to fetch weather data for"
    )
