"""Initialize database with seed data."""

import math

from app.database import init_db, SessionLocal, engine
from app.models import City, Station, Airport, TrainRoute, FlightRoute, BusRoute
from datetime import datetime, time


def seed_cities() -> None:
    """Seed top 50 Indian cities."""
    cities_data = [
        # Top metros
        ("Mumbai", "Maharashtra", "BOM", 19.0760, 72.8777, True),
        ("Delhi", "Delhi", "DEL", 28.7041, 77.1025, True),
        ("Bangalore", "Karnataka", "BLR", 12.9716, 77.5946, True),
        ("Hyderabad", "Telangana", "HYD", 17.3850, 78.4867, True),
        ("Chennai", "Tamil Nadu", "MAA", 13.0827, 80.2707, True),
        ("Kolkata", "West Bengal", "CCU", 22.5726, 88.3639, True),
        # Tier-2 cities
        ("Pune", "Maharashtra", "PNQ", 18.5204, 73.8567, True),
        ("Ahmedabad", "Gujarat", "AMD", 23.0225, 72.5714, True),
        ("Jaipur", "Rajasthan", "JAI", 26.9124, 75.7873, True),
        ("Surat", "Gujarat", None, 21.1702, 72.8311, True),
        ("Lucknow", "Uttar Pradesh", "LKO", 26.8467, 80.9462, True),
        ("Kanpur", "Uttar Pradesh", "KNU", 26.4499, 80.3319, True),
        ("Nagpur", "Maharashtra", "NAG", 21.1458, 79.0882, True),
        ("Indore", "Madhya Pradesh", "IDR", 22.7196, 75.8577, True),
        ("Thane", "Maharashtra", None, 19.2183, 72.9781, True),
        ("Bhopal", "Madhya Pradesh", "BHO", 23.2599, 77.4126, True),
        ("Visakhapatnam", "Andhra Pradesh", "VTZ", 17.6868, 83.2185, True),
        ("Pimpri-Chinchwad", "Maharashtra", None, 18.6298, 73.7997, True),
        ("Patna", "Bihar", "PAT", 25.5941, 85.1376, True),
        ("Vadodara", "Gujarat", "BDQ", 22.3107, 73.1924, True),
        ("Ghaziabad", "Uttar Pradesh", None, 28.6692, 77.4538, True),
        ("Ludhiana", "Punjab", "LUH", 30.9010, 75.8573, True),
        ("Agra", "Uttar Pradesh", "AGR", 27.1751, 78.0421, True),
        ("Nashik", "Maharashtra", "ISK", 19.9975, 73.7898, True),
        ("Ranchi", "Jharkhand", "IXR", 23.3441, 85.3096, True),
        ("Faridabad", "Haryana", None, 28.4089, 77.3178, True),
        ("Meerut", "Uttar Pradesh", None, 28.9845, 77.7064, True),
        ("Rajkot", "Gujarat", "RAJ", 22.3039, 70.8022, True),
        ("Varanasi", "Uttar Pradesh", "VNS", 25.3176, 82.9739, True),
        ("Srinagar", "Jammu & Kashmir", "SXR", 34.0837, 74.7973, True),
        ("Aurangabad", "Maharashtra", "IXU", 19.8762, 75.3433, True),
        ("Dhanbad", "Jharkhand", None, 23.7957, 86.4304, True),
        ("Amritsar", "Punjab", "ATQ", 31.6340, 74.8723, True),
        ("Navi Mumbai", "Maharashtra", None, 19.0330, 73.0297, True),
        ("Prayagraj", "Uttar Pradesh", "IXD", 25.4358, 81.8806, True),
        ("Howrah", "West Bengal", None, 22.5958, 88.2636, True),
        ("Jabalpur", "Madhya Pradesh", "JLR", 23.1815, 79.9864, True),
        ("Gwalior", "Madhya Pradesh", "GWL", 26.2124, 78.1772, True),
        ("Vijayawada", "Andhra Pradesh", "VGA", 16.5062, 80.6480, True),
        ("Jodhpur", "Rajasthan", "JDH", 26.2969, 73.0368, True),
        ("Madurai", "Tamil Nadu", "IXM", 9.9252, 78.1198, True),
        ("Raipur", "Chhattisgarh", "RPR", 21.2514, 81.6296, True),
        ("Kota", "Rajasthan", "KTU", 25.1386, 75.8361, True),
        ("Guwahati", "Assam", "GAU", 26.1480, 91.7333, True),
        ("Chandigarh", "Punjab", "IXC", 30.7333, 76.7794, True),
        ("Solapur", "Maharashtra", None, 17.6599, 75.9064, True),
        ("Hubballi", "Karnataka", "HBX", 15.3647, 75.1240, True),
        ("Mysore", "Karnataka", "MYQ", 12.2958, 76.6394, True),
        ("Tiruchirappalli", "Tamil Nadu", "TRZ", 10.7905, 78.7047, True),
        ("Bareilly", "Uttar Pradesh", None, 28.3670, 79.4304, True),
        ("Aligarh", "Uttar Pradesh", None, 27.8803, 78.0777, True),
        ("Tiruppur", "Tamil Nadu", None, 11.1085, 77.3411, True),
        ("Gurgaon", "Haryana", None, 28.4594, 77.0266, True),
        ("Bhubaneswar", "Odisha", "BBI", 20.2961, 85.8245, True),
        ("Kochi", "Kerala", "COK", 9.9312, 76.2673, True),
        ("Coimbatore", "Tamil Nadu", "CJB", 11.0168, 76.9558, True),
        ("Dehradun", "Uttarakhand", "DED", 30.3272, 78.0320, True),
        ("Nasik", "Maharashtra", None, 19.9722, 73.7895, True),
    ]

    db = SessionLocal()
    for name, state, code, lat, lon, is_top in cities_data:
        existing = db.query(City).filter(City.name == name).first()
        if not existing:
            city = City(
                name=name,
                state=state,
                code=code,
                latitude=lat,
                longitude=lon,
                is_top_city=is_top,
            )
            db.add(city)
    db.commit()
    print(f"✅ Seeded {len(cities_data)} cities")


