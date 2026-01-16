"""Railway station model."""

from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Station(Base):
    """Represent a railway station in India."""

    __tablename__ = "stations"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(10), unique=True, index=True)  # e.g., "HPT"
    name: Mapped[str] = mapped_column(String(200))
    state: Mapped[str | None] = mapped_column(String(50), nullable=True)
    zone: Mapped[str | None] = mapped_column(String(10), nullable=True)  # e.g., "SWR"
    latitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    longitude: Mapped[float | None] = mapped_column(Float, nullable=True)
    elevation: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Nearest city (for last-mile routing)
    nearest_city_id: Mapped[int | None] = mapped_column(ForeignKey("cities.id"), nullable=True)
    distance_to_city_km: Mapped[float | None] = mapped_column(Float, nullable=True)

    def __repr__(self) -> str:
        return f"<Station {self.code} - {self.name}>"
