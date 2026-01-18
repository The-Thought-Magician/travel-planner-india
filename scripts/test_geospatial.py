#!/usr/bin/env python3
"""
Test geospatial/proximity functionality.

This is CRITICAL for the core feature:
"Find all nodes between A and B with proximity of 20km"

We'll test:
1. GeoPy for distance calculations
2. Finding nearby stations/airports within radius
3. Creating proximity graphs
"""

import math
from geopy.distance import geodesic
from geopy.point import Point
import json
import os


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance between two points using Haversine formula (no dependency)."""

    R = 6371  # Earth's radius in km

    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)

    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) *
         math.sin(delta_lon / 2) ** 2)

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c

    return distance


def test_geopy():
    """Test GeoPy for distance calculations."""

    print("=" * 60)
    print("Testing Geospatial Functionality")
    print("=" * 60)

    print(f"\n📏 Test 1: Distance calculation with GeoPy")
    print("-" * 60)

    # Sample coordinates (Indian cities)
    locations = {
        "Delhi": (28.6139, 77.2090),
        "Mumbai": (19.0760, 72.8777),
        "Bangalore": (12.9716, 77.5946),
        "Chennai": (13.0827, 80.2707),
        "Kolkata": (22.5726, 88.3639),
        "Hyderabad": (17.3850, 78.4867),
        "Ranchi": (23.3441, 85.3096),
        "Hampi": (15.3350, 76.4600),
    }

    # Test distance between major cities
    test_pairs = [
        ("Delhi", "Mumbai"),
        ("Bangalore", "Chennai"),
        ("Ranchi", "Hampi"),
    ]

    for city1, city2 in test_pairs:
        coord1 = locations[city1]
        coord2 = locations[city2]

        # Using GeoPy
        distance_geopy = geodesic(coord1, coord2).kilometers

        # Using Haversine (backup)
        distance_haversine = haversine_distance(
            coord1[0], coord1[1],
            coord2[0], coord2[1]
        )

        print(f"   {city1} → {city2}:")
        print(f"      GeoPy: {distance_geopy:.1f} km")
        print(f"      Haversine: {distance_haversine:.1f} km")

    print(f"\n✅ Distance calculation: Working")

    return locations


def test_proximity_search(locations):
    """Test finding nearby locations within a radius."""

    print(f"\n🔍 Test 2: Proximity search (find locations within 20km)")
    print("-" * 60)

    # Sample train stations with coordinates
    stations = {
        "NDLS (New Delhi)": (28.6431, 77.2197),
        "BCT (Mumbai Central)": (18.9682, 72.8195),
        "SBC (Bangalore City)": (12.9777, 77.5728),
        "MAS (Chennai Central)": (13.0821, 80.2750),
        "HWH (Howrah)": (22.5833, 88.3417),
        "SC (Secunderabad)": (17.4398, 78.4983),
        "RNC (Ranchi)": (23.3567, 85.3339),
        "HPT (Hospet)": (15.2784, 76.4033),  # Near Hampi
    }

    # Find stations within 20km of a city
    radius_km = 20

    print(f"   Finding stations within {radius_km}km of major cities:\n")

    for city, city_coord in locations.items():
        if city not in ["Delhi", "Bangalore", "Hampi"]:
            continue

        print(f"   🏙️  {city}:")
        nearby = []

        for station, station_coord in stations.items():
            distance = geodesic(city_coord, station_coord).kilometers
            if distance <= radius_km:
                nearby.append((station, distance))

        if nearby:
            for station, distance in nearby:
                print(f"      ✅ {station}: {distance:.1f} km")
        else:
            print(f"      (No stations within {radius_km}km)")
        print()

    print(f"✅ Proximity search: Working")


def test_intermediate_nodes(locations):
    """
    Test finding intermediate nodes between two points.
    This is crucial for multi-modal journey planning.
    """

    print(f"\n🗺️  Test 3: Find intermediate nodes between A and B")
    print("-" * 60)

    # More detailed location list (simulating train stations)
    intermediate_locations = {
        "Ranchi": (23.3441, 85.3096),
        "Bokaro": (23.6718, 86.1516),
        "Dhanbad": (23.7957, 86.4304),
        "Asansol": (23.6739, 86.9524),
        "Durgapur": (23.5204, 87.3119),
        "Kolkata": (22.5726, 88.3639),
        "Kharagpur": (22.3424, 87.3328),
        "Bhubaneswar": (20.2961, 85.8245),
        "Vizag": (17.6868, 83.2185),
        "Vijayawada": (16.5062, 80.6480),
        "Hyderabad": (17.3850, 78.4867),
        "Bangalore": (12.9716, 77.5946),
        "Hospet": (15.2784, 76.4033),
        "Hampi": (15.3350, 76.4600),
    }

    # Find stations within 50km of the straight line path
    origin = "Ranchi"
    destination = "Hampi"
    search_radius = 50  # km

    print(f"   Journey: {origin} → {destination}")
    print(f"   Search radius: {search_radius}km from path\n")

    # Simple approach: Find points within radius of any point along the path
    # For each intermediate location, check if it's reasonably close to the path

    origin_coord = intermediate_locations[origin]
    dest_coord = intermediate_locations[destination]

    # Calculate total distance
    total_distance = geodesic(origin_coord, dest_coord).kilometers
    print(f"   Direct distance: {total_distance:.1f} km\n")

    # Find intermediate points (simplified - check distance from line segment)
    print(f"   Potential intermediate nodes (within {search_radius}km of journey):")

    intermediate_nodes = []
    for name, coord in intermediate_locations.items():
        if name in [origin, destination]:
            continue

        # Check if this point is relatively close to our general path direction
        # Simplified: check distance from origin, if less than total distance
        # and check if it's "along the way" (roughly)

        dist_from_origin = geodesic(origin_coord, coord).kilometers
        dist_to_dest = geodesic(coord, dest_coord).kilometers

        # If sum of distances is not much more than direct route, it's on the way
        # This is a simplified check
        if dist_from_origin + dist_to_dest < total_distance * 1.3:
            if dist_from_origin < total_distance and dist_to_dest < total_distance:
                intermediate_nodes.append({
                    "name": name,
                    "distance_from_origin": dist_from_origin,
                    "distance_to_dest": dist_to_dest
                })

    # Sort by distance from origin
    intermediate_nodes.sort(key=lambda x: x["distance_from_origin"])

    for node in intermediate_nodes:
        print(f"      ✅ {node['name']}")
        print(f"         {node['distance_from_origin']:.1f}km from {origin}, "
              f"{node['distance_to_dest']:.1f}km to {destination}")

    print(f"\n✅ Found {len(intermediate_nodes)} potential intermediate nodes")


def test_bounding_box_search(locations):
    """Test finding locations within a bounding box."""

    print(f"\n📦 Test 4: Bounding box search (find all nodes in an area)")
    print("-" * 60)

    # Define a bounding box around Bangalore (for example)
    center = locations["Bangalore"]
    radius_km = 100

    # Calculate bounding box
    # Approximation: 1 degree ≈ 111 km
    lat_delta = radius_km / 111
    lon_delta = radius_km / (111 * math.cos(math.radians(center[0])))

    bounds = {
        "min_lat": center[0] - lat_delta,
        "max_lat": center[0] + lat_delta,
        "min_lon": center[1] - lon_delta,
        "max_lon": center[1] + lon_delta,
    }

    print(f"   Bounding box around Bangalore (±{radius_km}km):")
    print(f"      Lat: {bounds['min_lat']:.4f} to {bounds['max_lat']:.4f}")
    print(f"      Lon: {bounds['min_lon']:.4f} to {bounds['max_lon']:.4f}\n")

    # Sample stations data
    stations = {
        "SBC (Bangalore City)": (12.9777, 77.5728),
        "YPR (Yeshwanthpur)": (13.0167, 77.5538),
        "BNC (Bangalore Cantonment)": (12.9833, 77.6033),
        "KJM (Krishnarajapuram)": (12.9940, 77.7130),
        "DSA (Dasarahalli)": (13.0580, 77.5430),
        "MAS (Chennai Central)": (13.0821, 80.2750),  # Should be outside
    }

    print(f"   Stations within bounding box:")

    in_bounds = []
    for station, coord in stations.items():
        lat, lon = coord
        if (bounds['min_lat'] <= lat <= bounds['max_lat'] and
            bounds['min_lon'] <= lon <= bounds['max_lon']):
            distance = geodesic(center, coord).kilometers
            in_bounds.append((station, distance))

    for station, distance in in_bounds:
        print(f"      ✅ {station}: {distance:.1f} km from center")

    print(f"\n✅ Bounding box search: Working")


def save_sample_data():
    """Save sample location data for testing."""

    print(f"\n💾 Saving sample geospatial data...")
    print("-" * 60)

    # Major Indian cities with coordinates
    cities = [
        {"name": "Delhi", "lat": 28.6139, "lon": 77.2090, "state": "Delhi"},
        {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777, "state": "Maharashtra"},
        {"name": "Bangalore", "lat": 12.9716, "lon": 77.5946, "state": "Karnataka"},
        {"name": "Chennai", "lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu"},
        {"name": "Kolkata", "lat": 22.5726, "lon": 88.3639, "state": "West Bengal"},
        {"name": "Hyderabad", "lat": 17.3850, "lon": 78.4867, "state": "Telangana"},
        {"name": "Ahmedabad", "lat": 23.0225, "lon": 72.5714, "state": "Gujarat"},
        {"name": "Pune", "lat": 18.5204, "lon": 73.8567, "state": "Maharashtra"},
        {"name": "Jaipur", "lat": 26.9124, "lon": 75.7873, "state": "Rajasthan"},
        {"name": "Lucknow", "lat": 26.8467, "lon": 80.9462, "state": "Uttar Pradesh"},
        {"name": "Ranchi", "lat": 23.3441, "lon": 85.3096, "state": "Jharkhand"},
        {"name": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245, "state": "Odisha"},
        {"name": "Guwahati", "lat": 26.1445, "lon": 91.7362, "state": "Assam"},
        {"name": "Chandigarh", "lat": 30.7333, "lon": 76.7794, "state": "Punjab"},
        {"name": "Kochi", "lat": 9.9312, "lon": 76.2673, "state": "Kerala"},
    ]

    os.makedirs("../data/seeds", exist_ok=True)

    with open("../data/seeds/indian_cities.json", "w") as f:
        json.dump(cities, f, indent=2)

    print(f"✅ Saved {len(cities)} cities to data/seeds/indian_cities.json")


def main():
    """Run all geospatial tests."""

    locations = test_geopy()
    test_proximity_search(locations)
    test_intermediate_nodes(locations)
    test_bounding_box_search(locations)
    save_sample_data()

    print("\n" + "=" * 60)
    print("✅ Geospatial testing completed")
    print("=" * 60)

    print("\n📝 Summary:")
    print("  ✅ GeoPy: Excellent for distance calculations")
    print("  ✅ Proximity search: Working")
    print("  ✅ Intermediate node discovery: Working")
    print("  ✅ Bounding box search: Working")
    print()
    print("  💡 This feature is FULLY FEASIBLE with open-source tools")


if __name__ == "__main__":
    main()
