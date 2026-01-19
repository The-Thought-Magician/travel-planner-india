#!/usr/bin/env python3
"""
RailRadar API Harvester

Collects live train data from RailRadar API.
Supports multiple API keys with rotation and rate limit distribution.

GET API KEYS: https://railradar.in/signup
API DOCS: https://railradar.in/docs

USAGE:
    # Add your API keys to a file (one per line)
    echo "your_api_key_1" > railradar_keys.txt
    echo "your_api_key_2" >> railradar_keys.txt

    # Discover all trains
    python3 scripts/railradar_harvester.py --discover-trains --keys railradar_keys.txt

    # Get live status for specific trains
    python3 scripts/railradar_harvester.py --live-status --train-numbers 12301,12951,12953 --keys railradar_keys.txt

    # Harvest trains between stations
    python3 scripts/railradar_harvester.py --trains-between --from NDLS --to HWH --keys railradar_keys.txt
"""

import requests
import json
import time
import random
import argparse
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class RailRadarAPIKey:
    """Manages a single API key with rate limiting."""

    def __init__(self, key: str, requests_per_minute: int = 60):
        self.key = key
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        self.lock = threading.Lock()
        self.total_requests = 0
        self.failures = 0

    def can_make_request(self) -> bool:
        """Check if this key can make a request (rate limit check)."""
        with self.lock:
            now = time.time()
            # Remove requests older than 1 minute
            self.request_times = [t for t in self.request_times if now - t < 60]
            return len(self.request_times) < self.requests_per_minute

    def record_request(self, success: bool = True):
        """Record a request made with this key."""
        with self.lock:
            self.request_times.append(time.time())
            self.total_requests += 1
            if not success:
                self.failures += 1

    def wait_time(self) -> float:
        """Calculate wait time before next request."""
        with self.lock:
            if len(self.request_times) < self.requests_per_minute:
                return 0
            # Sort and find when the oldest request will be 60 seconds old
            sorted_times = sorted(self.request_times)
            oldest_in_minute = sorted_times[0]
            wait_until = oldest_in_minute + 60
            return max(0, wait_until - time.time())


