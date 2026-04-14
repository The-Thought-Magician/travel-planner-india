"""Initialize database with seed data."""

import json
import math
from pathlib import Path

from app.database import init_db, SessionLocal, engine
from app.models import City, Station, Airport, TrainRoute, FlightRoute, BusRoute, TransferTime
from datetime import datetime, time

SEEDS_DIR = Path(__file__).resolve().parent.parent / "data" / "seeds"


def _load_seed(name: str) -> list:
    path = SEEDS_DIR / name
    if not path.exists():
        return []
    return json.loads(path.read_text())


def _parse_hhmm(s: str) -> time:
    h, m = s.split(":")
    return time(int(h), int(m))


def seed_cities() -> None:
    """Seed comprehensive list of Indian cities - all districts and major towns."""

    cities_data = []

    # ANDHRA PRADESH
    cities_data.extend([
        ("Hyderabad", "Telangana", "HYD", 17.3850, 78.4867, True),
        ("Visakhapatnam", "Andhra Pradesh", "VTZ", 17.6868, 83.2185, True),
        ("Vijayawada", "Andhra Pradesh", "VGA", 16.5062, 80.6480, True),
        ("Guntur", "Andhra Pradesh", None, 16.3067, 80.4365, True),
        ("Nellore", "Andhra Pradesh", None, 14.4429, 79.9864, True),
        ("Kurnool", "Andhra Pradesh", None, 15.8281, 78.0373, True),
        ("Rajahmundry", "Andhra Pradesh", None, 17.0005, 81.8044, True),
        ("Tirupati", "Andhra Pradesh", "TIR", 13.6288, 79.4191, True),
        ("Kadapa", "Andhra Pradesh", None, 14.4715, 78.8232, True),
        ("Kakinada", "Andhra Pradesh", None, 16.9893, 82.2475, True),
        ("Anantapur", "Andhra Pradesh", None, 14.6798, 77.5999, True),
        ("Vizianagaram", "Andhra Pradesh", None, 18.1167, 83.4167, True),
        ("Eluru", "Andhra Pradesh", None, 16.7102, 81.1055, True),
        ("Ongole", "Andhra Pradesh", None, 15.5055, 80.0494, True),
        ("Nandyala", "Andhra Pradesh", None, 15.4876, 78.4841, True),
        ("Machilipatnam", "Andhra Pradesh", None, 16.1871, 81.1333, True),
        ("Tenali", "Andhra Pradesh", None, 16.2383, 80.5809, True),
        ("Chittoor", "Andhra Pradesh", None, 13.2172, 79.1005, True),
        ("Khammam", "Telangana", None, 17.2473, 80.1514, True),
        ("Ramagundam", "Telangana", None, 18.7519, 79.4471, True),
    ])

    # ARUNACHAL PRADESH
    cities_data.extend([
        ("Itanagar", "Arunachal Pradesh", None, 26.9846, 93.6175, True),
        ("Naharlagun", "Arunachal Pradesh", None, 26.9896, 93.7076, True),
        ("Pasighat", "Arunachal Pradesh", None, 28.0667, 95.3333, True),
        ("Tezpur", "Assam", "TEZ", 26.6281, 92.7958, True),
        ("Bomdila", "Arunachal Pradesh", None, 27.2517, 92.4087, True),
        ("Tawang", "Arunachal Pradesh", None, 27.5833, 91.8667, True),
    ])

    # ASSAM
    cities_data.extend([
        ("Guwahati", "Assam", "GAU", 26.1480, 91.7333, True),
        ("Silchar", "Assam", None, 24.8317, 92.7782, True),
        ("Dibrugarh", "Assam", "DIB", 27.4833, 94.9064, True),
        ("Jorhat", "Assam", "JRH", 26.7541, 94.2016, True),
        ("Nagaon", "Assam", None, 26.3473, 92.6835, True),
        ("Tinsukia", "Assam", None, 27.4935, 95.3622, True),
        ("Tezpur", "Assam", "TEZ", 26.6281, 92.7958, True),
        ("Bongaigaon", "Assam", None, 26.4748, 90.5494, True),
        ("Karimganj", "Assam", None, 24.8667, 92.3500, True),
        ("Sivasagar", "Assam", None, 26.9833, 94.6333, True),
        ("Lakhimpur", "Assam", None, 27.2333, 94.1000, True),
        ("Dhubri", "Assam", None, 26.0235, 89.9777, True),
    ])

    # BIHAR
    cities_data.extend([
        ("Patna", "Bihar", "PAT", 25.5941, 85.1376, True),
        ("Gaya", "Bihar", "GAY", 24.7914, 85.0002, True),
        ("Bhagalpur", "Bihar", None, 25.2427, 86.9426, True),
        ("Muzaffarpur", "Bihar", None, 26.1225, 85.3910, True),
        ("Purnia", "Bihar", None, 25.7778, 87.4757, True),
        ("Darbhanga", "Bihar", "DBR", 26.1619, 85.8899, True),
        ("Arrah", "Bihar", None, 25.5567, 84.6643, True),
        ("Begusarai", "Bihar", None, 25.4167, 86.1250, True),
        ("Katihar", "Bihar", None, 25.5392, 87.5801, True),
        ("Munger", "Bihar", None, 25.3756, 86.4731, True),
        ("Chhapra", "Bihar", None, 25.7833, 84.7278, True),
        ("Danapur", "Bihar", None, 25.6109, 85.0606, True),
        ("Buxar", "Bihar", None, 25.5670, 83.9755, True),
        ("Sasaram", "Bihar", None, 24.9486, 84.0177, True),
        ("Dehri", "Bihar", None, 24.8667, 84.1833, True),
        ("Motihari", "Bihar", None, 26.6504, 84.9120, True),
        ("Bettiah", "Bihar", None, 26.8017, 84.5024, True),
        ("Jamui", "Bihar", None, 24.9167, 86.2167, True),
        (" Jehanabad", "Bihar", None, 25.2167, 85.2000, True),
        ("Aurangabad", "Bihar", None, 24.7500, 84.3667, True),
    ])

    # CHHATTISGARH
    cities_data.extend([
        ("Raipur", "Chhattisgarh", "RPR", 21.2514, 81.6296, True),
        ("Bilaspur", "Chhattisgarh", None, 22.0797, 82.1582, True),
        ("Durg", "Chhattisgarh", None, 21.1906, 81.2841, True),
        ("Rajnandgaon", "Chhattisgarh", None, 21.1012, 81.0281, True),
        ("Korba", "Chhattisgarh", None, 22.3510, 82.6819, True),
        ("Jagdalpur", "Chhattisgarh", None, 19.0756, 82.0389, True),
        ("Raigarh", "Chhattisgarh", None, 21.8917, 83.3917, True),
        ("Ambikapur", "Chhattisgarh", None, 23.1257, 83.1866, True),
        ("Mahasamund", "Chhattisgarh", None, 21.1167, 82.0833, True),
        ("Dhamtari", "Chhattisgarh", None, 20.7167, 81.5500, True),
        ("Chirmiri", "Chhattisgarh", None, 23.1833, 82.1167, True),
        ("Bhatapara", "Chhattisgarh", None, 21.7333, 82.2833, True),
    ])

    # GOA
    cities_data.extend([
        ("Panaji", "Goa", "GOI", 15.4909, 73.8278, True),
        ("Margao", "Goa", None, 15.2993, 73.9058, True),
        ("Vasco da Gama", "Goa", None, 15.3957, 73.8381, True),
        ("Mapusa", "Goa", None, 15.6002, 73.8237, True),
        ("Ponda", "Goa", None, 15.4033, 73.9905, True),
    ])

    # GUJARAT
    cities_data.extend([
        ("Ahmedabad", "Gujarat", "AMD", 23.0225, 72.5714, True),
        ("Surat", "Gujarat", None, 21.1702, 72.8311, True),
        ("Vadodara", "Gujarat", "BDQ", 22.3107, 73.1924, True),
        ("Rajkot", "Gujarat", "RAJ", 22.3039, 70.8022, True),
        ("Bhavnagar", "Gujarat", "BHU", 21.7643, 72.1517, True),
        ("Jamnagar", "Gujarat", "JGA", 22.4707, 70.0577, True),
        ("Junagadh", "Gujarat", None, 21.5216, 70.4548, True),
        ("Gandhinagar", "Gujarat", None, 23.1251, 72.6371, True),
        ("Anand", "Gujarat", None, 22.5550, 72.9339, True),
        ("Bharuch", "Gujarat", None, 21.7072, 72.9963, True),
        ("Porbandar", "Gujarat", "PBD", 21.6495, 69.6077, True),
        ("Bhuj", "Gujarat", "BHJ", 23.2599, 69.6703, True),
        ("Surendranagar", "Gujarat", None, 22.5996, 71.6559, True),
        ("Dwarka", "Gujarat", None, 22.2376, 68.9678, True),
        ("Navsari", "Gujarat", None, 20.9469, 72.9239, True),
        ("Veraval", "Gujarat", None, 20.9137, 70.3689, True),
        ("Godhra", "Gujarat", None, 22.7818, 73.6036, True),
        ("Palanpur", "Gujarat", None, 24.1750, 72.4333, True),
        ("Morbi", "Gujarat", None, 22.8167, 71.8667, True),
        ("Mehsana", "Gujarat", None, 23.5876, 72.3789, True),
        ("Valsad", "Gujarat", None, 20.6094, 72.9339, True),
        ("Nadiad", "Gujarat", None, 22.6894, 72.8567, True),
    ])

    # HARYANA
    cities_data.extend([
        ("Faridabad", "Haryana", None, 28.4089, 77.3178, True),
        ("Gurgaon", "Haryana", None, 28.4594, 77.0266, True),
        ("Panipat", "Haryana", None, 29.3892, 76.9695, True),
        ("Ambala", "Haryana", None, 30.3752, 76.7820, True),
        ("Karnal", "Haryana", None, 29.6856, 76.9895, True),
        ("Sonipat", "Haryana", None, 28.9818, 77.0185, True),
        ("Yamunanagar", "Haryana", None, 30.1336, 77.2835, True),
        ("Rohtak", "Haryana", None, 28.8918, 76.6066, True),
        ("Hisar", "Haryana", "HSS", 29.1492, 75.7217, True),
        ("Bhiwani", "Haryana", None, 28.7833, 76.1333, True),
        ("Kurukshetra", "Haryana", None, 29.9684, 76.8782, True),
        ("Sirsa", "Haryana", None, 29.5405, 75.0264, True),
        ("Panvel", "Haryana", None, 28.6267, 77.2167, True),
        ("Jind", "Haryana", None, 29.3167, 76.3167, True),
    ])

    # HIMACHAL PRADESH
    cities_data.extend([
        ("Shimla", "Himachal Pradesh", None, 31.1048, 77.1734, True),
        ("Dharamshala", "Himachal Pradesh", "DHM", 32.2204, 76.3207, True),
        ("Manali", "Himachal Pradesh", None, 32.2435, 77.1882, True),
        ("Mandi", "Himachal Pradesh", None, 31.7066, 76.9178, True),
        ("Solan", "Himachal Pradesh", None, 30.9056, 77.1003, True),
        ("Hamirpur", "Himachal Pradesh", None, 31.6833, 76.5167, True),
        ("Una", "Himachal Pradesh", None, 31.4667, 76.2833, True),
        ("Bilaspur", "Himachal Pradesh", None, 31.3533, 76.7500, True),
        ("Kullu", "Himachal Pradesh", "KUU", 31.9555, 77.1039, True),
        ("Chamba", "Himachal Pradesh", None, 32.5500, 76.1167, True),
        ("Kangra", "Himachal Pradesh", None, 32.0833, 76.2667, True),
        ("Palampur", "Himachal Pradesh", None, 32.1104, 76.5336, True),
        ("Nahan", "Himachal Pradesh", None, 30.5500, 77.2833, True),
        ("Mcleodganj", "Himachal Pradesh", None, 32.2399, 76.3363, True),
    ])

    # JHARKHAND
    cities_data.extend([
        ("Ranchi", "Jharkhand", "IXR", 23.3441, 85.3096, True),
        ("Jamshedpur", "Jharkhand", "IXW", 22.8046, 86.2029, True),
        ("Dhanbad", "Jharkhand", None, 23.7957, 86.4304, True),
        ("Bokaro", "Jharkhand", None, 23.6667, 85.9167, True),
        ("Deoghar", "Jharkhand", "DGH", 24.4833, 86.7000, True),
        ("Hazaribagh", "Jharkhand", None, 23.9833, 85.3667, True),
        ("Giridih", "Jharkhand", None, 24.1833, 86.3000, True),
        ("Dumka", "Jharkhand", None, 24.2667, 87.2500, True),
        ("Chaibasa", "Jharkhand", None, 22.4667, 85.5000, True),
        ("Ramgarh", "Jharkhand", None, 23.3833, 85.5167, True),
        ("Jamtara", "Jharkhand", None, 23.9500, 86.8000, True),
        ("Godda", "Jharkhand", None, 24.9833, 87.2167, True),
        ("Sahebganj", "Jharkhand", None, 25.2500, 87.8500, True),
        ("Medininagar", "Jharkhand", None, 23.6167, 84.4500, True),
    ])

    # KARNATAKA
    cities_data.extend([
        ("Bangalore", "Karnataka", "BLR", 12.9716, 77.5946, True),
        ("Mysore", "Karnataka", "MYQ", 12.2958, 76.6394, True),
        ("Hubli", "Karnataka", "HBX", 15.3647, 75.1240, True),
        ("Mangalore", "Karnataka", "IXE", 12.9141, 74.8560, True),
        ("Belgaum", "Karnataka", "IXG", 15.8587, 74.5119, True),
        ("Gulbarga", "Karnataka", "GBI", 17.3289, 76.8344, True),
        ("Davanagere", "Karnataka", None, 14.4667, 75.9167, True),
        ("Bellary", "Karnataka", None, 15.1467, 76.9167, True),
        ("Vijayapura", "Karnataka", None, 16.8333, 75.7167, True),
        ("Shimoga", "Karnataka", None, 13.9333, 75.5667, True),
        ("Tumkur", "Karnataka", None, 13.3393, 77.1130, True),
        ("Raichur", "Karnataka", None, 16.2076, 77.3463, True),
        ("Bidar", "Karnataka", None, 17.9167, 77.5167, True),
        ("Hassan", "Karnataka", None, 13.0067, 76.1000, True),
        ("Mandya", "Karnataka", None, 12.5417, 76.8956, True),
        ("Chikmagalur", "Karnataka", None, 13.3167, 75.7667, True),
        ("Udupi", "Karnataka", None, 13.3409, 74.7438, True),
        ("Dakshina Kannada", "Karnataka", None, 12.9141, 74.8560, True),
        ("Chitradurga", "Karnataka", None, 14.2167, 76.4500, True),
        ("Kolar", "Karnataka", None, 13.1333, 78.1333, True),
    ])

    # KERALA
    cities_data.extend([
        ("Thiruvananthapuram", "Kerala", "TRV", 8.4821, 76.9201, True),
        ("Kochi", "Kerala", "COK", 9.9312, 76.2673, True),
        ("Kozhikode", "Kerala", "CCJ", 11.2479, 75.7803, True),
        ("Thrissur", "Kerala", None, 10.5276, 76.2144, True),
        ("Kollam", "Kerala", None, 8.8932, 76.6141, True),
        ("Palakkad", "Kerala", None, 10.7867, 76.6548, True),
        ("Alappuzha", "Kerala", None, 9.4981, 76.3388, True),
        ("Malappuram", "Kerala", None, 11.0628, 76.0690, True),
        ("Kannur", "Kerala", "CNN", 11.8745, 75.3704, True),
        ("Kasaragod", "Kerala", None, 12.4995, 75.0056, True),
        ("Kottayam", "Kerala", None, 9.5916, 76.5217, True),
        ("Idukki", "Kerala", None, 9.9289, 76.9337, True),
        ("Pathanamthitta", "Kerala", None, 9.2667, 76.7833, True),
        ("Wayanad", "Kerala", None, 11.6833, 76.0167, True),
        ("Varkala", "Kerala", None, 8.7333, 76.7000, True),
        ("Munnar", "Kerala", None, 10.0833, 77.0667, True),
    ])

    # MADHYA PRADESH
    cities_data.extend([
        ("Indore", "Madhya Pradesh", "IDR", 22.7196, 75.8577, True),
        ("Bhopal", "Madhya Pradesh", "BHO", 23.2599, 77.4126, True),
        ("Jabalpur", "Madhya Pradesh", "JLR", 23.1815, 79.9864, True),
        ("Gwalior", "Madhya Pradesh", "GWL", 26.2124, 78.1772, True),
        ("Ujjain", "Madhya Pradesh", "UJN", 23.1769, 75.7885, True),
        ("Sagar", "Madhya Pradesh", None, 23.8508, 78.7621, True),
        ("Dewas", "Madhya Pradesh", None, 22.9671, 76.0650, True),
        ("Satna", "Madhya Pradesh", None, 24.5833, 80.8333, True),
        ("Ratlam", "Madhya Pradesh", None, 23.3306, 75.0367, True),
        ("Rewa", "Madhya Pradesh", "REW", 24.5333, 81.3000, True),
        ("Murwara", "Madhya Pradesh", None, 23.8500, 79.9833, True),
        ("Singrauli", "Madhya Pradesh", None, 24.1986, 82.6662, True),
        ("Burhanpur", "Madhya Pradesh", None, 21.3167, 76.2500, True),
        ("Khandwa", "Madhya Pradesh", None, 21.8333, 76.3500, True),
        ("Chhindwara", "Madhya Pradesh", None, 22.0570, 78.9354, True),
        ("Guna", "Madhya Pradesh", None, 24.6500, 77.3167, True),
        ("Shivpuri", "Madhya Pradesh", None, 25.4167, 77.6500, True),
        ("Vidisha", "Madhya Pradesh", None, 23.5333, 77.8000, True),
        ("Morena", "Madhya Pradesh", None, 26.5000, 78.0000, True),
        ("Khargone", "Madhya Pradesh", None, 21.8333, 75.6000, True),
        ("Mandsaur", "Madhya Pradesh", None, 24.0667, 75.0667, True),
        ("Neemuch", "Madhya Pradesh", None, 24.4667, 74.8500, True),
        ("Hoshangabad", "Madhya Pradesh", None, 22.7500, 77.7167, True),
        ("Itarsi", "Madhya Pradesh", None, 22.6167, 77.7667, True),
        ("Sehore", "Madhya Pradesh", None, 23.2000, 77.0667, True),
    ])

    # MAHARASHTRA
    cities_data.extend([
        ("Mumbai", "Maharashtra", "BOM", 19.0760, 72.8777, True),
        ("Pune", "Maharashtra", "PNQ", 18.5204, 73.8567, True),
        ("Nagpur", "Maharashtra", "NAG", 21.1458, 79.0882, True),
        ("Thane", "Maharashtra", None, 19.2183, 72.9781, True),
        ("Pimpri-Chinchwad", "Maharashtra", None, 18.6298, 73.7997, True),
        ("Nashik", "Maharashtra", "ISK", 19.9975, 73.7898, True),
        ("Kalyan-Dombivli", "Maharashtra", None, 19.2367, 73.1305, True),
        ("Vasai-Virar", "Maharashtra", None, 19.4912, 72.8399, True),
        ("Aurangabad", "Maharashtra", "IXU", 19.8762, 75.3433, True),
        ("Navi Mumbai", "Maharashtra", None, 19.0330, 73.0297, True),
        ("Solapur", "Maharashtra", None, 17.6599, 75.9064, True),
        ("Kolhapur", "Maharashtra", "KLH", 16.7025, 74.2376, True),
        ("Amravati", "Maharashtra", None, 20.9333, 77.7500, True),
        ("Sangli-Miraj", "Maharashtra", None, 16.8500, 74.5833, True),
        ("Malegaon", "Maharashtra", None, 20.5500, 74.5000, True),
        ("Jalgaon", "Maharashtra", None, 21.0076, 75.5627, True),
        ("Latur", "Maharashtra", None, 18.4015, 76.5615, True),
        ("Akola", "Maharashtra", None, 20.7000, 77.0083, True),
        ("Nanded", "Maharashtra", "NDC", 19.1333, 77.3167, True),
        ("Dhule", "Maharashtra", None, 20.8800, 74.4667, True),
        ("Ahmednagar", "Maharashtra", "AMN", 19.0833, 74.7333, True),
        ("Chandrapur", "Maharashtra", None, 19.9667, 79.3000, True),
        ("Parbhani", "Maharashtra", None, 19.2667, 76.7833, True),
        ("Bhusawal", "Maharashtra", None, 21.0500, 76.0500, True),
        ("Jalna", "Maharashtra", None, 19.8500, 75.8833, True),
        ("Satara", "Maharashtra", None, 17.6800, 73.9833, True),
        ("Ratnagiri", "Maharashtra", None, 17.3000, 73.2000, True),
        ("Bhiwandi", "Maharashtra", None, 19.2933, 73.0667, True),
        ("Ulhasnagar", "Maharashtra", None, 19.2167, 73.1500, True),
        ("Aurangabad", "Maharashtra", None, 19.8762, 75.3433, True),
        ("Kalyan", "Maharashtra", None, 19.2367, 73.1305, True),
        ("Ambejogai", "Maharashtra", None, 18.7167, 76.5667, True),
        ("Yavatmal", "Maharashtra", None, 20.3833, 78.1333, True),
    ])

    # MANIPUR
    cities_data.extend([
        ("Imphal", "Manipur", "IMF", 24.8170, 93.9368, True),
        ("Thoubal", "Manipur", None, 24.6167, 94.0167, True),
        ("Bishnupur", "Manipur", None, 24.6167, 93.8167, True),
        ("Churachandpur", "Manipur", None, 24.3333, 93.7000, True),
        ("Ukhrul", "Manipur", None, 25.1167, 94.3667, True),
    ])

    # MEGHALAYA
    cities_data.extend([
        ("Shillong", "Meghalaya", "SHL", 25.5788, 91.8827, True),
        ("Tura", "Meghalaya", None, 25.5167, 90.2167, True),
        ("Cherrapunji", "Meghalaya", None, 25.2833, 91.7000, True),
        ("Jowai", "Meghalaya", None, 25.4500, 92.0333, True),
        ("Baghmara", "Meghalaya", None, 25.1167, 90.6167, True),
    ])

    # MIZORAM
    cities_data.extend([
        ("Aizawl", "Mizoram", "AJL", 23.7271, 92.7176, True),
        ("Lunglei", "Mizoram", None, 22.8833, 92.7500, True),
        ("Saiha", "Mizoram", None, 22.4833, 92.9667, True),
        ("Champhai", "Mizoram", None, 23.3500, 93.3167, True),
        ("Kolasib", "Mizoram", None, 24.2333, 92.6833, True),
    ])

    # NAGALAND
    cities_data.extend([
        ("Kohima", "Nagaland", None, 25.6744, 94.1096, True),
        ("Dimapur", "Nagaland", "DMU", 25.9126, 93.7300, True),
        ("Mokokchung", "Nagaland", None, 26.3167, 94.5167, True),
        ("Tuensang", "Nagaland", None, 26.2500, 94.8333, True),
        ("Wokha", "Nagaland", None, 26.1000, 94.3667, True),
        ("Zunheboto", "Nagaland", None, 25.9667, 94.5500, True),
    ])

    # ODISHA
    cities_data.extend([
        ("Bhubaneswar", "Odisha", "BBI", 20.2961, 85.8245, True),
        ("Cuttack", "Odisha", None, 20.4614, 85.8830, True),
        ("Rourkela", "Odisha", None, 22.2593, 84.8834, True),
        ("Berhampur", "Odisha", None, 19.3057, 84.7865, True),
        ("Sambalpur", "Odisha", None, 21.4667, 83.9833, True),
        ("Puri", "Odisha", None, 19.8135, 85.8312, True),
        ("Jharsuguda", "Odisha", "JRG", 21.8667, 84.0333, True),
        ("Cuttack", "Odisha", None, 20.4614, 85.8830, True),
        ("Baripada", "Odisha", None, 21.9367, 86.7167, True),
        ("Balasore", "Odisha", None, 21.4931, 86.9353, True),
        ("Bhadrak", "Odisha", None, 21.0667, 86.5167, True),
        ("Angul", "Odisha", None, 20.8500, 85.1167, True),
        ("Dhenkanal", "Odisha", None, 20.9500, 85.6000, True),
        ("Gunupur", "Odisha", None, 19.5833, 83.8167, True),
        ("Jeypore", "Odisha", None, 18.8500, 82.5667, True),
        ("Kendujhar", "Odisha", None, 21.6333, 85.5833, True),
        ("Koraput", "Odisha", None, 18.8000, 82.7000, True),
        ("Phulbani", "Odisha", None, 20.4667, 84.2333, True),
        ("Rayagada", "Odisha", None, 19.1667, 83.4167, True),
        ("Rourkela", "Odisha", None, 22.2593, 84.8834, True),
    ])

    # PUNJAB
    cities_data.extend([
        ("Ludhiana", "Punjab", "LUH", 30.9010, 75.8573, True),
        ("Amritsar", "Punjab", "ATQ", 31.6340, 74.8723, True),
        ("Jalandhar", "Punjab", None, 31.3260, 75.5762, True),
        ("Patiala", "Punjab", None, 30.3398, 76.3869, True),
        ("Bathinda", "Punjab", None, 30.2000, 74.9500, True),
        ("Firozpur", "Punjab", None, 30.9167, 74.6000, True),
        ("Pathankot", "Punjab", None, 32.2667, 75.6500, True),
        ("Mohali", "Punjab", None, 30.7042, 76.7002, True),
        ("Batala", "Punjab", None, 31.9167, 75.4000, True),
        ("Moga", "Punjab", None, 30.8167, 75.1667, True),
        ("Hoshiarpur", "Punjab", None, 31.5333, 75.9167, True),
        ("Kapurthala", "Punjab", None, 31.3833, 75.3833, True),
    ])

    # RAJASTHAN
    cities_data.extend([
        ("Jaipur", "Rajasthan", "JAI", 26.9124, 75.7873, True),
        ("Jodhpur", "Rajasthan", "JDH", 26.2969, 73.0368, True),
        ("Kota", "Rajasthan", "KTU", 25.1386, 75.8361, True),
        ("Bikaner", "Rajasthan", "BKB", 28.0229, 73.3119, True),
        ("Udaipur", "Rajasthan", "UDR", 24.5854, 73.7125, True),
        ("Ajmer", "Rajasthan", None, 26.4499, 74.6399, True),
        ("Bhilwara", "Rajasthan", None, 25.3500, 74.6333, True),
        ("Alwar", "Rajasthan", None, 27.5500, 76.3833, True),
        ("Bharatpur", "Rajasthan", None, 27.2167, 77.4833, True),
        ("Sikar", "Rajasthan", None, 27.6167, 75.1500, True),
        ("Ganganagar", "Rajasthan", None, 29.9167, 73.8833, True),
        ("Hanumangarh", "Rajasthan", None, 29.5667, 74.3167, True),
        ("Churu", "Rajasthan", None, 28.3083, 74.4167, True),
        ("Pali", "Rajasthan", None, 25.7667, 73.3167, True),
        ("Jhunjhunu", "Rajasthan", None, 28.1333, 75.4000, True),
        ("Tonk", "Rajasthan", None, 26.1667, 75.7833, True),
        ("Bundi", "Rajasthan", None, 25.4333, 75.6333, True),
        ("Banswara", "Rajasthan", None, 23.5500, 74.4500, True),
        ("Dungarpur", "Rajasthan", None, 23.8333, 73.7167, True),
        ("Sawai Madhopur", "Rajasthan", None, 26.0000, 76.3167, True),
        ("Baran", "Rajasthan", None, 25.0500, 76.5167, True),
        ("Dausa", "Rajasthan", None, 26.8833, 76.3333, True),
        ("Jaisalmer", "Rajasthan", "JSA", 26.9158, 70.9082, True),
        ("Nagaur", "Rajasthan", None, 27.2000, 73.7333, True),
        ("Rajsamand", "Rajasthan", None, 25.0667, 73.8833, True),
        ("Sirohi", "Rajasthan", None, 24.8833, 72.8667, True),
        ("Barmer", "Rajasthan", None, 25.7500, 71.3833, True),
        ("Pratapgarh", "Rajasthan", None, 24.0333, 74.7833, True),
    ])

    # SIKKIM
    cities_data.extend([
        ("Gangtok", "Sikkim", None, 27.3368, 88.6065, True),
        ("Geyzing", "Sikkim", None, 27.2833, 88.2667, True),
        ("Pelling", "Sikkim", None, 27.3167, 88.2500, True),
        ("Namchi", "Sikkim", None, 27.1667, 88.3500, True),
    ])

    # TAMIL NADU
    cities_data.extend([
        ("Chennai", "Tamil Nadu", "MAA", 13.0827, 80.2707, True),
        ("Coimbatore", "Tamil Nadu", "CJB", 11.0168, 76.9558, True),
        ("Madurai", "Tamil Nadu", "IXM", 9.9252, 78.1198, True),
        ("Tiruchirappalli", "Tamil Nadu", "TRZ", 10.7905, 78.7047, True),
        ("Salem", "Tamil Nadu", None, 11.4333, 78.0667, True),
        ("Tiruppur", "Tamil Nadu", None, 11.1085, 77.3411, True),
        ("Erode", "Tamil Nadu", None, 11.3410, 77.7282, True),
        ("Tirunelveli", "Tamil Nadu", None, 8.7333, 77.7000, True),
        ("Vellore", "Tamil Nadu", None, 12.9167, 79.1333, True),
        ("Thoothukudi", "Tamil Nadu", None, 8.7833, 78.1333, True),
        ("Dindigul", "Tamil Nadu", None, 10.4833, 77.9667, True),
        ("Thanjavur", "Tamil Nadu", None, 10.7833, 79.1333, True),
        ("Ranipet", "Tamil Nadu", None, 12.9333, 79.3333, True),
        ("Sivakasi", "Tamil Nadu", None, 9.4500, 77.8000, True),
        ("Karur", "Tamil Nadu", None, 10.9500, 78.0833, True),
        ("Udhagamandalam", "Tamil Nadu", None, 11.4167, 76.6833, True),
        ("Hosur", "Tamil Nadu", None, 12.7409, 77.8252, True),
        ("Nagercoil", "Tamil Nadu", None, 8.1833, 77.4333, True),
        ("Kanchipuram", "Tamil Nadu", None, 12.8333, 79.7000, True),
        ("Kumbakonam", "Tamil Nadu", None, 10.9667, 79.4167, True),
        ("Tiruchengode", "Tamil Nadu", None, 11.3833, 77.6167, True),
        ("Vaniyambadi", "Tamil Nadu", None, 12.6833, 78.6000, True),
        ("Pollachi", "Tamil Nadu", None, 10.6667, 77.0167, True),
        ("Ramanathapuram", "Tamil Nadu", None, 9.3833, 78.8333, True),
        ("Tiruvannamalai", "Tamil Nadu", None, 12.2167, 79.0667, True),
        ("Tirupattur", "Tamil Nadu", None, 12.4833, 78.5667, True),
    ])

    # TELANGANA
    cities_data.extend([
        ("Hyderabad", "Telangana", "HYD", 17.3850, 78.4867, True),
        ("Warangal", "Telangana", None, 17.9667, 79.5833, True),
        ("Nizamabad", "Telangana", None, 18.6725, 78.0941, True),
        ("Khammam", "Telangana", None, 17.2473, 80.1514, True),
        ("Karimnagar", "Telangana", None, 18.4386, 79.1282, True),
        ("Ramagundam", "Telangana", None, 18.7519, 79.4471, True),
        ("Mahbubnagar", "Telangana", None, 16.7333, 77.9833, True),
        ("Nalgonda", "Telangana", None, 17.0500, 79.2667, True),
        ("Adilabad", "Telangana", None, 19.6667, 78.5333, True),
        ("Miryalaguda", "Telangana", None, 16.8667, 79.4833, True),
        ("Suryapet", "Telangana", None, 17.1500, 79.6167, True),
        ("Siddipet", "Telangana", None, 18.1000, 78.8500, True),
    ])

    # TRIPURA
    cities_data.extend([
        ("Agartala", "Tripura", "IXA", 23.8315, 91.2868, True),
        ("Dharmanagar", "Tripura", None, 24.3833, 92.1667, True),
        ("Udaipur", "Tripura", None, 23.5500, 91.4833, True),
        ("Kailashahar", "Tripura", None, 24.3167, 92.0167, True),
        ("Belonia", "Tripura", None, 23.2500, 91.4500, True),
    ])

    # UTTAR PRADESH
    cities_data.extend([
        ("Lucknow", "Uttar Pradesh", "LKO", 26.8467, 80.9462, True),
        ("Kanpur", "Uttar Pradesh", "KNU", 26.4499, 80.3319, True),
        ("Ghaziabad", "Uttar Pradesh", None, 28.6692, 77.4538, True),
        ("Agra", "Uttar Pradesh", "AGR", 27.1751, 78.0421, True),
        ("Meerut", "Uttar Pradesh", None, 28.9845, 77.7064, True),
        ("Varanasi", "Uttar Pradesh", "VNS", 25.3176, 82.9739, True),
        ("Prayagraj", "Uttar Pradesh", "IXD", 25.4358, 81.8806, True),
        ("Bareilly", "Uttar Pradesh", None, 28.3670, 79.4304, True),
        ("Aligarh", "Uttar Pradesh", None, 27.8803, 78.0777, True),
        ("Moradabad", "Uttar Pradesh", None, 28.8367, 78.7667, True),
        ("Saharanpur", "Uttar Pradesh", None, 30.0167, 77.5500, True),
        ("Gorakhpur", "Uttar Pradesh", "GOP", 26.7587, 83.3719, True),
        ("Noida", "Uttar Pradesh", None, 28.5355, 77.3910, True),
        ("Firozabad", "Uttar Pradesh", None, 27.1500, 78.4167, True),
        ("Jhansi", "Uttar Pradesh", "JNS", 25.4486, 78.5686, True),
        ("Muzaffarnagar", "Uttar Pradesh", None, 29.4708, 77.7036, True),
        ("Rampur", "Uttar Pradesh", None, 28.7958, 79.0167, True),
        ("Mathura", "Uttar Pradesh", None, 27.4924, 77.6737, True),
        ("Bulandshahr", "Uttar Pradesh", None, 28.4069, 77.8497, True),
        ("Aligarh", "Uttar Pradesh", None, 27.8803, 78.0777, True),
        ("Shahjahanpur", "Uttar Pradesh", None, 27.8833, 79.9167, True),
        ("Unnao", "Uttar Pradesh", None, 26.5333, 80.4833, True),
        ("Anola", "Uttar Pradesh", None, 26.4833, 82.4500, True),
        ("Azamgarh", "Uttar Pradesh", None, 26.0667, 83.1833, True),
        ("Faizabad", "Uttar Pradesh", None, 26.7833, 82.1333, True),
        ("Meerut", "Uttar Pradesh", None, 28.9845, 77.7064, True),
        ("Bareilly", "Uttar Pradesh", None, 28.3670, 79.4304, True),
        ("Basti", "Uttar Pradesh", None, 26.8167, 82.7167, True),
        ("Gonda", "Uttar Pradesh", None, 27.1333, 81.9167, True),
        ("Kanpur", "Uttar Pradesh", None, 26.4499, 80.3319, True),
        ("Lakhimpur", "Uttar Pradesh", None, 27.9333, 80.7667, True),
    ])

    # UTTARAKHAND
    cities_data.extend([
        ("Dehradun", "Uttarakhand", "DED", 30.3272, 78.0320, True),
        ("Haridwar", "Uttarakhand", None, 29.9457, 78.1642, True),
        ("Roorkee", "Uttarakhand", None, 29.8667, 77.8833, True),
        ("Haldwani", "Uttarakhand", None, 29.2167, 79.5167, True),
        ("Kashipur", "Uttarakhand", None, 29.2167, 78.9500, True),
        ("Rudrapur", "Uttarakhand", None, 28.9833, 79.4000, True),
        ("Rishikesh", "Uttarakhand", None, 30.0869, 78.2676, True),
        ("Kashipur", "Uttarakhand", None, 29.2167, 78.9500, True),
        ("Mussoorie", "Uttarakhand", None, 30.4500, 78.0833, True),
        ("Nainital", "Uttarakhand", None, 29.3833, 79.4500, True),
        ("Pauri", "Uttarakhand", None, 30.1333, 78.7667, True),
        ("Almora", "Uttarakhand", None, 29.5833, 79.6500, True),
        ("Pithoragarh", "Uttarakhand", None, 29.5833, 80.2167, True),
        ("Uttarkashi", "Uttarakhand", None, 30.7167, 78.4333, True),
        ("Chamoli", "Uttarakhand", None, 30.4000, 79.3167, True),
    ])

    # WEST BENGAL
    cities_data.extend([
        ("Kolkata", "West Bengal", "CCU", 22.5726, 88.3639, True),
        ("Howrah", "West Bengal", None, 22.5958, 88.2636, True),
        ("Durgapur", "West Bengal", None, 23.5204, 87.3119, True),
        ("Asansol", "West Bengal", None, 23.6739, 86.9524, True),
        ("Siliguri", "West Bengal", "IXB", 26.7271, 88.3948, True),
        ("Bardhaman", "West Bengal", None, 23.2333, 87.8667, True),
        ("Malda", "West Bengal", None, 25.0083, 88.1417, True),
        ("Baharampur", "West Bengal", None, 24.1167, 88.2500, True),
        ("Habla", "West Bengal", None, 22.8667, 88.3667, True),
        ("Kharagpur", "West Bengal", None, 22.3431, 87.3236, True),
        ("Shantipur", "West Bengal", None, 23.2500, 88.4333, True),
        ("Dhuliyan", "West Bengal", None, 24.2167, 88.0667, True),
        ("Ranaghat", "West Bengal", None, 23.1833, 88.5833, True),
        ("Haldia", "West Bengal", None, 22.0667, 88.0667, True),
        ("Raiganj", "West Bengal", None, 25.6167, 88.1167, True),
        ("Krishnanagar", "West Bengal", None, 23.4000, 88.5167, True),
        ("Nabadwip", "West Bengal", None, 23.4167, 88.3667, True),
        ("Midnapore", "West Bengal", None, 22.4167, 87.3167, True),
        ("Jalpaiguri", "West Bengal", None, 26.5333, 88.7167, True),
        ("Darjeeling", "West Bengal", "DAI", 27.0360, 88.2627, True),
        ("Cooch Behar", "West Bengal", None, 26.3167, 89.4500, True),
        ("Purulia", "West Bengal", None, 23.3167, 86.3667, True),
        ("Bankura", "West Bengal", None, 23.2333, 87.0667, True),
        ("Bolpur", "West Bengal", None, 23.6667, 87.7000, True),
        ("Suri", "West Bengal", None, 23.9167, 87.5333, True),
    ])

    # ANDAMAN & NICOBAR
    cities_data.extend([
        ("Port Blair", "Andaman and Nicobar", "IXZ", 11.6234, 92.7265, True),
    ])

    # CHANDIGARH (UT)
    cities_data.extend([
        ("Chandigarh", "Chandigarh", "IXC", 30.7333, 76.7794, True),
    ])

    # DADRA & NAGAR HAVELI AND DAMAN & DIU
    cities_data.extend([
        ("Daman", "Dadra and Nagar Haveli and Daman and Diu", "NMB", 20.4283, 72.8397, True),
        ("Diu", "Dadra and Nagar Haveli and Daman and Diu", "DIU", 20.7167, 70.9833, True),
        ("Silvassa", "Dadra and Nagar Haveli and Daman and Diu", None, 20.2736, 73.0167, True),
    ])

    # DELHI (UT)
    cities_data.extend([
        ("New Delhi", "Delhi", "DEL", 28.6139, 77.2090, True),
        ("Delhi", "Delhi", "DEL", 28.7041, 77.1025, True),
    ])

    # JAMMU & KASHMIR (UT)
    cities_data.extend([
        ("Srinagar", "Jammu and Kashmir", "SXR", 34.0837, 74.7973, True),
        ("Jammu", "Jammu and Kashmir", "IXJ", 32.7266, 74.8570, True),
        ("Anantnag", "Jammu and Kashmir", None, 33.7333, 75.1500, True),
        ("Baramula", "Jammu and Kashmir", None, 34.2000, 74.3500, True),
        ("Sopore", "Jammu and Kashmir", None, 34.3000, 74.4667, True),
        ("Kathua", "Jammu and Kashmir", None, 32.3833, 75.5167, True),
        ("Udhampur", "Jammu and Kashmir", None, 32.9333, 75.1333, True),
        ("Pulwama", "Jammu and Kashmir", None, 33.9833, 75.0833, True),
    ])

    # LADAKH (UT)
    cities_data.extend([
        ("Leh", "Ladakh", "IXL", 34.1667, 77.5000, True),
        ("Kargil", "Ladakh", "IXK", 34.3000, 76.3333, True),
    ])

    # LAKSHADWEEP (UT)
    cities_data.extend([
        ("Kavaratti", "Lakshadweep", None, 10.5667, 72.6167, True),
        ("Agatti", "Lakshadweep", "AGX", 10.8333, 72.1833, True),
        ("Minicoy", "Lakshadweep", None, 8.2833, 73.0500, True),
    ])

    # PUDUCHERRY (UT)
    cities_data.extend([
        ("Puducherry", "Puducherry", "PNY", 11.9363, 79.8350, True),
        ("Karaikal", "Puducherry", None, 10.9167, 79.8333, True),
        ("Yanam", "Puducherry", None, 16.7333, 82.2167, True),
        ("Mahe", "Puducherry", None, 11.7000, 75.5500, True),
    ])

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
                # Add default auto pricing
                auto_base_fare=50,
                auto_per_km=10,
                cab_base_fare=100,
                cab_per_km=15,
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
        ("JAT", "Jammu Tawi", "Jammu and Kashmir", "NR", 32.7063, 74.8643),
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
        ("RJL", "Rourkela Junction", "Odisha", "ECoR", 22.2593, 84.8834),
        ("DURG", "Durg Junction", "Chhattisgarh", "SECR", 21.1906, 81.2841),
        ("DJ", "Dhanbad Junction", "Jharkhand", "ECR", 23.7957, 86.4304),
        ("TATA", "Tatanagar Junction", "Jharkhand", "SER", 22.7746, 86.1838),
        ("BKN", "Bikaner Junction", "Rajasthan", "NWR", 28.0229, 73.3119),
        ("JU", "Jodhpur Junction", "Rajasthan", "NWR", 26.2969, 73.0368),
        ("BGKT", "Bhagat Ki Kothi", "Rajasthan", "NWR", 26.2805, 73.0264),
        ("RK", "Ratlam Junction", "Madhya Pradesh", "WR", 23.3306, 75.0367),
        ("RTM", "Ratlam", "Madhya Pradesh", "WR", 23.3306, 75.0367),
        ("INDB", "Indore Junction", "Madhya Pradesh", "WR", 22.7196, 75.8577),
        ("BRC", "Vadodara Junction", "Gujarat", "WR", 22.3107, 73.1924),
        ("ST", "Surat", "Gujarat", "WR", 21.1702, 72.8311),
        ("BCT", "Mumbai Central", "Maharashtra", "WR", 18.9667, 72.8443),
        ("LTT", "Lokmanya Tilak Terminus", "Maharashtra", "CR", 19.0772, 72.8851),
        ("TVC", "Thiruvananthapuram", "Kerala", "SR", 8.4821, 76.9201),
        ("SRR", "Shoranur Junction", "Kerala", "SR", 10.7667, 76.2667),
        ("KTYM", "Kottayam", "Kerala", "SR", 9.5916, 76.5217),
        ("PGT", "Palakkad Junction", "Kerala", "SR", 10.7867, 76.6548),
    ]

    db = SessionLocal()
    city_map = {c.name: c.id for c in db.query(City).all()}
    seen: set[str] = set()

    for code, name, state, zone, lat, lon in stations_data:
        if code in seen:
            continue
        seen.add(code)
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
    print(f"✅ Seeded {len(seen)} unique stations")


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
        ("BHO", "VABP", "Raja Bhoj Airport", "Bhopal", "Madhya Pradesh", 23.2871, 77.3366, False),
        ("CCT", "VECA", "Netaji Subhash Chandra Bose", "Kolkata", "West Bengal", 22.6547, 88.4467, False),
        ("IXB", "VEBK", "Bagdogra Airport", "Siliguri", "West Bengal", 26.6821, 88.3275, True),
        ("IXZ", "VOCP", "Veer Savarkar International", "Port Blair", "Andaman and Nicobar", 11.6570, 92.7284, False),
        ("AGR", "VIAG", "Kheria Airport", "Agra", "Uttar Pradesh", 27.1582, 77.9615, False),
        ("NAG", "VANP", "Dr. Babasaheb Ambedkar", "Nagpur", "Maharashtra", 21.0921, 79.0477, False),
        ("GAY", "VEGT", "Gaya Airport", "Gaya", "Bihar", 24.7522, 85.0382, True),
        ("DBC", "VEDG", "Dibrugarh Airport", "Dibrugarh", "Assam", 27.4833, 94.9064, False),
        ("IMF", "VEIM", "Imphal Airport", "Imphal", "Manipur", 24.8170, 93.9368, False),
        ("AJL", "VEAT", "Lengpui Airport", "Aizawl", "Mizoram", 23.7271, 92.7176, False),
        ("SHL", "VEER", "Shillong Airport", "Shillong", "Meghalaya", 25.5788, 91.8827, False),
        ("TEZ", "VETZ", "Tezpur Airport", "Tezpur", "Assam", 26.6281, 92.7958, False),
        ("JRH", "VEJR", "Rowriah Airport", "Jorhat", "Assam", 26.7541, 94.2016, False),
        ("SXR", "VISR", "Sheikh ul-Alam", "Srinagar", "Jammu and Kashmir", 33.9877, 74.7667, True),
        ("IXJ", "VIJW", "Jammu Airport", "Jammu", "Jammu and Kashmir", 32.7266, 74.8570, False),
        ("IXL", "VILH", "Kushok Bakula Rimpochee", "Leh", "Ladakh", 34.1667, 77.5000, False),
        ("DHM", "VIGG", "Gaggal Airport", "Dharamshala", "Himachal Pradesh", 32.2204, 76.3207, False),
        ("KUU", "VIBN", "Bhuntar Airport", "Kullu", "Himachal Pradesh", 31.9555, 77.1039, False),
        ("SLV", "VISL", "Shimla Airport", "Shimla", "Himachal Pradesh", 31.1048, 77.1734, False),
        ("PNY", "VOPC", "Puducherry Airport", "Puducherry", "Puducherry", 11.9363, 79.8350, False),
        ("TRM", "VOTR", "Thiruvalluvar", "Karaikal", "Puducherry", 10.9167, 79.8333, False),
        ("NMB", "VANP", "Nagpur Airport", "Nagpur", "Maharashtra", 21.0921, 79.0477, False),
        ("IXW", "VEJS", "Sonari Airport", "Jamshedpur", "Jharkhand", 22.8046, 86.2029, False),
        ("RPR", "VEBR", "Raipur Airport", "Raipur", "Chhattisgarh", 21.2514, 81.6296, False),
        ("NDC", "VENM", "Nanded Airport", "Nanded", "Maharashtra", 19.1333, 77.3167, False),
    ]

    db = SessionLocal()
    city_map = {c.name: c.id for c in db.query(City).all()}
    seen: set[str] = set()

    for iata, icao, name, city, state, lat, lon, intl in airports_data:
        if iata in seen:
            continue
        seen.add(iata)
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
    """Seed routes from data/seeds/*.json (flights, trains, buses)."""
    db = SessionLocal()

    trains = _load_seed("trains.json")
    flights = _load_seed("flights.json")
    buses = _load_seed("buses.json")

    for t in trains:
        existing = db.query(TrainRoute).filter(
            TrainRoute.train_no == t["train_no"],
            TrainRoute.from_station_code == t["from"],
        ).first()
        if existing:
            continue
        db.add(TrainRoute(
            train_no=t["train_no"],
            train_name=t["name"],
            from_station_code=t["from"],
            to_station_code=t["to"],
            departure_time=_parse_hhmm(t["departure"]),
            arrival_time=_parse_hhmm(t["arrival"]),
            duration_minutes=t["duration_minutes"],
            distance_km=t.get("distance_km"),
            days_run=t.get("days", "Daily"),
            pricing=t.get("pricing"),
            on_time_percentage=t.get("on_time_pct"),
            avg_delay_minutes=t.get("avg_delay_minutes"),
            classes=t.get("classes"),
            source=t.get("source", "curated"),
        ))

    for f in flights:
        existing = db.query(FlightRoute).filter(
            FlightRoute.flight_no == f["flight_no"],
            FlightRoute.from_airport_code == f["from"],
        ).first()
        if existing:
            continue
        db.add(FlightRoute(
            flight_no=f["flight_no"],
            airline=f["airline"],
            airline_code=f.get("airline_code"),
            from_airport_code=f["from"],
            to_airport_code=f["to"],
            departure_time=_parse_hhmm(f["departure"]),
            arrival_time=_parse_hhmm(f["arrival"]),
            duration_minutes=f["duration_minutes"],
            days_run=f.get("days", "Daily"),
            price_min=f.get("price_min"),
            price_avg=f.get("price_avg"),
            price_max=f.get("price_max"),
            on_time_percentage=f.get("on_time_pct"),
            aircraft_type=f.get("aircraft"),
            source=f.get("source", "curated"),
        ))

    for b in buses:
        existing = db.query(BusRoute).filter(
            BusRoute.operator == b["operator"],
            BusRoute.from_city == b["from_city"],
            BusRoute.to_city == b["to_city"],
        ).first()
        if existing:
            continue
        db.add(BusRoute(
            operator=b["operator"],
            operator_id=b.get("operator_id"),
            from_city=b["from_city"],
            to_city=b["to_city"],
            departure_time=_parse_hhmm(b["departure"]),
            arrival_time=_parse_hhmm(b["arrival"]),
            duration_minutes=b["duration_minutes"],
            bus_type=b["bus_type"],
            price_min=b.get("price_min"),
            price_avg=b.get("price_avg"),
            price_max=b.get("price_max"),
            fare_tiers=b.get("fare_tiers"),
            rating=b.get("rating"),
            total_ratings=b.get("total_ratings"),
            amenities=b.get("amenities"),
            source=b.get("source", "curated"),
        ))

    db.commit()
    print(f"✅ Seeded routes: {len(trains)} trains, {len(flights)} flights, {len(buses)} buses")


