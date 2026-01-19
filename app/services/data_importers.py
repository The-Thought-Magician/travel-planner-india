"""Data import services.

Services for importing harvested data from external APIs into the database.
"""

from datetime import datetime, time
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from app.models import City, Station, Airport, TrainRoute, FlightRoute, BusRoute


class FlightDataImporter:
    """Import flight data from ixigo harvester into database."""

    def __init__(self, db: Session):
        self.db = db

    def import_flight_record(self, flight_data: Dict) -> Optional[FlightRoute]:
        """Import a single flight record from ixigo harvester data."""
        try:
            # Check if route already exists
            existing = self.db.query(FlightRoute).filter(
                FlightRoute.flight_no == flight_data.get("flight_number"),
                FlightRoute.from_airport_code == flight_data.get("origin"),
                FlightRoute.to_airport_code == flight_data.get("destination"),
                FlightRoute.source == "ixigo"
            ).first()

            # Parse departure/arrival times
            dep_time = self._parse_time(flight_data.get("departure_time"))
            arr_time = self._parse_time(flight_data.get("arrival_time"))

            if existing:
                # Update existing record
                existing.airline = flight_data.get("airline", "Unknown")
                existing.airline_code = flight_data.get("airline_code", "")
                existing.departure_time = dep_time
                existing.arrival_time = arr_time
                existing.duration_minutes = flight_data.get("duration_minutes")
                existing.price_avg = int(flight_data.get("fare", 0))
                existing.last_harvested_at = datetime.now().isoformat()
                self.db.commit()
                return existing

            # Create new route
            route = FlightRoute(
                flight_no=flight_data.get("flight_number", ""),
                airline=flight_data.get("airline", "Unknown"),
                airline_code=flight_data.get("airline_code", ""),
                from_airport_code=flight_data["origin"],
                to_airport_code=flight_data["destination"],
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=flight_data.get("duration_minutes"),
                days_run="Daily",
                price_avg=int(flight_data.get("fare", 0)),
                price_min=int(flight_data.get("fare", 0)),
                price_max=int(flight_data.get("fare", 0)),
                source="ixigo",
                last_harvested_at=datetime.now().isoformat()
            )

            self.db.add(route)
            self.db.commit()
            self.db.refresh(route)
            return route

        except Exception as e:
            self.db.rollback()
            print(f"Error importing flight {flight_data.get('flight_number')}: {e}")
            return None

    def import_price_trends(self, origin: str, dest: str, trends_data: Dict):
        """Import 30-day price trends for a route."""
        try:
            # Update all routes on this path with price trends
            routes = self.db.query(FlightRoute).filter(
                FlightRoute.from_airport_code == origin,
                FlightRoute.to_airport_code == dest
            ).all()

            price_ranges = trends_data.get("price_ranges", {})
            for route in routes:
                route.price_trends = {
                    "low_range": price_ranges.get("low"),
                    "medium_range": price_ranges.get("medium"),
                    "high_range": price_ranges.get("high"),
                    "updated_at": datetime.now().isoformat()
                }

            self.db.commit()
            return len(routes)

        except Exception as e:
            self.db.rollback()
            print(f"Error importing price trends: {e}")
            return 0

    def _parse_time(self, time_str: str) -> Optional[time]:
        """Parse time string from various formats."""
        if not time_str:
            return None

        try:
            # Handle formats like "19:01:2026" or "14:30"
            parts = time_str.split(":")
            if len(parts) >= 2:
                hour = int(parts[0])
                minute = int(parts[1])
                return time(hour=hour % 24, minute=minute)
        except Exception:
            pass

        return None


