"""City model."""

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class City(Base):
    """Represent a city in India."""

    __tablename__ = "cities"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(50))
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    code: Mapped[str | None] = mapped_column(String(10), nullable=True)  # e.g., "IXR" for Ranchi
    is_top_city: Mapped[bool] = mapped_column(default=False)  # MVP: top 50 cities

    # Last-mile estimates (in INR)
    auto_base_fare: Mapped[int] = mapped_column(default=25)  # Base flag fall
    auto_per_km: Mapped[int] = mapped_column(default=15)  # Per km rate
    cab_base_fare: Mapped[int] = mapped_column(default=50)
    cab_per_km: Mapped[int] = mapped_column(default=20)

    def __repr__(self) -> str:
        return f"<City {self.name}, {self.state}>"
