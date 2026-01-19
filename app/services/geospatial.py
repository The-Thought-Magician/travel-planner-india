"""Geospatial service for proximity calculations.

Handles finding nearby locations within a given radius,
calculating distances, and determining intermediate nodes.
"""

import math
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session

from app.models import City, Station, Airport
from app.services.data_importers import CityDataImporter


@dataclass
class Location:
    """Represent a location with coordinates."""
    name: str
    latitude: float
    longitude: float
    location_type: str  # "city", "station", "airport"
    code: str | None = None
    city_id: int | None = None
    distance_to_origin: float = 0.0


class GeospatialService:
    """Service for geospatial calculations and proximity queries."""

    def __init__(self, db: Session):
        self.db = db

    def calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two points using Haversine formula (in km).

        Args:
            lat1, lon1: Coordinates of first point
            lat2, lon2: Coordinates of second point

        Returns:
            Distance in kilometers
        """
        R = 6371  # Earth's radius in km

        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)

        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def find_nearby_cities(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 20,
        limit: int = 10
    ) -> List[Location]:
        """Find cities within a given radius.

        Args:
            latitude, longitude: Center point coordinates
            radius_km: Search radius in kilometers
            limit: Maximum number of results

        Returns:
            List of nearby cities with distances
        """
        cities = self.db.query(City).filter(
            City.latitude.isnot(None),
            City.longitude.isnot(None)
        ).all()

        nearby = []
        for city in cities:
            distance = self.calculate_distance(
                latitude, longitude,
                city.latitude, city.longitude
            )

            if distance <= radius_km:
                nearby.append(Location(
                    name=city.name,
                    latitude=city.latitude,
                    longitude=city.longitude,
                    location_type="city",
                    code=city.code,
                    city_id=city.id,
                    distance_to_origin=distance
                ))

        # Sort by distance and limit
        nearby.sort(key=lambda x: x.distance_to_origin)
        return nearby[:limit]

    def find_nearby_stations(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 20,
        limit: int = 10
    ) -> List[Location]:
        """Find railway stations within a given radius."""
        stations = self.db.query(Station).filter(
            Station.latitude.isnot(None),
            Station.longitude.isnot(None)
        ).all()

        nearby = []
        for station in stations:
            distance = self.calculate_distance(
                latitude, longitude,
                station.latitude, station.longitude
            )

            if distance <= radius_km:
                nearby.append(Location(
                    name=station.name,
                    latitude=station.latitude,
                    longitude=station.longitude,
                    location_type="station",
                    code=station.code,
                    city_id=station.nearest_city_id,
                    distance_to_origin=distance
                ))

        nearby.sort(key=lambda x: x.distance_to_origin)
        return nearby[:limit]

    def find_nearby_airports(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 50,
        limit: int = 10
    ) -> List[Location]:
        """Find airports within a given radius."""
        airports = self.db.query(Airport).all()

        nearby = []
        for airport in airports:
            distance = self.calculate_distance(
                latitude, longitude,
                airport.latitude, airport.longitude
            )

            if distance <= radius_km:
                nearby.append(Location(
                    name=airport.name,
                    latitude=airport.latitude,
                    longitude=airport.longitude,
                    location_type="airport",
                    code=airport.iata_code,
                    city_id=airport.nearest_city_id,
                    distance_to_origin=distance
                ))

        nearby.sort(key=lambda x: x.distance_to_origin)
        return nearby[:limit]

    def find_intermediate_nodes(
        self,
        origin_lat: float,
        origin_lon: float,
        dest_lat: float,
        dest_lon: float,
        proximity_km: float = 20,
        max_deviation: float = 1.3
    ) -> List[Location]:
        """Find intermediate nodes between two points.

        Args:
            origin_lat, origin_lon: Starting point coordinates
            dest_lat, dest_lon: Destination coordinates
            proximity_km: Maximum distance from route to include a node
            max_deviation: Maximum ratio of sum-of-distances to direct distance

        Returns:
            List of intermediate locations sorted by distance from origin
        """
        direct_distance = self.calculate_distance(
            origin_lat, origin_lon,
            dest_lat, dest_lon
        )

        # Get all cities
        cities = self.db.query(City).filter(
            City.latitude.isnot(None),
            City.longitude.isnot(None)
        ).all()

        intermediate = []

        for city in cities:
            # Skip origin and destination (approximate match)
            dist_to_origin = self.calculate_distance(
                origin_lat, origin_lon,
                city.latitude, city.longitude
            )
            dist_to_dest = self.calculate_distance(
                city.latitude, city.longitude,
                dest_lat, dest_lon
            )

            # Check if city is beyond origin or destination (along the route)
            if dist_to_origin < direct_distance and dist_to_dest < direct_distance:
                # Check if it's reasonably along the path
                sum_distance = dist_to_origin + dist_to_dest
                deviation_ratio = sum_distance / direct_distance if direct_distance > 0 else float('inf')

                # Also check proximity to the great circle path
                distance_from_path = self._distance_from_path(
                    origin_lat, origin_lon,
                    dest_lat, dest_lon,
                    city.latitude, city.longitude
                )

                if deviation_ratio <= max_deviation and distance_from_path <= proximity_km:
                    intermediate.append(Location(
                        name=city.name,
                        latitude=city.latitude,
                        longitude=city.longitude,
                        location_type="city",
                        code=city.code,
                        city_id=city.id,
                        distance_to_origin=dist_to_origin
                    ))

        # Sort by distance from origin
        intermediate.sort(key=lambda x: x.distance_to_origin)
        return intermediate

    def _distance_from_path(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float,
        lat3: float, lon3: float
    ) -> float:
        """Calculate perpendicular distance from point 3 to line segment 1-2.

        Uses cross-track distance formula.
        """
        R = 6371  # Earth's radius in km

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        lat3_rad = math.radians(lat3)
        lon1_rad = math.radians(lon1)
        lon2_rad = math.radians(lon2)
        lon3_rad = math.radians(lon3)

        # Bearing from point 1 to point 2
        theta12 = math.atan2(
            math.sin(lon2_rad - lon1_rad) * math.cos(lat2_rad),
            math.cos(lat1_rad) * math.sin(lat2_rad) -
            math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(lon2_rad - lon1_rad)
        )

        # Bearing from point 1 to point 3
        theta13 = math.atan2(
            math.sin(lon3_rad - lon1_rad) * math.cos(lat3_rad),
            math.cos(lat1_rad) * math.sin(lat3_rad) -
            math.sin(lat1_rad) * math.cos(lat3_rad) * math.cos(lon3_rad - lon1_rad)
        )

        # Angular distance from point 1 to point 3
        d13 = math.acos(
            math.sin(lat1_rad) * math.sin(lat3_rad) +
            math.cos(lat1_rad) * math.cos(lat3_rad) * math.cos(lon3_rad - lon1_rad)
        )

        # Cross-track distance
        dxt = math.asin(math.sin(d13) * math.sin(theta13 - theta12)) * R

        return abs(dxt)

    def find_locations_by_name(
        self,
        query: str,
        limit: int = 5
    ) -> List[Location]:
        """Find locations by name search.

        Searches cities, stations, and airports.
        """
        query_lower = query.lower()
        results = []

        # Search cities
        cities = self.db.query(City).filter(
            City.name.ilike(f"%{query}%")
        ).limit(limit).all()

        for city in cities:
            results.append(Location(
                name=city.name,
                latitude=city.latitude or 0,
                longitude=city.longitude or 0,
                location_type="city",
                code=city.code,
                city_id=city.id
            ))

        # Search stations
        stations = self.db.query(Station).filter(
            Station.name.ilike(f"%{query}%")
        ).limit(limit).all()

        for station in stations:
            results.append(Location(
                name=station.name,
                latitude=station.latitude or 0,
                longitude=station.longitude or 0,
                location_type="station",
                code=station.code
            ))

        # Search airports
        airports = self.db.query(Airport).filter(
            Airport.name.ilike(f"%{query}%") |
            Airport.iata_code.ilike(f"%{query}%")
        ).limit(limit).all()

        for airport in airports:
            results.append(Location(
                name=airport.name,
                latitude=airport.latitude,
                longitude=airport.longitude,
                location_type="airport",
                code=airport.iata_code
            ))

        return results[:limit]

    def estimate_last_mile_cost(
        self,
        city_id: int,
        distance_km: float,
        transport_type: str = "auto"
    ) -> int:
        """Estimate last-mile transport cost.

        Args:
            city_id: City ID
            distance_km: Distance in kilometers
            transport_type: "auto" or "cab"

        Returns:
            Estimated cost in INR
        """
        city = self.db.query(City).get(city_id)
        if not city:
            # Default rates
            base_fare = 25 if transport_type == "auto" else 50
            per_km = 15 if transport_type == "auto" else 20
            return base_fare + int(per_km * distance_km)

        if transport_type == "auto":
            base_fare = city.auto_base_fare
            per_km = city.auto_per_km
        else:  # cab
            base_fare = city.cab_base_fare
            per_km = city.cab_per_km

        return base_fare + int(per_km * distance_km)
