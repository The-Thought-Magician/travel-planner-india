"""Journey planner service - orchestrates search and routing."""

from datetime import date, datetime, time
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import City, Station, Airport, TrainRoute, FlightRoute, BusRoute
from app.routing.connection_scan import Connection, ConnectionScanAlgorithm, Journey
from app.services.geospatial import GeospatialService, Location


class JourneyPlanner:
    """
    Main service for planning multi-modal journeys.

    Orchestrates:
    1. Finding nearest stations/airports to origin/destination
    2. Querying route options from database
    3. Running the routing algorithm
    4. Adding last-mile estimates
    5. Finding intermediate nodes with proximity search
    6. Returning ranked journey options
    """

    def __init__(self, db: Optional[Session] = None):
        """Initialize the journey planner."""
        self.db = db if db else next(get_db())
        self.geo = GeospatialService(self.db)

    def find_journeys(
        self,
        from_city: str,
        to_city: str,
        travel_date: date | None = None,
        preference: str = "balanced",
        max_transfers: int = 3,
        max_journeys: int = 5,
    ) -> tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Find journey options between two cities.

        Args:
            from_city: Origin city name
            to_city: Destination city name
            travel_date: Date of travel (optional, for date-specific pricing)
            preference: Optimization preference (fastest, cheapest, balanced, most_reliable)
            max_transfers: Maximum transfers allowed
            max_journeys: Maximum number of journey options to return

        Returns:
            Tuple of (journeys list, metadata dict)
        """
        # 1. Resolve cities
        origin = self._find_city(from_city)
        destination = self._find_city(to_city)

        if not origin:
            return self._create_fallback_journeys(
                City(name=from_city, state="Unknown", latitude=0, longitude=0, code=None),
                destination
            )

        if not destination:
            return self._create_fallback_journeys(
                origin,
                City(name=to_city, state="Unknown", latitude=0, longitude=0, code=None)
            )

        # 2. Get nearby transport hubs (returns List[Location] directly)
        origin_stations = self.geo.find_nearby_stations(
            origin.latitude, origin.longitude, radius_km=50, limit=5
        )
        origin_airports = self.geo.find_nearby_airports(
            origin.latitude, origin.longitude, radius_km=100, limit=3
        )
        dest_stations = self.geo.find_nearby_stations(
            destination.latitude, destination.longitude, radius_km=50, limit=5
        )
        dest_airports = self.geo.find_nearby_airports(
            destination.latitude, destination.longitude, radius_km=100, limit=3
        )

        # Combine all origin and destination locations
        origin_locations = origin_stations + origin_airports
        dest_locations = dest_stations + dest_airports

        if not origin_locations or not dest_locations:
            return self._create_fallback_journeys(origin, destination)

        # 3. Build connections from database routes
        all_connections: List[Connection] = []

        # Flight routes
        for origin_loc in origin_locations:
            if origin_loc.location_type != "airport":
                continue

            for dest_loc in dest_locations:
                if dest_loc.location_type != "airport":
                    continue

                flights = self._get_flights_from_db(
                    origin_loc.code, dest_loc.code
                )
                for flight in flights:
                    all_connections.append(self._flight_to_connection(flight))

        # Train routes
        for origin_loc in origin_locations:
            if origin_loc.location_type != "station":
                continue

            for dest_loc in dest_locations:
                if dest_loc.location_type != "station":
                    continue

                trains = self._get_trains_from_db(
                    origin_loc.code, dest_loc.code
                )
                for train in trains:
                    all_connections.append(self._train_to_connection(train))

        # Bus routes
        bus_routes = self._get_bus_routes_from_db(
            origin.name, destination.name
        )
        for bus_route in bus_routes:
            all_connections.append(self._bus_to_connection(bus_route))

        if not all_connections:
            return self._create_fallback_journeys(origin, destination)

        # 4. Run routing algorithm - try all origin/destination combinations
        csa = ConnectionScanAlgorithm(
            all_connections,
            min_connection_buffer=settings.min_connection_buffer_minutes,
        )

        # Try all combinations of origin and destination locations
        all_journeys = []
        for from_loc in origin_locations:
            for to_loc in dest_locations:
                journeys = csa.find_k_best(
                    from_code=from_loc.code,
                    to_code=to_loc.code,
                    k=max_journeys,
                    max_transfers=max_transfers,
                    preference=preference,
                )
                for j in journeys:
                    # Store with the actual origin/dest location info
                    j._origin_location = from_loc
                    j._dest_location = to_loc
                all_journeys.extend(journeys)

        # Sort by combined score and limit
        all_journeys.sort(key=lambda j: j.total_cost, reverse=False)
        journeys = all_journeys[:max_journeys]

        # 5. Convert to response format with last-mile
        journey_dicts = [
            self._journey_to_dict(j, origin, destination, preference)
            for j in journeys
        ]

        # Calculate intermediate nodes for top journey
        metadata = {}
        if journey_dicts:
            top_journey = journey_dicts[0]
            intermediate_nodes = self.geo.find_intermediate_nodes(
                origin.latitude, origin.longitude,
                destination.latitude, destination.longitude,
                proximity_km=20
            )

            if intermediate_nodes:
                metadata["intermediate_nodes"] = [
                    {
                        "name": node.name,
                        "distance_from_origin": node.distance_to_origin,
                        "distance_to_dest": self.geo.calculate_distance(
                            node.latitude, node.longitude,
                            destination.latitude, destination.longitude
                        )
                    }
                    for node in intermediate_nodes[:5]
                ]

        return journey_dicts, metadata

    def _find_city(self, name: str) -> Optional[City]:
        """Find city by name (fuzzy match)."""
        city = (
            self.db.query(City)
            .filter(City.name.ilike(f"%{name}%"))
            .first()
        )
        return city

    def _get_flights_from_db(self, origin: str, destination: str) -> List[FlightRoute]:
        """Get flight routes from database."""
        return (
            self.db.query(FlightRoute)
            .filter(
                FlightRoute.from_airport_code == origin,
                FlightRoute.to_airport_code == destination,
                FlightRoute.is_active == True
            )
            .order_by(FlightRoute.price_avg)
            .limit(10)
            .all()
        )

    def _get_trains_from_db(self, origin: str, destination: str) -> List[TrainRoute]:
        """Get train routes from database."""
        return (
            self.db.query(TrainRoute)
            .filter(
                TrainRoute.from_station_code == origin,
                TrainRoute.to_station_code == destination,
                TrainRoute.is_active == True
            )
            .order_by(TrainRoute.duration_minutes)
            .limit(10)
            .all()
        )

    def _get_bus_routes_from_db(self, from_city: str, to_city: str) -> List[BusRoute]:
        """Get bus routes from database."""
        return (
            self.db.query(BusRoute)
            .filter(
                BusRoute.from_city == from_city,
                BusRoute.to_city == to_city,
                BusRoute.is_active == True
            )
            .order_by(BusRoute.duration_minutes)
            .limit(10)
            .all()
        )

    def _flight_to_connection(self, flight: FlightRoute) -> Connection:
        """Convert FlightRoute to Connection object."""
        dep_time = datetime.combine(datetime.now().date(), flight.departure_time)
        arr_time = datetime.combine(datetime.now().date(), flight.arrival_time)

        return Connection(
            mode="flight",
            from_code=flight.from_airport_code,
            to_code=flight.to_airport_code,
            departure_time=dep_time,
            arrival_time=arr_time,
            cost=flight.price_avg or 0,
            vehicle_id=flight.flight_no,
            reliability=flight.on_time_percentage or 0.85,
            duration_minutes=flight.duration_minutes,
        )

    def _train_to_connection(self, train: TrainRoute) -> Connection:
        """Convert TrainRoute to Connection object."""
        dep_time = datetime.combine(datetime.now().date(), train.departure_time)
        arr_time = datetime.combine(datetime.now().date(), train.arrival_time)

        # Get pricing - prefer 3A or Sleeper
        price = 500
        if train.pricing:
            price = train.pricing.get("3A", train.pricing.get("SL", 500))

        return Connection(
            mode="train",
            from_code=train.from_station_code,
            to_code=train.to_station_code,
            departure_time=dep_time,
            arrival_time=arr_time,
            cost=price,
            vehicle_id=str(train.train_no),
            reliability=train.on_time_percentage or 0.75,
            duration_minutes=train.duration_minutes,
        )

    def _bus_to_connection(self, bus: BusRoute) -> Connection:
        """Convert BusRoute to Connection object."""
        dep_time = datetime.combine(datetime.now().date(), bus.departure_time)
        arr_time = datetime.combine(datetime.now().date(), bus.arrival_time)

        return Connection(
            mode="bus",
            from_city=bus.from_city,
            to_city=bus.to_city,
            from_code=bus.from_city,
            to_code=bus.to_city,
            departure_time=dep_time,
            arrival_time=arr_time,
            cost=bus.price_avg or 0,
            vehicle_id=bus.operator,
            reliability=bus.rating or 4.0,
            duration_minutes=bus.duration_minutes,
        )

    def _journey_to_dict(
        self,
        journey: Journey,
        origin: City,
        destination: City,
        preference: str
    ) -> dict[str, Any]:
        """Convert Journey object to response dictionary."""
        legs = []
        warnings = []
        total_cost = 0
        total_duration = 0

        # Add origin last-mile (estimated)
        origin_leg_cost = self.geo.estimate_last_mile_cost(
            origin.id, distance_km=10
        )
        legs.append({
            "mode": "auto",
            "from_name": origin.name,
            "to_name": f"{origin.name} Bus/Train Station or Airport",
            "cost": origin_leg_cost,
            "duration_minutes": 30,
            "departure_time": None,
            "arrival_time": None,
            "reliability_score": 0.95,
        })
        total_cost += origin_leg_cost
        total_duration += 30

        # Add transport legs
        for conn in journey.connections:
            if conn.mode == "bus":
                leg = {
                    "mode": conn.mode,
                    "from_name": conn.from_city,
                    "to_name": conn.to_city,
                    "from_code": conn.from_code,
                    "to_code": conn.to_code,
                    "cost": conn.cost,
                    "duration_minutes": conn.duration_minutes,
                    "departure_time": conn.departure_time.isoformat() if conn.departure_time else None,
                    "arrival_time": conn.arrival_time.isoformat() if conn.arrival_time else None,
                    "flight_train_bus_no": conn.vehicle_id,
                    "reliability_score": conn.reliability,
                }
            else:
                leg = {
                    "mode": conn.mode,
                    "from_name": conn.from_code,
                    "to_name": conn.to_code,
                    "from_code": conn.from_code,
                    "to_code": conn.to_code,
                    "cost": conn.cost,
                    "duration_minutes": conn.duration_minutes,
                    "departure_time": conn.departure_time.isoformat() if conn.departure_time else None,
                    "arrival_time": conn.arrival_time.isoformat() if conn.arrival_time else None,
                    "flight_train_bus_no": conn.vehicle_id,
                    "reliability_score": conn.reliability,
                }

            legs.append(leg)
            total_cost += conn.cost
            total_duration += conn.duration_minutes

            # Check for risky connections
            if conn.reliability < 0.7:
                warnings.append(
                    f"{conn.mode.upper()} {conn.vehicle_id} has low reliability ({conn.reliability*100:.0f}%)"
                )

        # Add destination last-mile (estimated)
        dest_leg_cost = self.geo.estimate_last_mile_cost(
            destination.id, distance_km=10
        )
        legs.append({
            "mode": "auto",
            "from_name": f"{destination.name} Bus/Train Station or Airport",
            "to_name": destination.name,
            "cost": dest_leg_cost,
            "duration_minutes": 30,
            "departure_time": None,
            "arrival_time": None,
            "reliability_score": 0.95,
        })
        total_cost += dest_leg_cost
        total_duration += 30

        # Calculate overall journey reliability
        transport_reliability = journey.reliability if journey.reliability else 0.75
        journey_reliability = transport_reliability * 0.9  # Adjust for last-mile uncertainty

        return {
            "rank": 0,  # Will be set by caller
            "total_cost": total_cost,
            "total_duration_minutes": total_duration,
            "reliability_score": journey_reliability,
            "legs": legs,
            "warnings": warnings if warnings else None,
            "booking_links": {
                "flights": "https://www.ixigo.com/flights",
                "trains": "https://www.irctc.co.in",
                "buses": "https://www.redbus.in",
            },
        }

    def _create_fallback_journeys(
        self,
        origin: City,
        destination: City
    ) -> Tuple[List[Dict], Dict]:
        """Create basic fallback journeys when no routes found."""
        # Estimate direct distance
        distance_km = self.geo.calculate_distance(
            origin.latitude, origin.longitude,
            destination.latitude, destination.longitude
        )

        estimated_cost = max(500, int(distance_km * 2))
        estimated_duration = int(distance_km / 50 * 60)  # ~50km/h average

        journey = {
            "rank": 1,
            "total_cost": estimated_cost + 500,
            "total_duration_minutes": estimated_duration + 60,
            "reliability_score": 0.7,
            "legs": [
                {
                    "mode": "auto",
                    "from_name": origin.name,
                    "to_name": origin.name,
                    "cost": 0,
                    "duration_minutes": 0,
                    "notes": "Start your journey",
                },
                {
                    "mode": "multi-modal",
                    "from_name": origin.name,
                    "to_name": destination.name,
                    "cost": estimated_cost,
                    "duration_minutes": estimated_duration,
                    "departure_time": None,
                    "arrival_time": None,
                    "reliability_score": 0.7,
                    "notes": "Estimated - Check IRCTC/RedBus for actual availability",
                },
                {
                    "mode": "auto",
                    "from_name": destination.name,
                    "to_name": destination.name,
                    "cost": 0,
                    "duration_minutes": 0,
                    "notes": "End destination",
                },
            ],
            "warnings": [
                "No direct routes found in database",
                "Please run: python3 scripts/sync_data.py --all to import data",
                "Check: https://data.gov.in for train timetable",
                "Check: https://ixigo.com for flights",
                "Check: https://redbus.in for buses",
            ],
            "booking_links": {
                "flights": "https://www.ixigo.com/flights",
                "trains": "https://www.irctc.co.in",
                "buses": "https://www.redbus.in",
            },
        }

        return [journey], {
            "error": "No routes found in database. Run: python3 scripts/sync_data.py --all to import data.",
            "suggestion": "Import data first: python3 scripts/sync_data.py --all",
            "origin": f"{origin.name} ({origin.code})",
            "destination": f"{destination.name} ({destination.code})",
            "distance_km": distance_km
        }

    def search_locations(self, query: str, limit: int = 10) -> List[Dict]:
        """Search for locations by name."""
        locations = self.geo.find_locations_by_name(query, limit)

        return [
            {
                "type": loc.location_type,
                "name": loc.name,
                "code": loc.code,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "distance_from_origin": loc.distance_to_origin,
                "city_id": loc.city_id,
            }
            for loc in locations
        ]
