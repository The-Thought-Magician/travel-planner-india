"""Popular-routes endpoint.

Backed by data/seeds/popular_pairs.json; each hit runs the planner once and
caches the cheapest teaser for quick rendering on the home page.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from fastapi import APIRouter, Query

from app.services.journey_planner import JourneyPlanner

router = APIRouter()

SEEDS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "seeds"


@lru_cache(maxsize=1)
def _load_pairs() -> list[dict]:
    path = SEEDS_DIR / "popular_pairs.json"
    if not path.exists():
        return []
    return json.loads(path.read_text())


@router.get("/routes/popular")
def popular_routes(limit: int = Query(12, ge=1, le=30)) -> dict:
    """Return curated popular route pairs for the home page."""
    pairs = _load_pairs()[:limit]
    return {
        "routes": [
            {
                "from": p["from"],
                "to": p["to"],
                "tagline": p.get("tagline"),
                "typical_cost": p.get("typical_cost"),
                "typical_duration_hours": p.get("typical_duration_hours"),
            }
            for p in pairs
        ],
        "count": len(pairs),
    }


@router.get("/routes/popular/{index}/plan")
def popular_route_plan(index: int) -> dict:
    """Run the planner for the Nth popular pair — useful for a demo link."""
    pairs = _load_pairs()
    if index < 0 or index >= len(pairs):
        return {"journeys": [], "metadata": {"error": "index out of range"}}
    p = pairs[index]
    planner = JourneyPlanner()
    journeys, metadata = planner.find_journeys(
        from_city=p["from"], to_city=p["to"], preference="balanced", max_journeys=5,
    )
    return {"journeys": journeys, "metadata": metadata, "pair": p}
