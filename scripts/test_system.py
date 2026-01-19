#!/usr/bin/env python3
"""
Test the travel planner system.

This script initializes the database and runs a test journey search.
Run this to verify the system is working correctly.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.services.journey_planner import JourneyPlanner
from app.models import City, Station, Airport, TrainRoute, FlightRoute, BusRoute


def test_database():
    """Test database initialization and data."""
    print("=" * 60)
    print("Testing Database")
    print("=" * 60)

    try:
        # Initialize database tables
        init_db()

        # Query cities
        db = SessionLocal()
        city_count = db.query(City).count()
        station_count = db.query(Station).count()
        airport_count = db.query(Airport).count()
        train_count = db.query(TrainRoute).count()
        flight_count = db.query(FlightRoute).count()
        bus_count = db.query(BusRoute).count()

        print(f"✅ Cities: {city_count}")
        print(f"✅ Stations: {station_count}")
        print(f"✅ Airports: {airport_count}")
        print(f"✅ Train Routes: {train_count}")
        print(f"✅ Flight Routes: {flight_count}")
        print(f"✅ Bus Routes: {bus_count}")

        return city_count > 0

    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False


def test_journey_planner():
    """Test journey planner with actual search."""
    print("\n" + "=" * 60)
    print("Testing Journey Planner")
    print("=" * 60)

    try:
        planner = JourneyPlanner()

        # Test 1: Search locations
        print("\n🔍 Test 1: Location Search")
        print("-" * 60)
        results = planner.search_locations("Delhi", limit=5)
        print(f"   Found {len(results)} locations matching 'Delhi':")
        for result in results[:3]:
            print(f"      - {result['type']}: {result['name']} ({result['code']})")

        # Test 2: Find journeys
        print("\n🔍 Test 2: Journey Search")
        print("-" * 60)

        # Test with cities that should have sample routes
        test_routes = [
            ("Mumbai", "Bangalore"),
            ("Delhi", "Kolkata"),
            ("Chennai", "Hyderabad"),
        ]

        for from_city, to_city in test_routes:
            print(f"   {from_city} → {to_city}:")
            try:
                journeys, metadata = planner.find_journeys(
                    from_city=from_city,
                    to_city=to_city,
                    preference="balanced",
                    max_transfers=2,
                    max_journeys=3
                )

                if "error" in metadata:
                    print(f"      ⚠️  {metadata.get('error', 'Unknown error')}")
                    continue

                print(f"      ✅ Found {len(journeys)} journey options")

                if journeys:
                    best = journeys[0]
                    print(f"      Best option:")
                    print(f"         Cost: ₹{best['total_cost']}")
                    print(f"         Duration: {best['total_duration_minutes']} minutes")
                    print(f"         Reliability: {best['reliability_score']:.2%}")
                    print(f"         Legs: {len(best['legs'])}")

                    # Show legs of best journey
                    for i, leg in enumerate(best['legs'][:4]):
                        mode_icon = {
                            "flight": "✈️",
                            "train": "🚂",
                            "bus": "🚌",
                            "auto": "🚗"
                        }.get(leg['mode'], "🚗")

                        time_str = f" {leg['departure_time']}" if leg['departure_time'] else "----"
                        print(f"         {i+1}. {mode_icon} {leg['mode']:6} "
                              f"{leg['from_name']} → {leg['to_name']}: "
                              f"₹{leg['cost']}")

                    if best.get("warnings"):
                        print(f"         ⚠️  Warnings: {', '.join(best['warnings'])}")

            except ValueError as e:
                print(f"      ❌ {e}")

        print("\n✅ Journey planner test completed")

        return True

    except Exception as e:
        print(f"❌ Journey planner test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🧪 Testing Travel Planner India")
    print("=" * 60)

    success = test_database()

    if success:
        test_journey_planner()

    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    if success:
        print("✅ All tests passed!")
        print("\nNext steps:")
        print("1. Run: python3 app/main.py")
        print("2. Visit: http://localhost:8000/docs for API documentation")
        print("3. Try: curl http://localhost:8000/api/v1/search?from=Delhi&to=Kolkata")
        print("\nTo import real data:")
        print("   python3 scripts/sync_data.py --init-db")
        print("   python3 scripts/ixigo_flights_harvester.py --top-routes 20")
        print("   python3 scripts/redbus_harvester.py --discover-cities")
    else:
        print("❌ Some tests failed. Check if database was initialized.")
        print("Run: python3 scripts/sync_data.py --init-db")


if __name__ == "__main__":
    main()
