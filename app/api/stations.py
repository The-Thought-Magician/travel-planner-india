"""Stations endpoint."""

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Station

router = APIRouter()


@router.get("/stations")
async def list_stations(
    limit: int = Query(100, ge=1, le=1000),
    search: str | None = Query(None, description="Search by name or code"),
) -> dict:
    """List railway stations."""
    db: Session = next(get_db())

    query = db.query(Station)

    if search:
        query = query.filter(
            (Station.name.ilike(f"%{search}%")) | (Station.code.ilike(f"%{search}%"))
        )

    stations = query.limit(limit).all()

    return {
        "count": len(stations),
        "stations": [
            {
                "id": s.id,
                "code": s.code,
                "name": s.name,
                "state": s.state,
                "zone": s.zone,
            }
            for s in stations
        ],
    }


@router.get("/stations/{station_code}")
async def get_station(station_code: str) -> dict:
    """Get station details."""
    db: Session = next(get_db())
    station = db.query(Station).filter(Station.code == station_code.upper()).first()

    if not station:
        return {"error": "Station not found"}

    return {
        "id": station.id,
        "code": station.code,
        "name": station.name,
        "state": station.state,
        "zone": station.zone,
        "latitude": station.latitude,
        "longitude": station.longitude,
        "nearest_city_id": station.nearest_city_id,
    }
