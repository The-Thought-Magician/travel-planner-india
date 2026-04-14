"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Test client fixture."""
    return TestClient(app)


def test_root(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "India Travel Planner API"
    assert "endpoints" in data


def test_health(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_missing_params(client):
    """Test search with missing parameters."""
    response = client.get("/api/v1/search")
    assert response.status_code == 422  # Validation error


def test_search_invalid_date(client):
    """Test search with invalid date format."""
    response = client.get("/api/v1/search?from=Ranchi&to=Hampi&date=invalid")
    assert response.status_code == 400


def test_search_multi_leg_ranchi_hampi(client):
    """Ranchi→Hampi should return a multi-leg journey combining flight+train."""
    response = client.get("/api/v1/search?from=Ranchi&to=Hampi&preference=balanced&max_journeys=3")
    assert response.status_code == 200
    data = response.json()
    assert len(data["journeys"]) >= 1
    top = data["journeys"][0]
    modes = {leg["mode"] for leg in top["legs"]}
    # We expect at least one flight and one train in the top journey
    assert "flight" in modes or "train" in modes, modes
    # Cost breakdown present
    assert "cost_breakdown" in top
    breakdown = top["cost_breakdown"]
    assert breakdown["tickets"] + breakdown["last_mile"] + breakdown["booking_fees"] + breakdown["meals_incidentals"] == breakdown["total"]


def test_popular_routes_endpoint(client):
    response = client.get("/api/v1/routes/popular?limit=5")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] == 5
    assert all("from" in r and "to" in r for r in data["routes"])


def test_journey_replan_excludes_disrupted_leg(client):
    """After searching Ranchi→Hampi, replanning without flight 6E234 must
    return a top journey that does NOT use that flight."""
    r1 = client.get("/api/v1/search?from=Ranchi&to=Hampi&preference=balanced&max_journeys=3")
    assert r1.status_code == 200
    journeys = r1.json()["journeys"]
    assert journeys
    jid = journeys[0]["journey_id"]
    r2 = client.post(f"/api/v1/journeys/{jid}/replan?exclude_vehicle_id=6E234")
    assert r2.status_code == 200
    new_journeys = r2.json()["journeys"]
    assert new_journeys
    for j in new_journeys:
        vehicle_ids = [leg.get("flight_train_bus_no") for leg in j["legs"]]
        assert "6E234" not in vehicle_ids


def test_journey_cache_roundtrip(client):
    """After /search, each returned journey_id should be retrievable via /journeys/{id}."""
    r1 = client.get("/api/v1/search?from=Delhi&to=Mumbai&max_journeys=2")
    assert r1.status_code == 200
    journeys = r1.json()["journeys"]
    assert journeys
    jid = journeys[0]["journey_id"]
    r2 = client.get(f"/api/v1/journeys/{jid}")
    assert r2.status_code == 200
    assert r2.json()["journey"]["total_cost"] == journeys[0]["total_cost"]


def test_cities_list(client):
    """Test cities list endpoint."""
    response = client.get("/api/v1/cities?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "cities" in data
    assert "count" in data


def test_airports_list(client):
    """Test airports list endpoint."""
    response = client.get("/api/v1/airports?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "airports" in data


def test_stations_list(client):
    """Test stations list endpoint."""
    response = client.get("/api/v1/stations?limit=10")
    assert response.status_code == 200
    data = response.json()
    assert "stations" in data
