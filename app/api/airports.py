"""Airports endpoint."""

from fastapi import APIRouter, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Airport

router = APIRouter()


@router.get("/airports")
async def list_airports(
    limit: int = Query(100, ge=1, le=500),
    search: str | None = Query(None, description="Search by name or code"),
    is_international: bool | None = Query(None, description="Filter by international status"),
) -> dict:
    """List airports in India."""
    db: Session = next(get_db())

    query = db.query(Airport)

    if search:
        query = query.filter(
            (Airport.name.ilike(f"%{search}%"))
            | (Airport.iata_code.ilike(f"%{search}%"))
            | (Airport.city.ilike(f"%{search}%"))
        )

    if is_international is not None:
        query = query.filter(Airport.is_international == is_international)

    airports = query.limit(limit).all()

    return {
        "count": len(airports),
        "airports": [
            {
                "id": a.id,
                "iata_code": a.iata_code,
                "icao_code": a.icao_code,
                "name": a.name,
                "city": a.city,
                "state": a.state,
                "is_international": a.is_international,
            }
            for a in airports
        ],
    }


@router.get("/airports/{iata_code}")
async def get_airport(iata_code: str) -> dict:
    """Get airport details."""
    db: Session = next(get_db())
    airport = db.query(Airport).filter(Airport.iata_code == iata_code.upper()).first()

    if not airport:
        return {"error": "Airport not found"}

    return {
        "id": airport.id,
        "iata_code": airport.iata_code,
        "icao_code": airport.icao_code,
        "name": airport.name,
        "city": airport.city,
        "state": airport.state,
        "latitude": airport.latitude,
        "longitude": airport.longitude,
        "type": airport.type,
        "is_international": airport.is_international,
    }
