"""Flight data scraper using Ixigo/MakeMyTrip."""

import re
from datetime import time
from typing import Any

from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper


class FlightScraper(BaseScraper):
    """
    Scrape flight data from travel websites.

    Note: For development purposes only.
    Modern sites use heavy JavaScript - use Playwright for production.
    """

    # These URLs are examples - actual implementation would need to handle
    # dynamic content with Playwright or Selenium
    IXIGO_URL = "https://www.ixigo.com/flights"
    MAKEMYTRIP_URL = "https://www.makemytrip.com/flight/search"

    def __init__(self) -> None:
        """Initialize the flight scraper."""
        super().__init__()
        # For MVP, use a static database of common flight routes
        self._static_routes = self._load_static_routes()

    def _load_static_routes(self) -> list[dict[str, Any]]:
        """
        Load static flight routes for MVP.

        In production, this would be scraped or fetched from an API.
        """
        return [
            {
                "flight_no": "6E 234",
                "airline": "IndiGo",
                "from_code": "IXR",
                "to_code": "DEL",
                "departure_time": time(6, 30),
                "arrival_time": time(8, 45),
                "duration_minutes": 135,
                "days_run": "Daily",
                "price_avg": 4500,
                "on_time_percentage": 0.85,
            },
            {
                "flight_no": "6E 234",
                "airline": "IndiGo",
                "from_code": "IXR",
                "to_code": "BLR",
                "departure_time": time(9, 15),
                "arrival_time": time(11, 30),
                "duration_minutes": 135,
                "days_run": "Daily",
                "price_avg": 5200,
                "on_time_percentage": 0.85,
            },
            {
                "flight_no": "UK 852",
                "airline": "Vistara",
                "from_code": "BLR",
                "to_code": "HBX",
                "departure_time": time(14, 0),
                "arrival_time": time(15, 15),
                "duration_minutes": 75,
                "days_run": "Daily",
                "price_avg": 3500,
                "on_time_percentage": 0.90,
            },
            {
                "flight_no": "AI 502",
                "airline": "Air India",
                "from_code": "DEL",
                "to_code": "BLR",
                "departure_time": time(10, 0),
                "arrival_time": time(12, 30),
                "duration_minutes": 150,
                "days_run": "Daily",
                "price_avg": 6500,
                "on_time_percentage": 0.75,
            },
            {
                "flight_no": "SG 8173",
                "airline": "SpiceJet",
                "from_code": "CCU",
                "to_code": "BLR",
                "departure_time": time(7, 0),
                "arrival_time": time(9, 30),
                "duration_minutes": 150,
                "days_run": "Daily",
                "price_avg": 4800,
                "on_time_percentage": 0.78,
            },
            {
                "flight_no": "G8 115",
                "airline": "GoAir",
                "from_code": "BOM",
                "to_code": "GOI",
                "departure_time": time(6, 30),
                "arrival_time": time(7, 45),
                "duration_minutes": 75,
                "days_run": "Daily",
                "price_avg": 3200,
                "on_time_percentage": 0.82,
            },
            {
                "flight_no": "6E 611",
                "airline": "IndiGo",
                "from_code": "BOM",
                "to_code": "PNQ",
                "departure_time": time(8, 0),
                "arrival_time": time(8, 55),
                "duration_minutes": 55,
                "days_run": "Daily",
                "price_avg": 2500,
                "on_time_percentage": 0.88,
            },
            {
                "flight_no": "UK 978",
                "airline": "Vistara",
                "from_code": "DEL",
                "to_code": "AMD",
                "departure_time": time(12, 0),
                "arrival_time": time(13, 30),
                "duration_minutes": 90,
                "days_run": "Daily",
                "price_avg": 3800,
                "on_time_percentage": 0.85,
            },
        ]

    async def get_flights_between_airports(
        self, from_code: str, to_code: str, date: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get flights between two airports.

        For MVP, uses static data. In production, would scrape or use API.

        Args:
            from_code: Source airport IATA code
            to_code: Destination airport IATA code
            date: Travel date (optional, for future price variation)

        Returns:
            List of flight dictionaries
        """
        # Filter static routes
        flights = [
            f
            for f in self._static_routes
            if f["from_code"] == from_code.upper() and f["to_code"] == to_code.upper()
        ]

        return flights

    async def scrape_with_playwright(
        self, from_code: str, to_code: str, date: str
    ) -> list[dict[str, Any]]:
        """
        Scrape flights using Playwright for JS-heavy sites.

        This would require Playwright setup and is left for future implementation.
        """
        # TODO: Implement Playwright-based scraping
        # This would:
        # 1. Launch browser
        # 2. Navigate to search page with form data
        # 3. Wait for results to load
        # 4. Extract flight information
        # 5. Close browser
        return []

    async def scrape(self, from_code: str, to_code: str) -> list[dict[str, Any]]:
        """Scrape flights between two airports."""
        return await self.get_flights_between_airports(from_code, to_code)
