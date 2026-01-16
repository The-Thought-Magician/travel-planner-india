"""Initialize database with seed data."""

from app.database import init_db, SessionLocal
from app.models import City, Station, Airport


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
        ("Allahabad", "Uttar Pradesh", "IXD", 25.4358, 81.8806, True),
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
        # Special case - Hampi (popular destination)
        ("Hampi", "Karnataka", None, 15.3350, 76.4600, True),
        # Nearby city to Hampi with transport
        ("Hospet", "Karnataka", None, 15.2737, 76.3830, True),
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
    print(f"Seeded {len(cities_data)} cities")


def seed_stations() -> None:
    """Seed major railway stations."""
    stations_data = [
        ("HWH", "Howrah Junction", "West Bengal", "ER"),
        ("NDLS", "New Delhi", "Delhi", "NR"),
        ("MAS", "Chennai Central", "Tamil Nadu", "SR"),
        ("CSMT", "Mumbai CST", "Maharashtra", "CR"),
        ("SBC", "Bangalore City Junction", "Karnataka", "SWR"),
        ("HYB", "Hyderabad Deccan", "Telangana", "SCR"),
        ("KOAA", "Kolkata", "West Bengal", "ER"),
        ("JP", "Jaipur", "Rajasthan", "NWR"),
        ("LKO", "Lucknow", "Uttar Pradesh", "NR"),
        ("PNBE", "Patna Junction", "Bihar", "ECR"),
        ("BPL", "Bhopal Junction", "Madhya Pradesh", "WCR"),
        ("AGC", "Agra Cantt", "Uttar Pradesh", "NCR"),
        ("CNB", "Kanpur Central", "Uttar Pradesh", "NR"),
        ("BBS", "Bhubaneswar", "Odisha", "ECoR"),
        ("TVC", "Thiruvananthapuram", "Kerala", "SR"),
        ("ADI", "Ahmedabad Junction", "Gujarat", "WR"),
        ("PUNE", "Pune Junction", "Maharashtra", "CR"),
        ("NGP", "Nagpur", "Maharashtra", "CR"),
        ("ALL", "Allahabad Junction", "Uttar Pradesh", "NR"),
        ("JAT", "Jammu Tawi", "Jammu & Kashmir", "NR"),
        ("ASR", "Amritsar Junction", "Punjab", "NR"),
        ("RNC", "Ranchi", "Jharkhand", "ECR"),
        ("HPT", "Hospet Junction", "Karnataka", "SWR"),
        ("UBL", "Hubballi Junction", "Karnataka", "SWR"),
        ("CLT", "Kozhikode", "Kerala", "SR"),
        ("ERS", "Ernakulam Junction", "Kerala", "SR"),
        ("BZA", "Vijayawada Junction", "Andhra Pradesh", "SCR"),
        ("SC", "Secunderabad Junction", "Telangana", "SCR"),
        ("GHY", "Guwahati", "Assam", "NFR"),
    ]

    db = SessionLocal()
    for code, name, state, zone in stations_data:
        existing = db.query(Station).filter(Station.code == code).first()
        if not existing:
            station = Station(code=code, name=name, state=state, zone=zone)
            db.add(station)
    db.commit()
    print(f"Seeded {len(stations_data)} stations")


def seed_airports() -> None:
    """Seed Indian airports."""
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
    ]

    db = SessionLocal()
    for iata, icao, name, city, state, lat, lon, intl in airports_data:
        existing = db.query(Airport).filter(Airport.iata_code == iata).first()
        if not existing:
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
            )
            db.add(airport)
    db.commit()
    print(f"Seeded {len(airports_data)} airports")


def main() -> None:
    """Initialize database with all seed data."""
    init_db()
    seed_cities()
    seed_stations()
    seed_airports()
    print("Database initialization complete!")


if __name__ == "__main__":
    main()
