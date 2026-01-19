"""Route models for trains, flights, and buses."""

from datetime import time, datetime
from sqlalchemy import String, Integer, Float, ForeignKey, Time, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TrainRoute(Base):
    """Represent a train route between two stations."""

    __tablename__ = "train_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_no: Mapped[int] = mapped_column(Integer, index=True)
    train_name: Mapped[str] = mapped_column(String(200))
    from_station_code: Mapped[str] = mapped_column(String(10), ForeignKey("stations.code"), index=True)
    to_station_code: Mapped[str] = mapped_column(String(10), ForeignKey("stations.code"), index=True)
    departure_time: Mapped[time] = mapped_column(Time)
    arrival_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    distance_km: Mapped[int | None] = mapped_column(Integer, nullable=True)
    days_run: Mapped[str] = mapped_column(String(20))  # e.g., "Daily", "Mon,Wed,Fri"

    # Pricing (sleeper, 3A, 2A, 1A) - stored as JSON
    pricing: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Reliability (historical on-time percentage)
    on_time_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_delay_minutes: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Classes available
    classes: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "1A,2A,3A,SL"

    # Data harvesting metadata
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "data.gov.in", "railradar"
    last_harvested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)  # For soft deletes

    def __repr__(self) -> str:
        return f"<TrainRoute {self.train_no} {self.train_name} {self.from_station_code}->{self.to_station_code}>"


class FlightRoute(Base):
    """Represent a flight route between two airports."""

    __tablename__ = "flight_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_no: Mapped[str] = mapped_column(String(10), index=True)  # e.g., "6E234"
    airline: Mapped[str] = mapped_column(String(50))  # e.g., "IndiGo"
    airline_code: Mapped[str | None] = mapped_column(String(5), nullable=True)  # e.g., "6E"
    from_airport_code: Mapped[str] = mapped_column(String(5), ForeignKey("airports.iata_code"), index=True)
    to_airport_code: Mapped[str] = mapped_column(String(5), ForeignKey("airports.iata_code"), index=True)
    departure_time: Mapped[time] = mapped_column(Time)
    arrival_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    days_run: Mapped[str] = mapped_column(String(20))  # e.g., "Daily"

    # Pricing
    price_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_trends: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # 30-day trends

    # Reliability
    on_time_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Aircraft type
    aircraft_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Data harvesting metadata
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "ixigo", "aviationstack"
    last_harvested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<FlightRoute {self.flight_no} {self.from_airport_code}->{self.to_airport_code}>"


class BusRoute(Base):
    """Represent a bus route between two cities."""

    __tablename__ = "bus_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    operator_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # RedBus operator ID
    operator: Mapped[str] = mapped_column(String(100))  # e.g., "KSRTC", "Private"
    from_city_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)  # RedBus city ID
    from_city: Mapped[str] = mapped_column(String(100), index=True)
    to_city_id: Mapped[str | None] = mapped_column(String(20), nullable=True, index=True)
    to_city: Mapped[str] = mapped_column(String(100), index=True)
    departure_time: Mapped[time] = mapped_column(Time)
    arrival_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    bus_type: Mapped[str] = mapped_column(String(50))  # e.g., "Sleeper", "Semi-Sleeper", "Seater"

    # Pricing
    price_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_max: Mapped[int | None] = mapped_column(Integer, nullable=True)
    fare_tiers: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # Different seat types

    # Reliability (operator rating)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_ratings: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Amenities
    amenities: Mapped[list | None] = mapped_column(JSON, nullable=True)

    # Data harvesting metadata
    source: Mapped[str | None] = mapped_column(String(50), nullable=True)  # "redbus", "abhibus"
    last_harvested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)

    def __repr__(self) -> str:
        return f"<BusRoute {self.operator} {self.from_city}->{self.to_city}>"


class TrainLiveStatus(Base):
    """Store live train status for delay tracking."""

    __tablename__ = "train_live_status"

    id: Mapped[int] = mapped_column(primary_key=True)
    train_no: Mapped[int] = mapped_column(Integer, index=True)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    scheduled_departure: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_departure: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    scheduled_arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    actual_arrival: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delay_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    current_station_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    status: Mapped[str] = mapped_column(String(50))  # "on_time", "delayed", "arrived"

    # Source of this data
    source: Mapped[str] = mapped_column(String(50))  # "railradar"

    def __repr__(self) -> str:
        return f"<TrainLiveStatus {self.train_no} {self.recorded_at.strftime('%Y-%m-%d %H:%M')} delay:{self.delay_minutes}>"
