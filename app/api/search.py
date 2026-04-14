"""Search and journey-lookup endpoints."""

from __future__ import annotations

import time as _time
from collections import OrderedDict
from datetime import date, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.api.schemas import SearchRequest  # noqa: F401  (kept for backward-compat)
from app.database import get_db
from app.models import City
from app.services.journey_planner import JourneyPlanner

router = APIRouter()


# ---------------------------------------------------------------------- #
# Journey cache
# ---------------------------------------------------------------------- #
# Journeys are transient: we don't persist them, but the UI wants to deep-link
# to a specific result and reload it. A simple TTL-LRU in the process serves
# the MVP. Key: journey_id returned in /search.

_JOURNEY_TTL_SECONDS = 30 * 60
_JOURNEY_CACHE_MAX = 1024
_journey_cache: "OrderedDict[str, tuple[float, dict[str, Any]]]" = OrderedDict()


def _cache_put(journey_id: str, payload: dict[str, Any]) -> None:
    now = _time.time()
    _journey_cache[journey_id] = (now, payload)
    _journey_cache.move_to_end(journey_id)
    while len(_journey_cache) > _JOURNEY_CACHE_MAX:
        _journey_cache.popitem(last=False)


def _cache_get(journey_id: str) -> dict[str, Any] | None:
    entry = _journey_cache.get(journey_id)
    if not entry:
        return None
    ts, payload = entry
    if _time.time() - ts > _JOURNEY_TTL_SECONDS:
        _journey_cache.pop(journey_id, None)
        return None
    _journey_cache.move_to_end(journey_id)
    return payload


# ---------------------------------------------------------------------- #
# Search
# ---------------------------------------------------------------------- #

@router.get("/search")
def search_journeys(
    from_location: str = Query(..., alias="from", description="Origin city name"),
    to_location: str = Query(..., alias="to", description="Destination city name"),
    travel_date: str | None = Query(None, alias="date", description="Travel date YYYY-MM-DD"),
    preference: str = Query("balanced", description="cheapest | fastest | reliable | balanced"),
    max_transfers: int = Query(3, ge=0, le=5),
    max_journeys: int = Query(10, ge=1, le=20),
):
    """Multi-leg journey search."""
    if travel_date is None:
        travel_date_obj = date.today()
    else:
        try:
            travel_date_obj = date.fromisoformat(travel_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")

    valid_preferences = {"cheapest", "fastest", "most_reliable", "reliable", "balanced"}
    if preference not in valid_preferences:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid preference. Must be one of: {', '.join(sorted(valid_preferences))}",
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
    except ValueError as e:
        return {
            "journeys": [],
            "metadata": {
                "error": str(e),
                "query": {"from": from_location, "to": to_location, "preference": preference},
            },
        }

    # Build rich from/to location objects
    db = next(get_db())
    from_city_obj = db.query(City).filter(City.name.ilike(from_location)).first()
    to_city_obj = db.query(City).filter(City.name.ilike(to_location)).first()

    def _city_payload(city: City | None, fallback_name: str) -> dict:
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
            "id": fallback_name.lower().replace(" ", "-"),
            "name": fallback_name,
            "type": "city",
            "code": fallback_name[:3].upper(),
        }

    metadata["from_location"] = _city_payload(from_city_obj, from_location)
    metadata["to_location"] = _city_payload(to_city_obj, to_location)
    metadata["query"] = {
        "from": from_location,
        "to": to_location,
        "date": travel_date_obj.isoformat(),
        "preference": preference,
        "max_transfers": max_transfers,
        "max_journeys": max_journeys,
    }

    # Cache each journey by id so clients can deep-link to /journeys/{id}
    for j in journeys:
        jid = j.get("journey_id")
        if jid:
            _cache_put(jid, {"journey": j, "metadata": metadata})

    return {"journeys": journeys, "metadata": metadata}


# ---------------------------------------------------------------------- #
# Locations autocomplete
# ---------------------------------------------------------------------- #