class BusDataImporter:
    """Import bus data from RedBus harvester into database."""

    def __init__(self, db: Session):
        self.db = db

    def import_bus_record(self, bus_data: Dict) -> Optional[BusRoute]:
        """Import a single bus record from RedBus harvester data."""
        try:
            # Check if route already exists
            existing = self.db.query(BusRoute).filter(
                BusRoute.operator == bus_data.get("operator_name"),
                BusRoute.from_city == bus_data.get("from_city_name"),
                BusRoute.to_city == bus_data.get("to_city_name"),
                BusRoute.departure_time == self._parse_time(bus_data.get("departure_time")),
                BusRoute.source == "redbus"
            ).first()

            dep_time = self._parse_time(bus_data.get("departure_time"))
            arr_time = self._parse_time(bus_data.get("arrival_time"))

            fares = bus_data.get("fares", [])
            price_min = min(fares) if fares else None
            price_max = max(fares) if fares else None
            price_avg = int(sum(fares) / len(fares)) if fares else None

            if existing:
                existing.departure_time = dep_time
                existing.arrival_time = arr_time
                existing.duration_minutes = bus_data.get("duration_minutes")
                existing.price_min = price_min
                existing.price_avg = price_avg
                existing.price_max = price_max
                existing.rating = bus_data.get("rating")
                existing.fare_tiers = {
                    "fares": fares,
                    "available_seats": bus_data.get("available_seats"),
                    "total_seats": bus_data.get("total_seats")
                }
                existing.amenities = bus_data.get("amenities")
                existing.last_harvested_at = datetime.now().isoformat()
                self.db.commit()
                return existing

            # Create new route
            route = BusRoute(
                operator_id=bus_data.get("operator_id"),
                operator=bus_data.get("operator_name", "Unknown"),
                from_city_id=bus_data.get("from_city_id"),
                from_city=bus_data.get("from_city_name"),
                to_city_id=bus_data.get("to_city_id"),
                to_city=bus_data.get("to_city_name"),
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=bus_data.get("duration_minutes"),
                bus_type=bus_data.get("bus_type", "Standard"),
                price_min=price_min,
                price_avg=price_avg,
                price_max=price_max,
                rating=bus_data.get("rating"),
                fare_tiers={
                    "fares": fares,
                    "available_seats": bus_data.get("available_seats"),
                    "total_seats": bus_data.get("total_seats")
                },
                amenities=bus_data.get("amenities"),
                source="redbus",
                last_harvested_at=datetime.now().isoformat()
            )

            self.db.add(route)
            self.db.commit()
            self.db.refresh(route)
            return route

        except Exception as e:
            self.db.rollback()
            print(f"Error importing bus {bus_data.get('operator_name')}: {e}")
            return None

    def _parse_time(self, time_str: str) -> Optional[time]:
        """Parse time string."""
        if not time_str:
            return None

        try:
            # Handle formats like "2026-01-20 20:50:00" or "20:50"
            if " " in time_str:
                time_part = time_str.split(" ")[1]
            else:
                time_part = time_str

            parts = time_part.split(":")
            if len(parts) >= 2:
                hour = int(parts[0])
                minute = int(parts[1])
                return time(hour=hour % 24, minute=minute)
        except Exception:
            pass

        return None


class TrainDataImporter:
    """Import train data into database."""

    def __init__(self, db: Session):
        self.db = db

    def import_train_record(self, train_data: Dict) -> Optional[TrainRoute]:
        """Import a single train record."""
        try:
            # Check if route already exists
            existing = self.db.query(TrainRoute).filter(
                TrainRoute.train_no == train_data.get("train_no"),
                TrainRoute.from_station_code == train_data.get("from_station"),
                TrainRoute.to_station_code == train_data.get("to_station")
            ).first()

            dep_time = self._parse_time(train_data.get("departure_time"))
            arr_time = self._parse_time(train_data.get("arrival_time"))

            if existing:
                existing.train_name = train_data.get("train_name", existing.train_name)
                existing.departure_time = dep_time
                existing.arrival_time = arr_time
                existing.duration_minutes = train_data.get("duration_minutes")
                existing.pricing = train_data.get("pricing")
                existing.on_time_percentage = train_data.get("on_time_percentage")
                existing.classes = train_data.get("classes")
                existing.last_harvested_at = datetime.now().isoformat()
                self.db.commit()
                return existing

            # Create new route
            route = TrainRoute(
                train_no=train_data.get("train_no"),
                train_name=train_data.get("train_name", ""),
                from_station_code=train_data.get("from_station"),
                to_station_code=train_data.get("to_station"),
                departure_time=dep_time,
                arrival_time=arr_time,
                duration_minutes=train_data.get("duration_minutes"),
                distance_km=train_data.get("distance_km"),
                days_run=train_data.get("days_run", "Daily"),
                pricing=train_data.get("pricing"),
                on_time_percentage=train_data.get("on_time_percentage"),
                classes=train_data.get("classes"),
                source=train_data.get("source", "data.gov.in"),
                last_harvested_at=datetime.now().isoformat()
            )

            self.db.add(route)
            self.db.commit()
            self.db.refresh(route)
            return route

        except Exception as e:
            self.db.rollback()
            print(f"Error importing train {train_data.get('train_no')}: {e}")
            return None

    def _parse_time(self, time_str: str) -> Optional[time]:
        """Parse time string (HH:MM format)."""
        if not time_str:
            return None

        try:
            parts = str(time_str).split(":")
            if len(parts) >= 2:
                hour = int(parts[0])
                minute = int(parts[1])
                return time(hour=hour % 24, minute=minute)
        except Exception:
            pass

        return None


class CityDataImporter:
    """Import city data including RedBus cities and ixigo airports."""

    def __init__(self, db: Session):
        self.db = db

    def import_or_update_city(self, city_data: Dict) -> Optional[City]:
        """Import or update a city from harvested data."""
        try:
            # Try to find by name first
            city = self.db.query(City).filter(
                City.name == city_data.get("name")
            ).first()

            if city:
                # Update existing
                city.latitude = city_data.get("latitude", city.latitude)
                city.longitude = city_data.get("longitude", city.longitude)
                city.state = city_data.get("state", city.state)
                if city_data.get("code"):
                    city.code = city_data["code"]
                return city

            # Create new city
            city = City(
                name=city_data["name"],
                state=city_data.get("state", ""),
                latitude=city_data.get("latitude"),
                longitude=city_data.get("longitude"),
                code=city_data.get("code"),
                is_top_city=len(self.db.query(City).all()) < 50
            )

            self.db.add(city)
            self.db.commit()
            self.db.refresh(city)
            return city

        except Exception as e:
            self.db.rollback()
            print(f"Error importing city {city_data.get('name')}: {e}")
            return None
