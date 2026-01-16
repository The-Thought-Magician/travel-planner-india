"""Cities endpoint."""

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import City

router = APIRouter()


@router.get("/cities")
async def list_cities(
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None, description="Search by name"),
    state: str | None = Query(None, description="Filter by state"),
    top_cities_only: bool = Query(False, description="Show only top 50 cities"),
) -> dict:
    """List cities."""
    db: Session = next(get_db())

    query = db.query(City)

    if search:
        query = query.filter(City.name.ilike(f"%{search}%"))

    if state:
        query = query.filter(City.state == state)

    if top_cities_only:
        query = query.filter(City.is_top_city == True)

    cities = query.order_by(City.name).limit(limit).all()

    return {
        "count": len(cities),
        "cities": [
            {
                "id": c.id,
                "name": c.name,
                "state": c.state,
                "code": c.code,
                "latitude": c.latitude,
                "longitude": c.longitude,
            }
            for c in cities
        ],
    }


@router.get("/cities/{city_id}")
async def get_city(city_id: int) -> dict:
    """Get city details."""
    db: Session = next(get_db())
    city = db.query(City).filter(City.id == city_id).first()

    if not city:
        return {"error": "City not found"}

    return {
        "id": city.id,
        "name": city.name,
        "state": city.state,
        "code": city.code,
        "latitude": city.latitude,
        "longitude": city.longitude,
        "is_top_city": city.is_top_city,
        "last_mile_estimates": {
            "auto": {"base": city.auto_base_fare, "per_km": city.auto_per_km},
            "cab": {"base": city.cab_base_fare, "per_km": city.cab_per_km},
        },
    }