def seed_extra_cities() -> None:
    """Seed additional tourist cities that aren't in the default inline list."""
    db = SessionLocal()
    records = _load_seed("cities_extra.json")
    for r in records:
        existing = db.query(City).filter(City.name == r["name"]).first()
        if existing:
            continue
        db.add(City(
            name=r["name"],
            state=r["state"],
            code=r.get("code"),
            latitude=r["latitude"],
            longitude=r["longitude"],
            is_top_city=r.get("is_major", False),
        ))
    db.commit()
    print(f"✅ Seeded {len(records)} extra cities")


def seed_transfer_times() -> None:
    """Seed airport↔station transfer-time buffers from JSON."""
    db = SessionLocal()
    records = _load_seed("transfer_times.json")

    for r in records:
        city = db.query(City).filter(City.name == r.get("city_name")).first()
        existing = db.query(TransferTime).filter(
            TransferTime.from_hub_code == r["from_hub_code"],
            TransferTime.to_hub_code == r["to_hub_code"],
        ).first()
        if existing:
            continue
        db.add(TransferTime(
            city_id=city.id if city else None,
            from_hub_type=r["from_hub_type"],
            from_hub_code=r["from_hub_code"],
            to_hub_type=r["to_hub_type"],
            to_hub_code=r["to_hub_code"],
            typical_minutes=r["typical_minutes"],
            p90_minutes=r["p90_minutes"],
            buffer_minutes=r["buffer_minutes"],
            notes=r.get("notes"),
        ))

    db.commit()
    print(f"✅ Seeded {len(records)} transfer-time records")


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

    print("=" * 60)
    print("Initializing Travel Planner Database")
    print("=" * 60)

    # Create all tables
    init_db()
    print("✅ Created database tables")

    # Seed data
    seed_cities()
    seed_extra_cities()
    seed_stations()
    seed_airports()
    seed_sample_routes()
    seed_transfer_times()

    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