def seed_stations() -> None:
    """Seed major railway stations with coordinates."""
    stations_data = [
        ("HWH", "Howrah Junction", "West Bengal", "ER", 22.5833, 88.3417),
        ("NDLS", "New Delhi", "Delhi", "NR", 28.6431, 77.2197),
        ("MAS", "Chennai Central", "Tamil Nadu", "SR", 13.0821, 80.2750),
        ("CSMT", "Mumbai CST", "Maharashtra", "CR", 18.9402, 72.8354),
        ("SBC", "Bangalore City Junction", "Karnataka", "SWR", 12.9777, 77.5728),
        ("HYB", "Hyderabad Deccan", "Telangana", "SCR", 17.3985, 78.4734),
        ("KOAA", "Kolkata", "West Bengal", "ER", 22.5630, 88.3426),
        ("JP", "Jaipur", "Rajasthan", "NWR", 26.9196, 75.7878),
        ("LKO", "Lucknow", "Uttar Pradesh", "NR", 26.8467, 80.9462),
        ("PNBE", "Patna Junction", "Bihar", "ECR", 25.6108, 85.1351),
        ("BPL", "Bhopal Junction", "Madhya Pradesh", "WCR", 23.2441, 77.3960),
        ("AGC", "Agra Cantt", "Uttar Pradesh", "NCR", 27.1581, 78.0041),
        ("CNB", "Kanpur Central", "Uttar Pradesh", "NR", 26.4499, 80.3511),
        ("BBS", "Bhubaneswar", "Odisha", "ECoR", 20.2926, 85.8110),
        ("TVC", "Thiruvananthapuram", "Kerala", "SR", 8.4821, 76.9201),
        ("ADI", "Ahmedabad Junction", "Gujarat", "WR", 23.0305, 72.5800),
        ("PUNE", "Pune Junction", "Maharashtra", "CR", 18.5288, 73.8749),
        ("NGP", "Nagpur", "Maharashtra", "CR", 21.1491, 79.0807),
        ("ALL", "Prayagraj Junction", "Uttar Pradesh", "NR", 25.4358, 81.8806),
        ("JAT", "Jammu Tawi", "Jammu & Kashmir", "NR", 32.7063, 74.8643),
        ("ASR", "Amritsar Junction", "Punjab", "NR", 31.6256, 74.8721),
        ("RNC", "Ranchi", "Jharkhand", "ECR", 23.3567, 85.3339),
        ("HPT", "Hospet Junction", "Karnataka", "SWR", 15.2784, 76.4033),
        ("UBL", "Hubballi Junction", "Karnataka", "SWR", 15.3647, 75.1240),
        ("CLT", "Kozhikode", "Kerala", "SR", 11.2479, 75.7803),
        ("ERS", "Ernakulam Junction", "Kerala", "SR", 9.9694, 76.3017),
        ("BZA", "Vijayawada Junction", "Andhra Pradesh", "SCR", 16.5115, 80.6310),
        ("SC", "Secunderabad Junction", "Telangana", "SCR", 17.4398, 78.4983),
        ("GHY", "Guwahati", "Assam", "NFR", 26.1860, 91.7436),
        ("CSTM", "Mumbai Central", "Maharashtra", "WR", 18.9667, 72.8443),
        ("BSB", "Banaras", "Uttar Pradesh", "NR", 25.3333, 83.0037),
        ("HJP", "Hajipur Junction", "Bihar", "ECR", 25.6855, 85.2125),
        ("DNR", "Danapur", "Bihar", "ECR", 25.6109, 85.0606),
        ("JES", "Junction", " Karnataka", "SWR", 12.9806, 77.5667),
    ]

    db = SessionLocal()
    city_map = {c.name: c.id for c in db.query(City).all()}

    for code, name, state, zone, lat, lon in stations_data:
        existing = db.query(Station).filter(Station.code == code).first()
        if not existing:
            # Find nearest city
            nearest_city_id = None
            min_distance = float('inf')
            for city_name, city_id in city_map.items():
                city = db.query(City).get(city_id)
                if city and city.latitude and city.longitude:
                    dist = _haversine(lat, lon, city.latitude, city.longitude)
                    if dist < min_distance:
                        min_distance = dist
                        nearest_city_id = city_id

            station = Station(
                code=code,
                name=name,
                state=state,
                zone=zone,
                latitude=lat,
                longitude=lon,
                nearest_city_id=nearest_city_id,
                distance_to_city_km=min_distance if min_distance != float('inf') else None
            )
            db.add(station)
    db.commit()
    print(f"✅ Seeded {len(stations_data)} stations")


