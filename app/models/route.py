"""Route models for trains, flights, and buses."""

from datetime import time
from sqlalchemy import String, Integer, Float, ForeignKey, Time, JSON
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

    # Classes available
    classes: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "1A,2A,3A,SL"

    def __repr__(self) -> str:
        return f"<TrainRoute {self.train_no} {self.train_name} {self.from_station_code}->{self.to_station_code}>"


class FlightRoute(Base):
    """Represent a flight route between two airports."""

    __tablename__ = "flight_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    flight_no: Mapped[str] = mapped_column(String(10), index=True)  # e.g., "6E234"
    airline: Mapped[str] = mapped_column(String(50))  # e.g., "IndiGo"
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

    # Reliability
    on_time_percentage: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Aircraft type
    aircraft_type: Mapped[str | None] = mapped_column(String(50), nullable=True)

    def __repr__(self) -> str:
        return f"<FlightRoute {self.flight_no} {self.from_airport_code}->{self.to_airport_code}>"


class BusRoute(Base):
    """Represent a bus route between two cities."""

    __tablename__ = "bus_routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    operator: Mapped[str] = mapped_column(String(100))  # e.g., "KSRTC", "Private"
    from_city: Mapped[str] = mapped_column(String(100), index=True)
    to_city: Mapped[str] = mapped_column(String(100), index=True)
    departure_time: Mapped[time] = mapped_column(Time)
    arrival_time: Mapped[time] = mapped_column(Time)
    duration_minutes: Mapped[int] = mapped_column(Integer)
    bus_type: Mapped[str] = mapped_column(String(50))  # e.g., "Sleeper", "Semi-Sleeper", "Seater"

    # Pricing
    price_min: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_avg: Mapped[int | None] = mapped_column(Integer, nullable=True)
    price_max: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Reliability (operator rating)
    rating: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<BusRoute {self.operator} {self.from_city}->{self.to_city}>"
