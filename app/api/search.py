"""Search endpoint for multi-modal journey planning."""

from datetime import date, time
from fastapi import APIRouter, HTTPException, Query

from app.api.schemas import SearchRequest, SearchResponse, JourneyOption, JourneyLeg
from app.services.journey_planner import JourneyPlanner

router = APIRouter()


@router.get("/search")
def search_journeys(
    from_location: str = Query(..., description="Origin city name"),
    to_location: str = Query(..., description="Destination city name"),
    travel_date: str = Query(..., description="Travel date (YYYY-MM-DD)"),
    preference: str = Query("balanced", description="cheapest, fastest, most_reliable, or balanced"),
    max_transfers: int = Query(3, ge=1, le=5, description="Maximum transfers"),
):
    """
    Search for multi-modal journey options.

    Finds optimal combinations of flights, trains, buses, and last-mile transport
    to get from origin to destination.
    """
    # Parse date
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
            max_journeys=5,
        )

        return {
            "from_location": from_location,
            "to_location": to_location,
            "travel_date": travel_date,
            "journeys": journeys,
            "metadata": metadata,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/search/health")
async def search_health() -> dict:
    """Health check for search service."""
    return {"status": "healthy", "service": "search"}