def seed_airports() -> None:
    """Seed Indian airports with city links."""
    airports_data = [
        ("DEL", "VIDP", "Indira Gandhi International", "Delhi", "Delhi", 28.5562, 77.1000, True),
        ("BOM", "VABB", "Chhatrapati Shivaji International", "Mumbai", "Maharashtra", 19.0896, 72.8656, True),
        ("BLR", "VOBL", "Kempegowda International", "Bangalore", "Karnataka", 13.1986, 77.7066, True),
        ("MAA", "VOMM", "Chennai International", "Chennai", "Tamil Nadu", 12.9941, 80.1709, True),
        ("CCU", "VECC", "Netaji Subhash Chandra Bose", "Kolkata", "West Bengal", 22.6547, 88.4467, True),
        ("HYD", "VOHY", "Rajiv Gandhi International", "Hyderabad", "Telangana", 17.2403, 78.4294, True),
        ("COK", "VOCI", "Cochin International", "Kochi", "Kerala", 10.1520, 76.4019, True),
        ("AMD", "VAAH", "Sardar Vallabhbhai Patel", "Ahmedabad", "Gujarat", 23.0772, 72.6347, True),
        ("GOI", "VAGO", "Goa International", "Goa", "Goa", 15.3808, 73.8314, True),
        ("PNQ", "VAPO", "Pune Airport", "Pune", "Maharashtra", 18.5821, 73.9197, False),
        ("ATQ", "VIAR", "Sri Guru Ram Dass Jee", "Amritsar", "Punjab", 31.7096, 75.7018, True),
        ("TRV", "VOTV", "Trivandrum International", "Thiruvananthapuram", "Kerala", 8.4821, 76.9201, True),
        ("JAI", "VIJP", "Jaipur International", "Jaipur", "Rajasthan", 26.8242, 75.8122, True),
        ("LKO", "VILK", "Chaudhary Charan Singh", "Lucknow", "Uttar Pradesh", 26.7606, 80.8893, True),
        ("CJB", "VOCI", "Coimbatore International", "Coimbatore", "Tamil Nadu", 11.0306, 77.0412, False),
        ("IXR", "VERC", "Birsa Munda", "Ranchi", "Jharkhand", 23.3131, 85.3306, False),
        ("PAT", "VEPT", "Jay Prakash Narayan", "Patna", "Bihar", 25.5929, 85.0915, False),
        ("NAG", "VANP", "Dr. Babasaheb Ambedkar", "Nagpur", "Maharashtra", 21.0921, 79.0477, False),
        ("IXU", "VAHH", "Chikkalthana Airport", "Aurangabad", "Maharashtra", 19.8663, 75.3967, False),
        ("HBX", "VOHB", "Hubli Airport", "Hubli", "Karnataka", 15.3588, 75.0955, False),
        ("VGA", "VOBG", "Vijayawada Airport", "Vijayawada", "Andhra Pradesh", 16.5291, 80.8002, False),
        ("GAU", "VEGT", "Lokpriya Gopinath Bordoloi", "Guwahati", "Assam", 26.1061, 91.5859, True),
        ("JDH", "VIJH", "Jodhpur Airport", "Jodhpur", "Rajasthan", 26.2630, 73.0176, False),
        ("IXM", "VOMD", "Madurai Airport", "Madurai", "Tamil Nadu", 9.8344, 78.0932, False),
        ("TRZ", "VOTR", "Tiruchirappalli International", "Tiruchirappalli", "Tamil Nadu", 10.7647, 78.7089, False),
        ("IXC", "VICG", "Shaheed Bhagat Singh", "Chandigarh", "Punjab", 30.6813, 76.7994, False),
        ("BBI", "VEBT", "Biju Patnaik", "Bhubaneswar", "Odisha", 20.2436, 85.7693, True),
        ("DED", "VIDP", "Jolly Grant", "Dehradun", "Uttarakhand", 30.1893, 78.1696, False),
        ("IDR", "VAAO", "Devi Ahilyabai Holkar", "Indore", "Madhya Pradesh", 22.7271, 75.8018, False),
        ("VTZ", "VOSM", "Visakhapatnam", "Visakhapatnam", "Andhra Pradesh", 17.7239, 83.2256, False),
    ]

    db = SessionLocal()
    city_map = {c.name: c.id for c in db.query(City).all()}

    for iata, icao, name, city, state, lat, lon, intl in airports_data:
        existing = db.query(Airport).filter(Airport.iata_code == iata).first()
        if not existing:
            nearest_city_id = city_map.get(city)
            # Calculate distance to nearest city
            min_distance = 0
            if nearest_city_id:
                c = db.query(City).get(nearest_city_id)
                if c:
                    min_distance = _haversine(lat, lon, c.latitude, c.longitude)

            airport = Airport(
                iata_code=iata,
                icao_code=icao,
                name=name,
                city=city,
                state=state,
                latitude=lat,
                longitude=lon,
                is_international=intl,
                type="large" if intl else "medium",
                nearest_city_id=nearest_city_id,
                distance_to_city_km=min_distance
            )
            db.add(airport)
    db.commit()
    print(f"✅ Seeded {len(airports_data)} airports")


