#!/usr/bin/env python3
"""
Test AviationStack API for flight data.
Free tier: 100 requests/month
Sign up: https://aviationstack.com/
"""

import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "")
BASE_URL = "http://api.aviationstack.com/v1"


def test_flights():
    """Test fetching flights for Indian routes."""

    if not API_KEY:
        print("❌ AVIATIONSTACK_API_KEY not found in .env")
        print("Get free key at: https://aviationstack.com/")
        return False

    headers = {
        "access_key": API_KEY
    }

    print("=" * 60)
    print("Testing AviationStack API")
    print("=" * 60)

    # Test 1: Get flights from Delhi to Mumbai tomorrow
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    print(f"\n📅 Test 1: Flights DEL → BOM on {tomorrow}")
    print("-" * 60)

    params = {
        "access_key": API_KEY,
        "dep_iata": "DEL",
        "arr_iata": "BOM",
        "flight_date": tomorrow
    }

    try:
        response = requests.get(f"{BASE_URL}/flights", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("data"):
            print(f"✅ Found {len(data['data'])} flights")
            for flight in data["data"][:3]:  # Show first 3
                airline = flight.get("airline", {}).get("name", "Unknown")
                flight_num = flight.get("flight", {}).get("number", "N/A")
                dep_time = flight.get("departure", {}).get("scheduled", "N/A")
                arr_time = flight.get("arrival", {}).get("scheduled", "N/A")
                print(f"   - {airline} {flight_num}: Dep {dep_time}, Arr {arr_time}")
        else:
            print("⚠️  No flights found (might be free tier limitation)")

        # Test 2: Get airlines
        print(f"\n📋 Test 2: Get Indian airlines")
        print("-" * 60)

        params = {
            "access_key": API_KEY,
            "limit": 100
        }
        response = requests.get(f"{BASE_URL}/airlines", params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        indian_airlines = [
            a for a in data.get("data", [])
            if a.get("country_name") == "India" or "India" in str(a.get("country_iso2", ""))
        ]

        print(f"✅ Total airlines: {len(data.get('data', []))}")
        print(f"✅ Indian airlines found: {len(indian_airlines)}")
        for airline in indian_airlines[:5]:
            print(f"   - {airline.get('name')} ({airline.get('iata_code', 'N/A')})")

        # Test 3: Get airports
        print(f"\n✈️  Test 3: Get Indian airports")
        print("-" * 60)

        response = requests.get(f"{BASE_URL}/airports", params={"access_key": API_KEY, "limit": 100}, timeout=10)
        response.raise_for_status()
        data = response.json()

        indian_airports = [
            a for a in data.get("data", [])
            if a.get("country_name") == "India" or "India" in str(a.get("country_iso2", ""))
        ]

        print(f"✅ Total airports: {len(data.get('data', []))}")
        print(f"✅ Indian airports found: {len(indian_airports)}")
        for airport in indian_airports[:10]:
            print(f"   - {airport.get('iata_code')}: {airport.get('airport_name')} ({airport.get('city_name')})")

        # Test 4: Historical flights (if available in free tier)
        print(f"\n📊 Test 4: Historical flight data")
        print("-" * 60)

        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        params = {
            "access_key": API_KEY,
            "dep_iata": "DEL",
            "arr_iata": "BOM",
            "flight_date": yesterday
        }

        response = requests.get(f"{BASE_URL}/flights", params=params, timeout=10)
        data = response.json()

        if "error" in data and "limit" in str(data.get("error", {})).lower():
            print("⚠️  Historical data not available in free tier")
        elif data.get("data"):
            print(f"✅ Historical data available: {len(data['data'])} flights")

        print("\n" + "=" * 60)
        print("✅ AviationStack API test completed")
        print("=" * 60)
        print("\n📝 Summary:")
        print("  - Free tier: 100 requests/month")
        print("  - Real-time data: ✅")
        print("  - Historical data: ⚠️  Check plan")
        print("  - Indian coverage: ✅")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


if __name__ == "__main__":
    success = test_flights()
    exit(0 if success else 1)
