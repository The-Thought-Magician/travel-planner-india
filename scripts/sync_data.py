#!/usr/bin/env python3
"""
Sync harvested data into the database.

This script runs the harvesters and imports the data into the database.
Run this periodically (daily/weekly) to keep data fresh.

USAGE:
    # Initialize database and load seed data
    python3 scripts/sync_data.py --init-db

    # Import ixigo flight data
    python3 scripts/sync_data.py --import-ixigo --data data/cache/ixigo/flights.json

    # Import RedBus data
    python3 scripts/sync_data.py --import-redbus --data data/cache/redbus/routes.json

    # Import RailRadar live status
    python3 scripts/sync_data.py --import-railradar --data data/cache/railradar/live_status.json

    # Run harvesters and import in one command
    python3 scripts/sync_data.py --all --ixigo-top-routes 50
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal, init_db
from app.services import FlightDataImporter, BusDataImporter, TrainDataImporter


def init_database():
    """Initialize database with seed data."""
    print("=" * 60)
    print("Initializing Database")
    print("=" * 60)

    from app.init_db import main as init_db_main
    init_db_main()


def import_ixigo_data(data_file: str, limit: int = None):
    """Import ixigo flight data from harvester output."""
    print(f"\nImporting ixigo flight data from {data_file}")

    data_path = Path(data_file)
    if not data_path.exists():
        print(f"❌ Data file not found: {data_file}")
        return

    with open(data_path) as f:
        data = json.load(f)

    db = SessionLocal()
    importer = FlightDataImporter(db)

    imported = 0
    for record in data.get("flights", []) if isinstance(data, dict) else data:
        if limit and imported >= limit:
            break

        # Convert harvester format to importer format
        flight_record = {
            "flight_number": record.get("flight_number"),
            "airline": record.get("airline"),
            "airline_code": record.get("airline_code"),
            "origin": record.get("origin"),
            "destination": record.get("destination"),
            "departure_time": record.get("date"),  # ixigo has date in "dd-mm-yyyy" format
            "duration_minutes": None,  # Not directly provided
            "fare": record.get("fare")
        }

        result = importer.import_flight_record(flight_record)
        if result:
            imported += 1

    db.close()
    print(f"✅ Imported {imported} flight records")


def import_redbus_data(data_file: str, limit: int = None):
    """Import RedBus data from harvester output."""
    print(f"\nImporting RedBus data from {data_file}")

    data_path = Path(data_file)
    if not data_path.exists():
        print(f"❌ Data file not found: {data_file}")
        return

    with open(data_path) as f:
        data = json.load(f)

    db = SessionLocal()
    importer = BusDataImporter(db)

    imported = 0
    routes = data.get("routes", []) if isinstance(data, dict) else data

    for record in routes:
        if limit and imported >= limit:
            break

        result = importer.import_bus_record(record)
        if result:
            imported += 1

    db.close()
    print(f"✅ Imported {imported} bus routes")


def import_railradar_data(data_file: str, limit: int = None):
    """Import RailRadar live status data."""
    print(f"\nImporting RailRadar data from {data_file}")

    data_path = Path(data_file)
    if not data_path.exists():
        print(f"❌ Data file not found: {data_file}")
        return

    with open(data_path) as f:
        data = json.load(f)

    db = SessionLocal()
    importer = TrainDataImporter(db)

    # Process live status records
    imported = 0
    for record in data.get("live_status", []) if isinstance(data, dict) else data:
        if limit and imported >= limit:
            break

        # Import into TrainLiveStatus table for tracking
        from app.models import TrainLiveStatus
        from datetime import datetime

        status_record = TrainLiveStatus(
            train_no=record.get("train_number"),
            recorded_at=datetime.now(),
            source="railradar"
        )
        db.add(status_record)
        imported += 1

    db.commit()
    db.close()
    print(f"✅ Imported {imported} live status records")


def run_harvesters(options):
    """Run the harvesters and import data."""
    if options.ixigo_top_routes:
        print("\n" + "=" * 60)
        print(f"Harvesting ixigo flight data (top {options.ixigo_top_routes} routes)")
        print("=" * 60)

        from scripts.ixigo_flights_harvester import IxigoFlightHarvester

        harvester = IxigoFlightHarvester()
        routes = harvester.get_top_routes(options.ixigo_top_routes)

        # Harvest each route
        all_flights = []
        for origin, dest in routes:
            data = harvester.get_route_prices(origin, dest)
            if "data" in data and "going" in data["data"]:
                for flight in data["data"]["going"].get("results", []):
                    flight["origin"] = origin
                    flight["destination"] = dest
                    all_flights.append(flight)

        # Save and import
        output_dir = Path("data/cache/ixigo")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / "flights.json"

        with open(output_file, 'w') as f:
            json.dump({"flights": all_flights}, f, indent=2)

        print(f"\n✅ Harvested {len(all_flights)} flight records")
        import_ixigo_data(str(output_file))

    if options.redbus_top_routes:
        print("\n" + "=" * 60)
        print(f"Harvesting RedBus data (top {options.redbus_top_routes} routes)")
        print("=" * 60)

        from scripts.redbus_harvester import RedBusHarvester

        harvester = RedBusHarvester()

        # First discover cities
        harvester.discover_cities()

        # Then harvest routes
        routes = harvester.get_top_routes(options.redbus_top_routes)
        harvester.harvest_routes(routes)

        # Import the harvested data
        import_redbus_data("data/cache/redbus/routes.json")


def main():
    parser = argparse.ArgumentParser(description='Sync harvested data into database')
    parser.add_argument('--init-db', action='store_true', help='Initialize database with seed data')
    parser.add_argument('--import-ixigo', action='store_true', help='Import ixigo flight data')
    parser.add_argument('--ixigo-data', help='Path to ixigo flight data JSON file')
    parser.add_argument('--import-redbus', action='store_true', help='Import RedBus data')
    parser.add_argument('--redbus-data', help='Path to RedBus data JSON file')
    parser.add_argument('--import-railradar', action='store_true', help='Import RailRadar data')
    parser.add_argument('--railradar-data', help='Path to RailRadar data JSON file')
    parser.add_argument('--all', action='store_true', help='Run all harvesters')
    parser.add_argument('--ixigo-top-routes', type=int, help='Harvest ixigo top N routes')
    parser.add_argument('--redbus-top-routes', type=int, help='Harvest RedBus top N routes')

    args = parser.parse_args()

    if args.init_db:
        init_database()

    if args.all:
        # Run harvesters
        class Options:
            ixigo_top_routes = args.ixigo_top_routes or 50
            redbus_top_routes = args.redbus_top_routes or 20

        run_harvesters(Options())

    if args.import_ixigo and args.ixigo_data:
        import_ixigo_data(args.ixigo_data)

    if args.import_redbus and args.redbus_data:
        import_redbus_data(args.redbus_data)

    if args.import_railradar and args.railradar_data:
        import_railradar_data(args.railradar_data)

    if not any([args.init_db, args.import_ixigo, args.import_redbus, args.import_railradar, args.all]):
        parser.print_help()


if __name__ == "__main__":
    main()
