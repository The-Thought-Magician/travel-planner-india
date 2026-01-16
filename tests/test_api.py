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
    response = client.get("/api/v1/search?from=Ranchi&to=Hampi&travel_date=invalid")
    assert response.status_code == 400


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
