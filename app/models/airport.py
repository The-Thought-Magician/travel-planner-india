"""Airport model."""

from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Airport(Base):
    """Represent an airport in India."""

    __tablename__ = "airports"

    id: Mapped[int] = mapped_column(primary_key=True)
    iata_code: Mapped[str] = mapped_column(String(5), unique=True, index=True)  # e.g., "IXR"
    icao_code: Mapped[str | None] = mapped_column(String(5), nullable=True)  # e.g., "VERC"
    name: Mapped[str] = mapped_column(String(200))
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(50))
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    elevation_ft: Mapped[int | None] = mapped_column(Integer, nullable=True)
    type: Mapped[str] = mapped_column(String(20))  # large, medium, small
    is_international: Mapped[bool] = mapped_column(default=False)

    # Nearest city (for last-mile routing)
    nearest_city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"), nullable=True)
    distance_to_city_km: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Airport {self.iata_code} - {self.name}>"