def seed_sample_routes() -> None:
    """Seed sample routes for testing."""
    db = SessionLocal()

    # Sample train routes
    train_routes = [
        # Rajdhani routes
        TrainRoute(
            train_no=12951,
            train_name="MUMBAI RAJDHANI",
            from_station_code="CSMT",
            to_station_code="NDLS",
            departure_time=time(17, 0),
            arrival_time=time(8, 45),
            duration_minutes=945,
            distance_km=1386,
            days_run="Daily",
            pricing={"1A": 2500, "2A": 1800, "3A": 1200, "SL": 500},
            on_time_percentage=85.0,
            classes="1A,2A,3A,SL",
            source="data.gov.in"
        ),
        TrainRoute(
            train_no=12301,
            train_name="RAJDHANI EXP",
            from_station_code="HWH",
            to_station_code="NDLS",
            departure_time=time(14, 5),
            arrival_time=time(9, 55),
            duration_minutes=1190,
            distance_km=1441,
            days_run="Daily",
            pricing={"1A": 2800, "2A": 2000, "3A": 1400, "SL": 600},
            on_time_percentage=82.0,
            classes="1A,2A,3A,SL",
            source="data.gov.in"
        ),
        TrainRoute(
            train_no=12627,
            train_name="KARNATAKA EXP",
            from_station_code="SBC",
            to_station_code="MAS",
            departure_time=time(20, 30),
            arrival_time=time(5, 10),
            duration_minutes=520,
            distance_km=350,
            days_run="Daily",
            pricing={"2S": 120, "3A": 500, "SL": 180},
            on_time_percentage=78.0,
            classes="2S,3A,SL",
            source="data.gov.in"
        ),
    ]

    # Sample flight routes
    flight_routes = [
        FlightRoute(
            flight_no="6E2341",
            airline="IndiGo",
            airline_code="6E",
            from_airport_code="DEL",
            to_airport_code="BOM",
            departure_time=time(6, 0),
            arrival_time=time(8, 15),
            duration_minutes=135,
            days_run="Daily",
            price_min=3500,
            price_avg=4500,
            price_max=7500,
            price_trends={"low": [3500, 4000], "medium": [4000, 6000], "high": [6000, 7500]},
            on_time_percentage=90.0,
            aircraft_type="A320neo",
            source="ixigo"
        ),
        FlightRoute(
            flight_no="UK951",
            airline="Vistara",
            airline_code="UK",
            from_airport_code="BOM",
            to_airport_code="BLR",
            departure_time=time(9, 30),
            arrival_time=time(11, 45),
            duration_minutes=135,
            days_run="Daily",
            price_min=4000,
            price_avg=5500,
            price_max=8500,
            on_time_percentage=88.0,
            aircraft_type="A320",
            source="ixigo"
        ),
        FlightRoute(
            flight_no="SG8171",
            airline="SpiceJet",
            airline_code="SG",
            from_airport_code="DEL",
            to_airport_code="HYD",
            departure_time=time(14, 0),
            arrival_time=time(16, 15),
            duration_minutes=135,
            days_run="Daily",
            price_min=3800,
            price_avg=5000,
            price_max=7000,
            on_time_percentage=85.0,
            aircraft_type="B737-800",
            source="ixigo"
        ),
    ]

    # Sample bus routes
    bus_routes = [
        BusRoute(
            operator="KSRTC",
            operator_id="ksrtc-001",
            from_city_id="123",
            from_city="Bangalore",
            to_city_id="141",
            to_city="Coimbatore",
            departure_time=time(22, 0),
            arrival_time=time(5, 0),
            duration_minutes=420,
            bus_type="A/C Semi-Sleeper",
            price_min=600,
            price_avg=800,
            price_max=1200,
            rating=4.2,
            total_ratings=1520,
            fare_tiers={"seater": 600, "sleeper": 1000},
            amenities=["wifi", "water", "charging"],
            source="redbus"
        ),
        BusRoute(
            operator="HRTC",
            operator_id="hrtc-002",
            from_city_id="74676",
            from_city="Bhubaneswar",
            to_city_id="123",
            to_city="Kolkata",
            departure_time=time(20, 30),
            arrival_time=time(6, 0),
            duration_minutes=570,
            bus_type="A/C Sleeper",
            price_min=700,
            price_avg=950,
            price_max=1400,
            rating=3.9,
            total_ratings=850,
            fare_tiers={"seater": 700, "sleeper": 1200},
            amenities=["water", "blanket"],
            source="redbus"
        ),
    ]

    for route in train_routes:
        existing = db.query(TrainRoute).filter(
            TrainRoute.train_no == route.train_no,
            TrainRoute.from_station_code == route.from_station_code
        ).first()
        if not existing:
            db.add(route)

    for route in flight_routes:
        existing = db.query(FlightRoute).filter(
            FlightRoute.flight_no == route.flight_no,
            FlightRoute.from_airport_code == route.from_airport_code
        ).first()
        if not existing:
            db.add(route)

    for route in bus_routes:
        existing = db.query(BusRoute).filter(
            BusRoute.operator == route.operator,
            BusRoute.from_city == route.from_city
        ).first()
        if not existing:
            db.add(route)

    db.commit()
    print(f"✅ Seeded sample routes: {len(train_routes)} trains, {len(flight_routes)} flights, {len(bus_routes)} buses")


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points using Haversine formula."""
    R = 6371  # Earth's radius in km
    lat1_rad, lon1_rad = math.radians(lat1), math.radians(lon1)
    lat2_rad, lon2_rad = math.radians(lat2), math.radians(lon2)
    dlat, dlon = lat2_rad - lat1_rad, lon2_rad - lon1_rad
    a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def main() -> None:
    """Initialize database with all seed data."""
    import math

    print("=" * 60)
    print("Initializing Travel Planner Database")
    print("=" * 60)

    # Create all tables
    init_db()
    print("✅ Created database tables")

    # Seed data
    seed_cities()
    seed_stations()
    seed_airports()
    seed_sample_routes()

    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
