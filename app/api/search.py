"""Search endpoint for multi-modal journey planning."""

from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Query

from app.api.schemas import SearchRequest, SearchResponse, JourneyOption, JourneyLeg
from app.services.journey_planner import JourneyPlanner
from app.models import City
from app.database import get_db

router = APIRouter()


@router.get("/search")
def search_journeys(
    from_location: str = Query(..., alias="from", description="Origin city name"),
    to_location: str = Query(..., alias="to", description="Destination city name"),
    travel_date: str = Query(None, description="Travel date (YYYY-MM-DD), defaults to today"),
    preference: str = Query("balanced", description="cheapest, fastest, most_reliable, or balanced"),
    max_transfers: int = Query(3, ge=0, le=5, description="Maximum transfers"),
    max_journeys: int = Query(10, ge=1, le=20, description="Maximum journeys to return"),
):
    """
    Search for multi-modal journey options.

    Finds optimal combinations of flights, trains, buses, and last-mile transport
    to get from origin to destination.
    """
    # Default to today if no date provided
    if travel_date is None:
        travel_date_obj = date.today()
    else:
        try:
            travel_date_obj = date.fromisoformat(travel_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    # Validate preference
    valid_preferences = {"cheapest", "fastest", "most_reliable", "balanced"}
    if preference not in valid_preferences:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid preference. Must be one of: {', '.join(valid_preferences)}",
        )

    planner = JourneyPlanner()

    try:
        journeys, metadata = planner.find_journeys(
            from_city=from_location,
            to_city=to_location,
            travel_date=travel_date_obj,
            preference=preference,
            max_transfers=max_transfers,
            max_journeys=max_journeys,
        )

        # Get location objects for response
        db = next(get_db())
        from_city_obj = db.query(City).filter(City.name.ilike(from_location)).first()
        to_city_obj = db.query(City).filter(City.name.ilike(to_location)).first()

        # Build location objects
        def build_location(city, query_name):
            if city:
                return {
                    "id": str(city.id),
                    "name": city.name,
                    "type": "city",
                    "code": city.code or city.name[:3].upper(),
                    "state": city.state,
                    "latitude": city.latitude,
                    "longitude": city.longitude,
                }
            return {
                "id": query_name.lower().replace(" ", "-"),
                "name": query_name,
                "type": "city",
                "code": query_name[:3].upper(),
            }

        from_loc = build_location(from_city_obj, from_location)
        to_loc = build_location(to_city_obj, to_location)

        # Update metadata with location objects
        metadata["from_location"] = from_loc
        metadata["to_location"] = to_loc
        metadata["query"] = {
            "from": from_location,
            "to": to_location,
            "preference": preference,
            "max_transfers": max_transfers,
            "max_journeys": max_journeys,
        }

        return {
            "journeys": journeys,
            "metadata": metadata,
        }
    except ValueError as e:
        metadata = {
            "from_location": {"name": from_location},
            "to_location": {"name": to_location},
            "query": {
                "from": from_location,
                "to": to_location,
                "preference": preference,
            },
            "error": str(e),
        }
        return {
            "journeys": [],
            "metadata": metadata,
        }


@router.get("/locations")
def search_locations(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50, description="Maximum results"),
):
    """
    Search for locations (cities, stations, airports) by name.
    Used for autocomplete in the frontend.
    """
    db = next(get_db())

    # Search cities
    cities = db.query(City).filter(City.name.ilike(f"%{q}%")).limit(limit).all()

    locations = []
    for city in cities:
        locations.append({
            "id": f"city-{city.id}",
            "name": city.name,
            "type": "city",
            "code": city.code or city.name[:3].upper(),
            "state": city.state,
            "latitude": city.latitude,
            "longitude": city.longitude,
        })

    return {
        "locations": locations,
        "count": len(locations),
    }


@router.get("/journeys/{journey_id}")
def get_journey_details(journey_id: str):
    """
    Get journey details by ID.

    Note: This is a placeholder. Currently journey details are
    transient and generated on-demand. In a full implementation,
    you would save journeys to a database for retrieval.
    """
    # For now, return a not found response
    # The frontend stores journey data in sessionStorage
    raise HTTPException(
        status_code=404,
        detail="Journey details not found on server. Please use the browser back button."
    )


@router.get("/search/health")
async def search_health() -> dict:
    """Health check for search service."""
    return {"status": "healthy", "service": "search"}
