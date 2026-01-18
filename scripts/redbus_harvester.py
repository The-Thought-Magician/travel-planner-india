#!/usr/bin/env python3
"""
RedBus Data Harvester

Discovers and collects bus route data from RedBus API.
- Phase 1: Discover all city IDs via autocomplete
- Phase 2: Harvest routes between city pairs

USAGE:
    python3 scripts/redbus_harvester.py --discover-cities
    python3 scripts/redbus_harvester.py --harvest-routes --limit 100

CAUTION: Use respectful delays to avoid being blocked.
This is for research/development purposes.
"""

import requests
import json
import time
import random
import string
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Set
from itertools import combinations


class RedBusHarvester:
    """Harvest bus data from RedBus API."""

    # API Endpoints
    AUTOCOMPLETE_URL = "https://www.redbus.in/seowapi/search-autocomplete"
    SEARCH_URL = "https://www.redbus.in/rpw/api/searchResults"

    # Harvesting settings
    REQUEST_DELAY_MIN = 2  # Minimum seconds between requests
    REQUEST_DELAY_MAX = 5  # Maximum seconds between requests
    MAX_RETRIES = 3
    TIMEOUT = 30

    # Common Indian city name prefixes for discovery
    COMMON_PREFIXES = [
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'y', 'z',
        'ban', 'ben', 'bha', 'bhu', 'che', 'cha', 'coi', 'cul', 'del',
        'dha', 'g', 'goa', 'gu', 'hyd', 'hub', 'jam', 'jai', 'kol',
        'koc', 'koz', 'lu', 'mum', 'mys', 'nag', 'nan', 'pun', 'pud',
        'ranch', 'sur', 'tir', 'ud', 'upa', 'vad', 'vij', 'vis', 'war'
    ]

    # Headers to mimic browser
    HEADERS = {
        'accept': '*/*',
        'accept-language': 'en-US,en;q=0.9',
        'content-type': 'application/json',
        'origin': 'https://www.redbus.in',
        'priority': 'u=1, i',
        'sec-ch-ua': '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Mobile Safari/537.36'
    }

    # Empty payload for search requests
    SEARCH_PAYLOAD = {
        "appliedFilterCount": 0,
        "onlyShow": [], "dt": [], "SeaterType": [], "AcType": [],
        "travelsList": [], "amtList": [], "bpList": [], "dpList": [],
        "CampaignFilter": [], "at": [], "persuasionList": [],
        "bpIdentifier": [], "dpIdentifier": [], "bcf": [],
        "opBusTypeFilterList": [], "priceRange": [], "RouteIds": [],
        "bpKeys": [], "dpKeys": [], "streaksFilter": [],
        "preRouteFilters": None
    }

    def __init__(self, output_dir: str = "../data/cache/redbus"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.cities: Dict[int, Dict] = {}
        self.routes: List[Dict] = []
        self.errors: List[Dict] = []

    def _delay(self):
        """Add random delay between requests."""
        delay = random.uniform(self.REQUEST_DELAY_MIN, self.REQUEST_DELAY_MAX)
        time.sleep(delay)

    def _make_request(self, url: str, params: dict = None, json_data: dict = None) -> dict:
        """Make HTTP request with retries."""
        headers = self.HEADERS.copy()

        # Add referer for search requests
        if json_data is not None:
            headers['referer'] = 'https://www.redbus.in/bus-tickets'
        else:
            headers['referer'] = 'https://www.redbus.in/bus-tickets'

        for attempt in range(self.MAX_RETRIES):
            try:
                if json_data is not None:
                    response = requests.get(
                        url,
                        params=params,
                        headers=headers,
                        json=json_data,
                        timeout=self.TIMEOUT
                    )
                else:
                    response = requests.get(
                        url,
                        params=params,
                        headers=headers,
                        timeout=self.TIMEOUT
                    )

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    wait_time = 30 * (attempt + 1)
                    print(f"  ⚠️  Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    self.errors.append({
                        'url': url,
                        'status': response.status_code,
                        'response': response.text[:500]
                    })

            except Exception as e:
                print(f"  ❌ Request failed (attempt {attempt + 1}): {e}")
                if attempt < self.MAX_RETRIES - 1:
                    time.sleep(5)

        return {}

    def discover_cities(self) -> Dict[int, Dict]:
        """Discover all cities via autocomplete API."""
        print("=" * 60)
        print("Phase 1: Discovering Cities")
        print("=" * 60)

        cities = {}

        for prefix in self.COMMON_PREFIXES:
            print(f"  🔍 Searching: '{prefix}'...", end=' ')

            params = {
                'q': prefix,
                'cc': 'IND',
                'lang': 'EN',
                'v': str(int(time.time() * 1000))
            }

            data = self._make_request(self.AUTOCOMPLETE_URL, params=params)

            if data and 'response' in data:
                docs = data.get('response', {}).get('docs', [])
                city_count = 0

                for doc in docs:
                    # Only collect cities (not areas, terminals)
                    if doc.get('locationType') == 'CITY':
                        city_id = doc.get('ID')
                        if city_id and city_id not in cities:
                            cities[city_id] = {
                                'id': city_id,
                                'name': doc.get('Name'),
                                'full_name': doc.get('locationName'),
                                'region': doc.get('region'),
                                'country': doc.get('cc'),
                                'parent_location': doc.get('parentLocation'),
                                'rank': doc.get('rank')
                            }
                            city_count += 1

                print(f"Found {city_count} new cities (total: {len(cities)})")
            else:
                print("Failed")

            self._delay()

            # Safety break
            if len(cities) > 1000:
                print(f"  ⚠️  Reached {len(cities)} cities. Stopping discovery.")
                break

        self.cities = cities

        # Save cities
        output_file = self.output_dir / "cities.json"
        with open(output_file, 'w') as f:
            json.dump(cities, f, indent=2)

        print(f"\n✅ Discovered {len(cities)} cities")
        print(f"💾 Saved to {output_file}")

        return cities

    def get_journey_date(self, days_ahead: int = 7) -> str:
        """Get date string for journey query."""
        date = datetime.now() + timedelta(days=days_ahead)
        return date.strftime("%d-%b-%Y")  # e.g., "25-Jan-2026"

    def harvest_routes(self, city_pairs: List[tuple] = None, limit: int = None):
        """Harvest bus routes between city pairs."""
        print("\n" + "=" * 60)
        print("Phase 2: Harvesting Routes")
        print("=" * 60)

        if not self.cities:
            # Load cities from file
            cities_file = self.output_dir / "cities.json"
            if cities_file.exists():
                with open(cities_file) as f:
                    self.cities = json.load(f)
                # Convert string keys back to int
                self.cities = {int(k): v for k, v in self.cities.items()}
            else:
                print("❌ No cities found. Run --discover-cities first.")
                return

        # Determine city pairs to query
        if city_pairs is None:
            # Use top cities by rank
            city_list = sorted(
                self.cities.values(),
                key=lambda x: x.get('rank', float('inf'))
            )[:50]  # Top 50 cities
            city_ids = [c['id'] for c in city_list]
            city_pairs = list(combinations(city_ids, 2))

        if limit:
            city_pairs = city_pairs[:limit]

        print(f"  📊 Querying {len(city_pairs)} city pairs")
        print(f"  📅 Journey date: {self.get_journey_date()}")
        print(f"  ⏱️  Estimated time: {len(city_pairs) * 4 / 60:.1f} minutes\n")

        journey_date = self.get_journey_date()
        routes = []
        stats = {
            'total_pairs': len(city_pairs),
            'successful': 0,
            'failed': 0,
            'with_buses': 0,
            'total_buses': 0
        }

        for i, (from_id, to_id) in enumerate(city_pairs, 1):
            from_city = self.cities.get(from_id, {}).get('name', str(from_id))
            to_city = self.cities.get(to_id, {}).get('name', str(to_id))

            print(f"  [{i}/{len(city_pairs)}] {from_city} → {to_city}...", end=' ')

            params = {
                'fromCity': from_id,
                'toCity': to_id,
                'DOJ': journey_date,
                'limit': 50,
                'offset': 0,
                'meta': 'true',
                'groupId': 0,
                'sectionId': 0,
                'sort': 0,
                'sortOrder': 0,
                'from': 'initialLoad',
                'getUuid': 'true',
                'bT': 1,
                'clearLMBFilter': 'undefined'
            }

            data = self._make_request(self.SEARCH_URL, params=params, json_data=self.SEARCH_PAYLOAD)

            if data and data.get('success'):
                stats['successful'] += 1

                # Extract bus information
                buses = data.get('data', {}).get('rdBoostedInv', [])

                if buses:
                    stats['with_buses'] += 1
                    stats['total_buses'] += len(buses)

                    for bus in buses:
                        route = {
                            'from_city_id': from_id,
                            'from_city_name': from_city,
                            'to_city_id': to_id,
                            'to_city_name': to_city,
                            'operator_id': bus.get('operatorId'),
                            'operator_name': bus.get('travelsName'),
                            'route_id': bus.get('routeId'),
                            'service_name': bus.get('serviceName'),
                            'bus_type': bus.get('busType'),
                            'departure_time': bus.get('departureTime'),
                            'arrival_time': bus.get('arrivalTime'),
                            'duration_minutes': bus.get('journeyDurationMin'),
                            'fares': bus.get('fareList', []),
                            'available_seats': bus.get('availableSeats'),
                            'total_seats': bus.get('totalSeats'),
                            'is_ac': bus.get('isAc'),
                            'is_sleeper': bus.get('isSleeper'),
                            'is_seater': bus.get('isSeater'),
                            'rating': bus.get('totalRatings'),
                            'reviews_count': bus.get('numberOfReviews'),
                            'boarding_points': bus.get('bpCount'),
                            'dropping_points': bus.get('dpCount'),
                            'standard_bp': bus.get('standardBpName'),
                            'standard_dp': bus.get('standardDpName'),
                            'live_tracking': bus.get('isLiveTrackingAvailable', False),
                            'cancellation_policy': bus.get('cancellationPolicy'),
                            'harvested_at': datetime.now().isoformat()
                        }
                        routes.append(route)

                    print(f"✅ {len(buses)} buses")
                else:
                    print("No buses")
            else:
                stats['failed'] += 1
                print("❌ Failed")

            self._delay()

            # Save progress periodically
            if i % 10 == 0:
                self._save_routes(routes)

        self.routes = routes
        self._save_routes(routes)

        # Print summary
        print("\n" + "=" * 60)
        print("Harvest Summary")
        print("=" * 60)
        print(f"  Total city pairs queried: {stats['total_pairs']}")
        print(f"  Successful queries: {stats['successful']}")
        print(f"  Failed queries: {stats['failed']}")
        print(f"  Pairs with buses: {stats['with_buses']}")
        print(f"  Total buses found: {stats['total_buses']}")
        print(f"  Unique routes: {len(routes)}")

    def _save_routes(self, routes: List[Dict]):
        """Save routes to file."""
        output_file = self.output_dir / "routes.json"
        with open(output_file, 'w') as f:
            json.dump(routes, f, indent=2)

        # Also save a summary
        summary_file = self.output_dir / "routes_summary.json"
        summary = {
            'total_routes': len(routes),
            'last_updated': datetime.now().isoformat(),
            'operators': len(set(r['operator_id'] for r in routes)),
            'city_pairs': len(set((r['from_city_id'], r['to_city_id']) for r in routes))
        }
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description='Harvest bus data from RedBus')
    parser.add_argument('--discover-cities', action='store_true',
                        help='Discover all cities via autocomplete API')
    parser.add_argument('--harvest-routes', action='store_true',
                        help='Harvest routes between discovered cities')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of city pairs to query (for testing)')
    parser.add_argument('--output-dir', default='../data/cache/redbus',
                        help='Output directory for cached data')

    args = parser.parse_args()

    harvester = RedBusHarvester(output_dir=args.output_dir)

    if args.discover_cities:
        harvester.discover_cities()

    if args.harvest_routes:
        harvester.harvest_routes(limit=args.limit)

    if not args.discover_cities and not args.harvest_routes:
        parser.print_help()


if __name__ == "__main__":
    main()