@router.get("/locations")
def search_locations(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(10, ge=1, le=50),
):
    db = next(get_db())
    cities = db.query(City).filter(City.name.ilike(f"%{q}%")).limit(limit).all()
    locations = [
        {
            "id": f"city-{city.id}",
            "name": city.name,
            "type": "city",
            "code": city.code or city.name[:3].upper(),
            "state": city.state,
            "latitude": city.latitude,
            "longitude": city.longitude,
        }
        for city in cities
    ]
    return {"locations": locations, "count": len(locations)}


# ---------------------------------------------------------------------- #
# Journey lookup by ID (cached)
# ---------------------------------------------------------------------- #

@router.get("/journeys/{journey_id}")
def get_journey(journey_id: str):
    payload = _cache_get(journey_id)
    if not payload:
        raise HTTPException(
            status_code=404,
            detail="Journey not found or expired. Please run a new search.",
        )
    return payload


@router.get("/journeys/{journey_id}/alternatives")
def journey_alternatives(journey_id: str, window: int = Query(7, ge=3, le=14)):
    """Return daily cheapest totals for dates ±window/2 around the original."""
    payload = _cache_get(journey_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Journey not found or expired.")
    meta = payload.get("metadata", {})
    q = meta.get("query", {})
    original_total = payload["journey"].get("total_cost")
    try:
        base_date = date.fromisoformat(q.get("date"))
    except Exception:
        base_date = date.today()

    half = window // 2
    planner = JourneyPlanner()
    results: list[dict[str, Any]] = []
    for offset in range(-half, half + 1):
        d = base_date + timedelta(days=offset)
        try:
            journeys, _ = planner.find_journeys(
                from_city=q.get("from"),
                to_city=q.get("to"),
                travel_date=d,
                preference="cheapest",
                max_journeys=1,
            )
            if journeys:
                cheapest = journeys[0]["total_cost"]
                results.append({
                    "date": d.isoformat(),
                    "cheapest_total": cheapest,
                    "delta_vs_selected": cheapest - (original_total or cheapest),
                    "is_selected": offset == 0,
                })
        except Exception:
            continue
    return {"alternatives": results, "base_date": base_date.isoformat(), "original_total": original_total}


@router.post("/journeys/{journey_id}/replan")
def replan_journey(
    journey_id: str,
    exclude_vehicle_id: str = Query(..., description="vehicle_id to avoid (e.g. flight/train/bus number)"),
):
    """Re-plan the same origin/destination excluding a disrupted leg.

    The UI wires this to a "If this train is delayed, re-plan" action on each
    transport leg — the new journeys are returned and cached under fresh ids.
    """
    payload = _cache_get(journey_id)
    if not payload:
        raise HTTPException(status_code=404, detail="Journey not found or expired.")
    q = payload.get("metadata", {}).get("query", {})
    if not q.get("from") or not q.get("to"):
        raise HTTPException(status_code=400, detail="Original search metadata missing.")

    try:
        base_date = date.fromisoformat(q.get("date")) if q.get("date") else date.today()
    except Exception:
        base_date = date.today()

    planner = JourneyPlanner()
    journeys, metadata = planner.find_journeys(
        from_city=q["from"],
        to_city=q["to"],
        travel_date=base_date,
        preference=q.get("preference", "balanced"),
        max_journeys=5,
        excluded_vehicle_ids={exclude_vehicle_id},
    )
    metadata["replanned_excluding"] = exclude_vehicle_id
    metadata["original_journey_id"] = journey_id
    for j in journeys:
        jid = j.get("journey_id")
        if jid:
            _cache_put(jid, {"journey": j, "metadata": metadata})
    return {"journeys": journeys, "metadata": metadata}


@router.get("/search/health")
async def search_health() -> dict:
    return {
        "status": "healthy",
        "service": "search",
        "cache_size": len(_journey_cache),
    }
