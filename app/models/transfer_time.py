"""Transfer-time model: buffer between hubs within the same city."""

from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TransferTime(Base):
    """Typical and p90 transfer minutes between two hubs (airport/station) in a city.

    Used by the routing layer to compute feasible connection buffers:
    - typical_minutes: median observed transit time
    - p90_minutes: 90th-percentile time (what we expect in bad traffic)
    - buffer_minutes: recommended planning buffer (p90 + safety)
    """

    __tablename__ = "transfer_times"

    id: Mapped[int] = mapped_column(primary_key=True)
    city_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("cities.id"), nullable=True, index=True)

    # Hub pair — hub_type is "airport" | "station" | "bus_stand"
    from_hub_type: Mapped[str] = mapped_column(String(20))
    from_hub_code: Mapped[str] = mapped_column(String(10), index=True)
    to_hub_type: Mapped[str] = mapped_column(String(20))
    to_hub_code: Mapped[str] = mapped_column(String(10), index=True)

    typical_minutes: Mapped[int] = mapped_column(Integer)
    p90_minutes: Mapped[int] = mapped_column(Integer)
    buffer_minutes: Mapped[int] = mapped_column(Integer)

    notes: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        return (
            f"<TransferTime {self.from_hub_type}:{self.from_hub_code}→"
            f"{self.to_hub_type}:{self.to_hub_code} typ={self.typical_minutes} buf={self.buffer_minutes}>"
        )
