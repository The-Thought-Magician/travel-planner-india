#!/usr/bin/env python3
"""
Test train data sources for Indian Railways.

Sources to test:
1. data.gov.in - Static timetable download
2. Railway station coordinates data
3. NTES unofficial endpoints
"""

import requests
import json
import csv
from io import StringIO
import os
from dotenv import load_dotenv

load_dotenv()


# Government data URLs
TRAIN_TIMETABLE_URL = "https://data.gov.in/sites/default/files/all_india_trains_csv.csv"


def test_gov_data():
    """Test accessing government train timetable data."""

    print("=" * 60)
    print("Testing Government Train Data Sources")
    print("=" * 60)

    # Test 1: Download train timetable
    print(f"\n📋 Test 1: Download train timetable from data.gov.in")
    print("-" * 60)

    try:
        response = requests.get(TRAIN_TIMETABLE_URL, timeout=30)
        response.raise_for_status()

        # Parse CSV
        csv_data = response.text
        reader = csv.DictReader(StringIO(csv_data))

        trains = list(reader)
        print(f"✅ Successfully downloaded {len(trains)} train records")

        # Show sample records
        for train in trains[:5]:
            train_no = train.get("Train No", train.get("train_no", "N/A"))
            train_name = train.get("Train Name", train.get("train_name", "N/A"))
            source = train.get("Source Station", train.get("source", "N/A"))
            dest = train.get("Destination Station", train.get("destination", "N/A"))
            print(f"   - {train_no}: {train_name} ({source} → {dest})")

        return trains

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download timetable: {e}")
        print("   You may need to download manually from:")
        print(f"   {TRAIN_TIMETABLE_URL}")
        return None


def test_station_coordinates():
    """Test accessing station coordinates data."""

    print(f"\n📍 Test 2: Station coordinates data")
    print("-" * 60)

    # GitHub gist with Indian railway station coordinates
    github_url = "https://gist.githubusercontent.com/sankalpsharmaa/0c0587f3ae31277411960f70128d682f/raw/indian_railway_stations.csv"

    try:
        response = requests.get(github_url, timeout=30)
        response.raise_for_status()

        # Parse CSV
        csv_data = response.text
        reader = csv.DictReader(StringIO(csv_data))

        stations = list(reader)
        print(f"✅ Found {len(stations)} stations with coordinates")

        # Show sample
        for station in stations[:5]:
            name = station.get("station_name", station.get("name", "N/A"))
            code = station.get("station_code", station.get("code", "N/A"))
            lat = station.get("lat", station.get("latitude", "N/A"))
            lon = station.get("lon", station.get("longitude", "N/A"))
            print(f"   - {code}: {name} ({lat}, {lon})")

        return stations

    except requests.exceptions.RequestException as e:
        print(f"❌ Failed to download station data: {e}")
        return None


def test_railradar():
    """Test RailRadar API if available."""

    print(f"\n🚂 Test 3: RailRadar API (unofficial)")
    print("-" * 60)

    # RailRadar live train endpoint (unofficial)
    api_url = "https://railradar.in/api/trains"

    try:
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        data = response.json()

        print(f"✅ RailRadar API responded")
        print(f"   Data keys: {list(data.keys())[:10]}")

        return True

    except requests.exceptions.RequestException as e:
        print(f"⚠️  RailRadar API not accessible: {e}")
        print("   May require API key or partnership")
        return False


def test_ntes_unofficial():
    """Test unofficial NTES endpoints."""

    print(f"\n📊 Test 4: NTES unofficial endpoints")
    print("-" * 60)

    # Common NTES API endpoints (unofficial)
    endpoints = [
        ("https://ntesapi.darshitbh.com/api/v1/stationList", "Station list"),
        ("https://ntesapi.darshitbh.com/api/v1/trainsBetweenStations?from=NDLS&to=BOM", "Trains between stations"),
    ]

    working = []
    for url, description in endpoints:
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            data = response.json()
            print(f"✅ {description}: Working")
            working.append((url, description, data))
        except Exception as e:
            print(f"❌ {description}: Failed - {str(e)[:50]}")

    return working


def save_sample_data(trains=None, stations=None):
    """Save sample data for testing."""

    print(f"\n💾 Saving sample data...")
    print("-" * 60)

    os.makedirs("../data/seeds", exist_ok=True)

    if trains:
        with open("../data/seeds/sample_trains.json", "w") as f:
            json.dump(trains[:100], f, indent=2)
        print(f"✅ Saved {min(100, len(trains))} trains to data/seeds/sample_trains.json")

    if stations:
        with open("../data/seeds/sample_stations.json", "w") as f:
            json.dump(stations[:100], f, indent=2)
        print(f"✅ Saved {min(100, len(stations))} stations to data/seeds/sample_stations.json")


def main():
    """Run all train data tests."""

    trains = test_gov_data()
    stations = test_station_coordinates()
    test_railradar()
    ntes = test_ntes_unofficial()

    save_sample_data(trains, stations)

    print("\n" + "=" * 60)
    print("✅ Train data testing completed")
    print("=" * 60)

    print("\n📝 Summary:")
    print("  - Static timetable: ✅ Free from data.gov.in")
    print("  - Station coordinates: ✅ Available on GitHub")
    print("  - Live train status: ⚠️  Third-party APIs (may be unstable)")
    print("  - Historical delay data: ❌ No free source (need to collect)")


if __name__ == "__main__":
    main()
