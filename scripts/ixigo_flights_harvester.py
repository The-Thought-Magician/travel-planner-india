#!/usr/bin/env python3
"""
ixigo Flight Data Harvester

Collects flight price data from ixigo's outlook API.
- Returns 30 days of prices in ONE call
- No API key required (simple auth pattern)
- Shows multiple airlines per route

USAGE:
    python3 scripts/ixigo_flights_harvester.py --route DEL BOM
    python3 scripts/ixigo_flights_harvester.py --top-routes 50

CAUTION: Use respectful delays to avoid being blocked.
"""

import requests
import json
import time
import random
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class IxigoFlightHarvester:
    """Harvest flight price data from ixigo API."""

    # API Endpoint
    OUTLOOK_URL = "https://www.ixigo.com/outlook/v1/onward/ranged"

    # Harvesting settings
    REQUEST_DELAY_MIN = 1
    REQUEST_DELAY_MAX = 3
    MAX_RETRIES = 3
    TIMEOUT = 30

    # Indian Airport Codes (major airports)
    AIRPORTS = {
        "DEL": "Delhi",
        "BOM": "Mumbai",
        "BLR": "Bangalore",
        "MAA": "Chennai",
        "CCU": "Kolkata",
        "HYD": "Hyderabad",
        "COK": "Kochi",
        "AMD": "Ahmedabad",
        "PNQ": "Pune",
        "GOI": "Goa",
        "JAI": "Jaipur",
        "LKO": "Lucknow",
        "GAU": "Guwahati",
        "CJB": "Coimbatore",
        "TRV": "Thiruvananthapuram",
        "NAG": "Nagpur",
        "VTZ": "Visakhapatnam",
        "BBI": "Bhubaneswar",
        "IXR": "Ranchi",
        "PAT": "Patna",
        "DED": "Dehradun",
        "IDR": "Indore",
        "JLR": "Jabalpur",
        "GAY": "Gaya",
        "SXR": "Srinagar",
        "IXB": "Bagdogra",
        "IXU": "Aurangabad",
        "JDH": "Jodhpur",
        "UDR": "Udaipur",
        "VNS": "Varanasi",
    }

    # Headers for ixigo API
    HEADERS = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'apikey': 'ixiweb$2$',
        'appversion': '2',
        'clientid': 'ixiweb',
        'content-type': 'application/json; charset=UTF-8',
        'deviceid': 'travel-planner-device',
        'ixisrc': 'ixiweb',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36',
        'uuid': 'travel-planner-uuid',
        'x-request-webappversion': '2.40.0'
    }

    def __init__(self, output_dir: str = "../data/cache/ixigo"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.routes_data: List[Dict] = []
        self.errors: List[Dict] = []

    def _delay(self):
        """Add random delay between requests."""
        delay = random.uniform(self.REQUEST_DELAY_MIN, self.REQUEST_DELAY_MAX)
        time.sleep(delay)

    def _get_journey_date(self, days_ahead: int = 7) -> str:
        """Get date string for journey query (DDMMYYYY)."""
        date = datetime.now() + timedelta(days=days_ahead)
        return date.strftime("%d%m%Y")

    def get_route_prices(self, origin: str, destination: str) -> Dict:
        """Get flight prices for a specific route.

        Returns 30 days of price data in one call!
        """
        journey_date = self._get_journey_date()

        params = {
            "departureDate": journey_date,
            "destination": destination,
            "fareClass": "e",
            "origin": origin,
            "paxCombinationType": "100",
            "refundTypes": "REFUNDABLE,NON_REFUNDABLE,PARTIALLY_REFUNDABLE"
        }

        for attempt in range(self.MAX_RETRIES):
            try:
                response = requests.get(
                    self.OUTLOOK_URL,
                    params=params,
                    headers=self.HEADERS,
                    timeout=self.TIMEOUT
                )

                if response.status_code == 200:
                    data = response.json()

                    if data.get("data") and data["data"].get("going"):
                        going = data["data"]["going"]
                        results = going.get("results", [])
                        ranges = going.get("ranges", {})

                        return {
                            "origin": origin,
                            "destination": destination,
                            "origin_city": self.AIRPORTS.get(origin, origin),
                            "destination_city": self.AIRPORTS.get(destination, destination),
                            "date_queried": journey_date,
                            "date_range_start": going.get("startDate"),
                            "date_range_end": going.get("endDate"),
                            "price_ranges": {
                                "low": ranges.get("G"),      # Good prices
                                "medium": ranges.get("Y"),    # Medium prices
                                "high": ranges.get("R")      # Peak prices
                            },
                            "flights": [
                                {
                                    "airline": f.get("airline", "Unknown"),
                                    "airline_code": f.get("airlineCode", ""),
                                    "flight_number": f.get("flightNumber", ""),
                                    "date": f.get("date"),
                                    "fare": f.get("fare"),
                                    "provider_id": f.get("providerId")
                                }
                                for f in results
                            ],
                            "total_flights": len(results),
                            "cheapest_fare": min([f.get("fare", float("inf")) for f in results]) if results else None,
                            "expensive_fare": max([f.get("fare", 0) for f in results]) if results else None,
                            "harvested_at": datetime.now().isoformat()
                        }
                    else:
                        return {"error": "No flight data found", "origin": origin, "destination": destination}

                elif response.status_code == 429:
                    wait_time = 10 * (attempt + 1)
                    print(f"  ⚠️  Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.errors.append({
                        "origin": origin,
                        "destination": destination,
                        "status": response.status_code,
                        "response": response.text[:200]
                    })

            except Exception as e:
                print(f"  ❌ Request failed (attempt {attempt + 1}): {e}")

        return {"error": "Failed to fetch", "origin": origin, "destination": destination}

    def harvest_routes(self, routes: List[Tuple[str, str]]):
        """Harvest flight data for multiple routes."""
        print("=" * 60)
        print("ixigo Flight Price Harvester")
        print("=" * 60)
        print(f"  Harvesting {len(routes)} routes")
        print(f"  Each query returns ~30 days of price data!")
        print(f"  Estimated time: {len(routes) * 2 / 60:.1f} minutes\n")

        all_data = []
        stats = {"success": 0, "failed": 0, "total_flights": 0}

        for i, (origin, dest) in enumerate(routes, 1):
            origin_city = self.AIRPORTS.get(origin, origin)
            dest_city = self.AIRPORTS.get(dest, dest)

            print(f"  [{i}/{len(routes)}] {origin_city} ({origin}) → {dest_city} ({dest})", end=' ... ')

            route_data = self.get_route_prices(origin, dest)

            if "error" not in route_data:
                stats["success"] += 1
                stats["total_flights"] += route_data.get("total_flights", 0)

                # Extract summary info
                price_range = route_data.get("price_ranges", {})
                cheapest = route_data.get("cheapest_fare", "N/A")
                airlines = set([f["airline"] for f in route_data.get("flights", []) if f["airline"]])

                print(f"✅ {route_data['total_flights']} flights, ₹{cheapest}-{route_data.get('expensive_fare', 'N/A')}, "
                      f"{len(airlines)} airlines")

                # Store individual flight records
                for flight in route_data.get("flights", []):
                    flight_record = {
                        "origin": origin,
                        "destination": dest,
                        "origin_city": origin_city,
                        "destination_city": dest_city,
                        **flight
                    }
                    all_data.append(flight_record)

                # Also store the route summary
                route_summary = {
                    k: v for k, v in route_data.items()
                    if k != "flights"
                }
                route_summary["airlines"] = list(airlines)
                self.routes_data.append(route_summary)

            else:
                stats["failed"] += 1
                print(f"❌ {route_data.get('error', 'Failed')}")

            self._delay()

            # Save progress periodically
            if i % 10 == 0:
                self._save_data(all_data)

        self.routes_data = all_data
        self._save_data(all_data)

        # Print summary
        print("\n" + "=" * 60)
        print("Harvest Summary")
        print("=" * 60)
        print(f"  Successful queries: {stats['success']}")
        print(f"  Failed queries: {stats['failed']}")
        print(f"  Total flight records: {stats['total_flights']}")

    def get_top_routes(self, n: int = 50) -> List[Tuple[str, str]]:
        """Get top N domestic routes to harvest.

        Focuses on major metro routes first.
        """
        major_hubs = ["DEL", "BOM", "BLR", "MAA", "CCU", "HYD"]
        other_airports = [code for code in self.AIRPORTS if code not in major_hubs]

        routes = []

        # Metro-to-metro (highest priority)
        for i, origin in enumerate(major_hubs):
            for dest in major_hubs[i+1:]:
                routes.append((origin, dest))

        # Metro-to-other
        for origin in major_hubs:
            for dest in other_airports[:10]:  # Top 10 others
                routes.append((origin, dest))

        return routes[:n]

    def _save_data(self, data: List[Dict]):
        """Save flight data to files."""
        # Save individual flight records
        flights_file = self.output_dir / "flights.json"
        with open(flights_file, 'w') as f:
            json.dump(data, f, indent=2)

        # Save route summaries
        routes_file = self.output_dir / "routes_summary.json"
        with open(routes_file, 'w') as f:
            json.dump(self.routes_data, f, indent=2)

        # Save metadata
        meta_file = self.output_dir / "metadata.json"
        metadata = {
            "last_updated": datetime.now().isoformat(),
            "total_flight_records": len(data),
            "total_routes": len(self.routes_data),
            "airports_covered": len(self.AIRPORTS)
        }
        with open(meta_file, 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"  💾 Saved to {flights_file}")


def main():
    parser = argparse.ArgumentParser(description='Harvest flight data from ixigo')
    parser.add_argument('--route', nargs=2, metavar=('ORIGIN', 'DEST'),
                        help='Single route to query (e.g., --route DEL BOM)')
    parser.add_argument('--top-routes', type=int, default=None,
                        help='Harvest top N domestic routes')
    parser.add_argument('--output-dir', default='../data/cache/ixigo',
                        help='Output directory for cached data')

    args = parser.parse_args()

    harvester = IxigoFlightHarvester(output_dir=args.output_dir)

    if args.route:
        origin, dest = args.route
        result = harvester.get_route_prices(origin.upper(), dest.upper())
        print(json.dumps(result, indent=2))

    elif args.top_routes:
        routes = harvester.get_top_routes(args.top_routes)
        harvester.harvest_routes(routes)

    else:
        # Default: test with a few routes
        test_routes = [("DEL", "BOM"), ("BLR", "MAA"), ("CCU", "HYD")]
        harvester.harvest_routes(test_routes)


if __name__ == "__main__":
    main()
