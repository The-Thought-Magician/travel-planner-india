"""API request/response schemas."""

from datetime import date, time
from typing import Literal
from pydantic import BaseModel, Field, field_validator


class SearchRequest(BaseModel):
    """Search request for multi-modal journey planning."""

    from_location: str = Field(..., description="Origin city name", examples=["Ranchi"])
    to_location: str = Field(..., description="Destination city name", examples=["Hampi"])
    travel_date: date = Field(..., description="Travel date (YYYY-MM-DD)")
    preference: Literal["cheapest", "fastest", "most_reliable", "balanced"] = Field(
        default="balanced", description="Optimization preference"
    )
    max_transfers: int = Field(default=3, ge=1, le=5, description="Maximum number of transfers")
    passengers: int = Field(default=1, ge=1, le=10, description="Number of passengers")


class JourneyLeg(BaseModel):
    """Single leg of a journey."""

    mode: Literal["flight", "train", "bus", "auto", "cab", "walk"]
    from_name: str
    to_name: str
    from_code: str | None = None  # Station/airport code
    to_code: str | None = None
    cost: int
    duration_minutes: int
    departure_time: time | None = None
    arrival_time: time | None = None
    flight_train_bus_no: str | None = None  # Flight/train/bus number
    reliability_score: float | None = None  # 0-1
    notes: str | None = None


class JourneyOption(BaseModel):
    """Complete journey option with multiple legs."""

    rank: int
    total_cost: int
    total_duration_minutes: int
    reliability_score: float  # Probability of completing journey on time
    legs: list[JourneyLeg]
    booking_links: dict[str, str] | None = None
    warnings: list[str] | None = None


class SearchResponse(BaseModel):
    """Search response with journey options."""

    from_location: str
    to_location: str
    travel_date: date
    options: list[JourneyOption]
    metadata: dict | None = None


class CityResponse(BaseModel):
    """City response."""

    id: int
    name: str
    state: str
    code: str | None
    latitude: float | None
    longitude: float | None


class StationResponse(BaseModel):
    """Station response."""

    id: int
    code: str
    name: str
    state: str | None
    zone: str | None


class AirportResponse(BaseModel):
    """Airport response."""

    id: int
    iata_code: str
    name: str
    city: str
    state: str
    is_international: bool