class RailRadarHarvester:
    """Harvest train data from RailRadar API with multiple API keys."""

    # RailRadar API Base URL
    BASE_URL = "https://railradar.in/api/v1"

    # API Endpoints (based on RailRadar documentation)
    ENDPOINTS = {
        "live_status": "/live/{train_number}",
        "train_schedule": "/train/{train_number}",
        "trains_between": "/trains/{from}/{to}",
        "station": "/station/{station_code}",
        "all_trains": "/trains",
        "all_stations": "/stations",
    }

    def __init__(self, api_keys: List[str], output_dir: str = "../data/cache/railradar"):
        """
        Initialize harvester with API keys.

        Args:
            api_keys: List of RailRadar API keys
            output_dir: Directory to store cached data
        """
        self.api_keys = [RailRadarAPIKey(key) for key in api_keys]
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'TravelPlanner/1.0 (contact: travel-planner@example.com)',
            'Accept': 'application/json',
        })

        self.stats = {
            'total_requests': 0,
            'successful': 0,
            'failed': 0,
            'by_key': []
        }

    def _get_available_key(self) -> Optional[RailRadarAPIKey]:
        """Get an API key that is available (not rate limited)."""
        # Shuffle for load distribution
        keys = self.api_keys.copy()
        random.shuffle(keys)

        for api_key in keys:
            if api_key.can_make_request():
                return api_key

        # If all keys are rate limited, return the one with shortest wait time
        min_wait = float('inf')
        best_key = None
        for api_key in keys:
            wait = api_key.wait_time()
            if wait < min_wait:
                min_wait = wait
                best_key = api_key

        if min_wait > 0:
            print(f"  ⏳ All keys rate limited. Waiting {min_wait:.1f}s...")
            time.sleep(min_wait + 0.5)

        return best_key

    def _make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make API request with automatic key rotation."""
        max_retries = 3

        for attempt in range(max_retries):
            api_key = self._get_available_key()

            if api_key is None:
                print("  ❌ No API keys available")
                return {"error": "No API keys available"}

            # Add API key to headers
            headers = {'X-API-Key': api_key.key}

            # Build full URL
            url = f"{self.BASE_URL}{endpoint}"

            try:
                self.stats['total_requests'] += 1

                response = self.session.get(url, params=params, headers=headers, timeout=30)

                # Record the request
                success = response.status_code == 200
                api_key.record_request(success)

                if response.status_code == 200:
                    self.stats['successful'] += 1
                    return response.json()
                elif response.status_code == 429:
                    print(f"  ⚠️  Rate limited for key ...{api_key.key[-4:]}")
                    time.sleep(5)
                elif response.status_code == 401:
                    print(f"  ❌ Invalid API key ...{api_key.key[-4:]}")
                    api_key.record_request(False)
                    break
                else:
                    print(f"  ⚠️  Status {response.status_code}: {response.text[:100]}")
                    api_key.record_request(False)
                    time.sleep(1)

            except Exception as e:
                print(f"  ❌ Request error: {e}")
                api_key.record_request(False)
                time.sleep(1)

        self.stats['failed'] += 1
        return {"error": "Max retries exceeded"}

    def get_live_status(self, train_number: str) -> dict:
        """Get live status for a specific train."""
        endpoint = self.ENDPOINTS["live_status"].format(train_number=train_number)
        return self._make_request(endpoint)

    def get_train_schedule(self, train_number: str) -> dict:
        """Get schedule for a specific train."""
        endpoint = self.ENDPOINTS["train_schedule"].format(train_number=train_number)
        return self._make_request(endpoint)

    def get_trains_between(self, from_station: str, to_station: str) -> dict:
        """Get trains between two stations."""
        endpoint = self.ENDPOINTS["trains_between"].format(from=from_station, to=to_station)
        return self._make_request(endpoint)

    def get_station_info(self, station_code: str) -> dict:
        """Get information about a station."""
        endpoint = self.ENDPOINTS["station"].format(station_code=station_code)
        return self._make_request(endpoint)

    def discover_all_trains(self) -> dict:
        """Get list of all trains."""
        endpoint = self.ENDPOINTS["all_trains"]
        return self._make_request(endpoint)

    def discover_all_stations(self) -> dict:
        """Get list of all stations."""
        endpoint = self.ENDPOINTS["all_stations"]
        return self._make_request(endpoint)

    def harvest_live_status_batch(self, train_numbers: List[str], max_workers: int = None) -> List[dict]:
        """
        Harvest live status for multiple trains in parallel using multiple API keys.

        Args:
            train_numbers: List of train numbers to query
            max_workers: Maximum parallel workers (default: number of API keys)

        Returns:
            List of live status responses
        """
        if max_workers is None:
            max_workers = min(len(self.api_keys), 10)

        print(f"  Harvesting live status for {len(train_numbers)} trains")
        print(f"  Using {len(self.api_keys)} API keys with {max_workers} workers\n")

        results = []

        def fetch_status(train_number: str) -> tuple:
            status = self.get_live_status(train_number)
            return train_number, status

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(fetch_status, tn): tn for tn in train_numbers}

            for i, future in enumerate(as_completed(futures), 1):
                train_number, status = future.result()

                success = "error" not in status
                status_code = "✅" if success else "❌"

                print(f"  [{i}/{len(train_numbers)}] {status_code} Train {train_number}: "
                      f"{len(status.get('data', {}))} fields" if success else f"Error")

                results.append({
                    "train_number": train_number,
                    "status": status,
                    "success": success,
                    "harvested_at": datetime.now().isoformat()
                })

                # Small delay to prevent overwhelming
                time.sleep(0.1)

        return results

    def harvest_trains_between_parallel(self, route_pairs: List[tuple], max_workers: int = None) -> List[dict]:
        """
        Harvest trains between multiple station pairs in parallel.

        Args:
            route_pairs: List of (from, to) station code tuples
            max_workers: Maximum parallel workers

        Returns:
            List of train results for each route
        """
        if max_workers is None:
            max_workers = min(len(self.api_keys), 10)

        print(f"  Harvesting trains for {len(route_pairs)} routes")
        print(f"  Using {len(self.api_keys)} API keys with {max_workers} workers\n")

        results = []

        def fetch_trains(from_station: str, to_station: str) -> tuple:
            data = self.get_trains_between(from_station, to_station)
            return (from_station, to_station), data

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(fetch_trains, frm, to): (frm, to)
                for frm, to in route_pairs
            }

            for i, future in enumerate(as_completed(futures), 1):
                (frm, to), data = future.result()

                success = "error" not in data and data.get("success")
                status_code = "✅" if success else "❌"

                train_count = len(data.get("data", {}).get("trains", [])) if success else 0
                print(f"  [{i}/{len(route_pairs)}] {status_code} {frm}→{to}: {train_count} trains")

                results.append({
                    "from": frm,
                    "to": to,
                    "data": data,
                    "success": success,
                    "train_count": train_count,
                    "harvested_at": datetime.now().isoformat()
                })

        return results

    def save_results(self, data: list, filename: str):
        """Save results to file."""
        output_file = self.output_dir / filename
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"  💾 Saved to {output_file}")

    def print_stats(self):
        """Print harvester statistics."""
        print("\n" + "=" * 60)
        print("Statistics")
        print("=" * 60)
        print(f"  Total requests: {self.stats['total_requests']}")
        print(f"  Successful: {self.stats['successful']}")
        print(f"  Failed: {self.stats['failed']}")
        print(f"  Success rate: {self.stats['successful']/max(1,self.stats['total_requests'])*100:.1f}%")
        print("\n  API Key Usage:")
        for i, key in enumerate(self.api_keys, 1):
            print(f"    Key {i} (...{key.key[-4:]}): "
                  f"{key.total_requests} requests, {key.failures} failures")


def load_api_keys(keys_file: str) -> List[str]:
    """Load API keys from file (one per line)."""
    file_path = Path(keys_file)
    if not file_path.exists():
        print(f"  ❌ API keys file not found: {keys_file}")
        print(f"  Create it with: echo 'your_api_key' > {keys_file}")
        return []

    keys = []
    with open(file_path) as f:
        for line in f:
            key = line.strip()
            if key and not key.startswith('#'):
                keys.append(key)

    return keys


def main():
    parser = argparse.ArgumentParser(description='Harvest train data from RailRadar API')
    parser.add_argument('--keys', required=True, help='File containing API keys (one per line)')
    parser.add_argument('--discover-trains', action='store_true', help='Discover all trains')
    parser.add_argument('--discover-stations', action='store_true', help='Discover all stations')
    parser.add_argument('--live-status', action='store_true', help='Get live status for trains')
    parser.add_argument('--train-numbers', help='Comma-separated train numbers for live status')
    parser.add_argument('--trains-between', action='store_true', help='Get trains between stations')
    parser.add_argument('--from', dest='from_station', help='From station code')
    parser.add_argument('--to', dest='to_station', help='To station code')
    parser.add_argument('--top-trains', type=int, help='Harvest live status for top N trains')
    parser.add_argument('--output-dir', default='../data/cache/railradar', help='Output directory')
    parser.add_argument('--workers', type=int, help='Number of parallel workers')

    args = parser.parse_args()

    # Load API keys
    api_keys = load_api_keys(args.keys)

    if not api_keys:
        print("❌ No API keys loaded. Exiting.")
        return

    print(f"✅ Loaded {len(api_keys)} API keys")
    print(f"   Each key: ~{60} requests/minute")
    print(f"   Total capacity: ~{len(api_keys) * 60} requests/minute\n")

    harvester = RailRadarHarvester(api_keys, output_dir=args.output_dir)

    # Execute requested action
    if args.discover_trains:
        print("=" * 60)
        print("Discovering All Trains")
        print("=" * 60)
        result = harvester.discover_all_trains()
        print(json.dumps(result, indent=2))
        harvester.save_results([result], "all_trains.json")

    elif args.discover_stations:
        print("=" * 60)
        print("Discovering All Stations")
        print("=" * 60)
        result = harvester.discover_all_stations()
        print(json.dumps(result, indent=2))
        harvester.save_results([result], "all_stations.json")

    elif args.live_status:
        if args.train_numbers:
            train_numbers = args.train_numbers.split(',')
        elif args.top_trains:
            # Top Indian trains
            train_numbers = [
                "12301", "12302", "12951", "12952", "12953", "12954",  # Rajdhani
                "12001", "12002", "12245", "12246", "12425", "12426",  # BSKS
                "12627", "12628", "12621", "12622", "12839", "12840",  # Karnataka
                "22691", "22692", "12429", "12430", "22221", "22222",  # Others
            ][:args.top_trains]
        else:
            print("❌ Specify --train-numbers or --top-trains")
            return

        print("=" * 60)
        print(f"Live Status for {len(train_numbers)} Trains")
        print("=" * 60)

        results = harvester.harvest_live_status_batch(
            train_numbers,
            max_workers=args.workers
        )
        harvester.save_results(results, "live_status.json")

    elif args.trains_between:
        if not args.from_station or not args.to_station:
            print("❌ Specify --from and --to station codes")
            return

        print("=" * 60)
        print(f"Trains Between {args.from_station} and {args.to_station}")
        print("=" * 60)

        result = harvester.get_trains_between(args.from_station, args.to_station)
        print(json.dumps(result, indent=2))
        harvester.save_results([result], f"trains_{args.from_station}_{args.to_station}.json")

    else:
        # Default: discover trains and stations
        harvester.discover_trains()
        harvester.discover_stations()

    harvester.print_stats()


if __name__ == "__main__":
    main()
