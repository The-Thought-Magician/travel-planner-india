"""Journey planner service - orchestrates search and routing."""

from datetime import date, time
from typing import Any

from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import City, Station, Airport
from app.scrapers import TrainScraper, FlightScraper
from app.routing.connection_scan import Connection, ConnectionScanAlgorithm, Journey


class JourneyPlanner:
    """
    Main service for planning multi-modal journeys.

    Orchestrates:
    1. Finding nearest stations/airports to origin/destination
    2. Scraping or fetching route options
    3. Running the routing algorithm
    4. Adding last-mile estimates
    5. Returning ranked journey options
    """

    def __init__(self) -> None:
        """Initialize the journey planner."""
        self.train_scraper = TrainScraper()
        self.flight_scraper = FlightScraper()
        self.db: Session = next(get_db())

    async def find_journeys(
        self,
        from_city: str,
        to_city: str,
        travel_date: date,
        preference: str = "balanced",
        max_transfers: int = 3,
    ) -> list[dict[str, Any]]:
        """
        Find journey options between two cities.

        Args:
            from_city: Origin city name
            to_city: Destination city name
            travel_date: Date of travel
            preference: Optimization preference
            max_transfers: Maximum transfers allowed

        Returns:
            List of journey option dictionaries
        """
        # 1. Resolve cities
        origin = self._find_city(from_city)
        destination = self._find_city(to_city)

        if not origin:
            raise ValueError(f"Origin city '{from_city}' not found")
        if not destination:
            raise ValueError(f"Destination city '{to_city}' not found")

        # 2. Get nearby stations and airports
        origin_stations = self._get_nearby_stations(origin)
        origin_airports = self._get_nearby_airports(origin)
        dest_stations = self._get_nearby_stations(destination)
        dest_airports = self._get_nearby_airports(destination)

        # 3. Build connections from all routes
        all_connections: list[Connection] = []

        # Flight routes
        for origin_ap in origin_airports:
            for dest_ap in dest_airports:
                flights = await self.flight_scraper.get_flights_between_airports(
                    origin_ap.iata_code, dest_ap.iata_code
                )
                for f in flights:
                    all_connections.append(
                        Connection(
                            mode="flight",
                            from_code=origin_ap.iata_code,
                            to_code=dest_ap.iata_code,
                            departure_time=f["departure_time"],
                            arrival_time=f["arrival_time"],
                            cost=f["price_avg"],
                            vehicle_id=f["flight_no"],
                            reliability=f.get("on_time_percentage", 0.8),
                            duration_minutes=f["duration_minutes"],
                        )
                    )

        # Train routes (sample for MVP - would use scraper in production)
        for origin_st in origin_stations[:2]:  # Limit for MVP
            for dest_st in dest_stations[:2]:
                trains = await self.train_scraper.get_trains_between_stations(
                    origin_st.code, dest_st.code
                )
                for t in trains:
                    if t["departure_time"] and t["arrival_time"]:
                        # Estimate pricing based on duration
                        estimated_cost = max(300, t["duration_minutes"] * 2)

                        all_connections.append(
                            Connection(
                                mode="train",
                                from_code=origin_st.code,
                                to_code=dest_st.code,
                                departure_time=t["departure_time"],
                                arrival_time=t["arrival_time"],
                                cost=estimated_cost,
                                vehicle_id=t["train_no"],
                                reliability=0.75,  # Base train reliability
                                duration_minutes=t["duration_minutes"],
                            )
                        )

        if not all_connections:
            # No direct routes found
            return self._create_fallback_journeys(origin, destination)

        # 4. Run routing algorithm
        csa = ConnectionScanAlgorithm(
            all_connections,
            min_connection_buffer=settings.min_connection_buffer_minutes,
        )

        journeys = csa.find_k_best(
            from_code=origin_airports[0].iata_code if origin_airports else origin_stations[0].code,
            to_code=dest_airports[0].iata_code if dest_airports else dest_stations[0].code,
            k=5,
            max_transfers=max_transfers,
            preference=preference,
        )

        # 5. Convert to response format with last-mile
        return [
            self._journey_to_dict(j, origin, destination, preference)
            for j in journeys[:5]
        ]

    def _find_city(self, name: str) -> City | None:
        """Find city by name (fuzzy match)."""
        city = (
            self.db.query(City)
            .filter(City.name.ilike(f"%{name}%"))
            .first()
        )
        return city

    def _get_nearby_stations(self, city: City, limit: int = 3) -> list[Station]:
        """Get railway stations near a city."""
        stations = (
            self.db.query(Station)
            .filter(Station.state == city.state)
            .limit(limit)
            .all()
        )
        return stations

    def _get_nearby_airports(self, city: City, limit: int = 2) -> list[Airport]:
        """Get airports near a city."""
        airports = (
            self.db.query(Airport)
            .filter(Airport.city.ilike(f"%{city.name}%"))
            .limit(limit)
            .all()
        )
        return airports

    def _journey_to_dict(
        self, journey: Journey, origin: City, destination: City, preference: str
    ) -> dict[str, Any]:
        """Convert Journey object to response dictionary."""
        from app.api.schemas import JourneyLeg

        legs = []
        warnings = []

        # Add origin last-mile
        origin_leg_cost = self._estimate_last_mile_cost(origin, distance_km=10)
        legs.append(
            {
                "mode": "auto",
                "from_name": origin.name,
                "to_name": f"{origin.name} Station/Airport",
                "cost": origin_leg_cost,
                "duration_minutes": 30,
                "departure_time": None,
                "arrival_time": None,
                "reliability_score": 0.95,
            }
        )

        # Add transport legs
        for conn in journey.connections:
            legs.append(
                {
                    "mode": conn.mode,
                    "from_name": conn.from_code,
                    "to_name": conn.to_code,
                    "from_code": conn.from_code,
                    "to_code": conn.to_code,
                    "cost": conn.cost,
                    "duration_minutes": conn.duration_minutes,
                    "departure_time": conn.departure_time.isoformat(),
                    "arrival_time": conn.arrival_time.isoformat(),
                    "flight_train_bus_no": conn.vehicle_id,
                    "reliability_score": conn.reliability,
                }
            )

            # Check for risky connections
            if conn.reliability < 0.8:
                warnings.append(
                    f"{conn.mode.upper()} {conn.vehicle_id} has low on-time performance "
                    f"({conn.reliability*100:.0f}%)"
                )

        # Add destination last-mile
        dest_leg_cost = self._estimate_last_mile_cost(destination, distance_km=10)
        legs.append(
            {
                "mode": "auto",
                "from_name": f"{destination.name} Station/Airport",
                "to_name": destination.name,
                "cost": dest_leg_cost,
                "duration_minutes": 30,
                "departure_time": None,
                "arrival_time": None,
                "reliability_score": 0.95,
            }
        )

        return {
            "rank": 0,  # Will be set by caller
            "total_cost": journey.total_cost + origin_leg_cost + dest_leg_cost,
            "total_duration_minutes": journey.total_duration + 60,  # +60 for last-mile
            "reliability_score": journey.reliability * 0.9,  # Adjusted for last-mile
            "legs": legs,
            "warnings": warnings if warnings else None,
            "booking_links": {
                "flights": "https://www.ixigo.com/flights",
                "trains": "https://www.irctc.co.in",
            },
        }

    def _estimate_last_mile_cost(self, city: City, distance_km: float) -> int:
        """Estimate auto/cab cost for last mile."""
        # Simple formula: base + (per_km * distance)
        auto_cost = city.auto_base_fare + int(city.auto_per_km * distance_km)
        return auto_cost

    def _create_fallback_journeys(
        self, origin: City, destination: City
    ) -> list[dict[str, Any]]:
        """Create basic fallback journeys when no routes found."""
        # Estimate a generic train journey
        distance_km = self._estimate_distance(origin, destination)
        estimated_cost = max(500, int(distance_km * 2))  # Rough estimate
        estimated_duration = int(distance_km / 50 * 60)  # ~50km/h average

        return [
            {
                "rank": 1,
                "total_cost": estimated_cost + 500,  # Including last-mile
                "total_duration_minutes": estimated_duration + 60,
                "reliability_score": 0.7,
                "legs": [
                    {
                        "mode": "auto",
                        "from_name": origin.name,
                        "to_name": f"{origin.name} Station",
                        "cost": 250,
                        "duration_minutes": 30,
                        "notes": "Estimated - to nearest railway station",
                    },
                    {
                        "mode": "train",
                        "from_name": origin.name,
                        "to_name": destination.name,
                        "cost": estimated_cost,
                        "duration_minutes": estimated_duration,
                        "notes": "Estimated - check IRCTC for exact trains",
                    },
                    {
                        "mode": "auto",
                        "from_name": f"{destination.name} Station",
                        "to_name": destination.name,
                        "cost": 250,
                        "duration_minutes": 30,
                        "notes": "Estimated - from railway station",
                    },
                ],
                "warnings": [
                    "Exact routes not found in database - this is an estimate",
                    "Please check IRCTC/Ixigo for actual availability",
                ],
            }
        ]

    def _estimate_distance(self, origin: City, destination: City) -> float:
        """Estimate distance between two cities (rough approximation)."""
        # For MVP, use state-based estimates
        # In production, use Haversine formula with lat/lon
        if origin.state == destination.state:
            return 200.0  # Same state
        return 800.0  # Different state
