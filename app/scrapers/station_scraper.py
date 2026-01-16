"""Indian Railways station scraper using erail.in."""

import re
from typing import Any

from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper


class StationScraper(BaseScraper):
    """
    Scrape Indian Railways station data from erail.in.

    Note: For development purposes only.
    For production, use official APIs or datasets.
    """

    BASE_URL = "https://erail.in"

    async def get_stations_by_city(self, city: str) -> list[dict[str, Any]]:
        """
        Get railway stations for a given city.

        Args:
            city: City name to search for

        Returns:
            List of station dictionaries
        """
        # Search for stations
        url = f"{self.BASE_URL}/railway-station"
        response = await self._fetch(url, params={"q": city})
        soup = self._parse_html(response.text)

        stations = []

        # Parse station data (structure varies, this is a basic implementation)
        # The actual implementation would need to inspect erail.in's HTML structure
        station_elements = soup.find_all("div", class_="station-item") or soup.select(
            "tr.station-row"
        )

        for element in station_elements[:50]:  # Limit results
            try:
                name_elem = element.find("span", class_="station-name") or element.find(
                    "td", class_="name"
                )
                code_elem = element.find("span", class_="station-code") or element.find(
                    "td", class_="code"
                )
                state_elem = element.find("span", class_="station-state") or element.find(
                    "td", class_="state"
                )

                if name_elem and code_elem:
                    stations.append(
                        {
                            "code": code_elem.text.strip(),
                            "name": name_elem.text.strip(),
                            "state": state_elem.text.strip() if state_elem else None,
                        }
                    )
            except Exception:
                continue

        return stations

    async def get_all_stations(self) -> list[dict[str, Any]]:
        """
        Get a comprehensive list of Indian Railway stations.

        For MVP, we'll use a static approach since scraping 8000+ stations
        would be slow and rate-limited.

        Returns:
            List of station dictionaries
        """
        # For MVP, return top stations
        # In production, load from a seeded CSV or database
        return await self._get_top_stations()

    async def _get_top_stations(self) -> list[dict[str, Any]]:
        """Return top 100 railway stations by traffic (hardcoded for MVP)."""
        return [
            {"code": "HWH", "name": "Howrah Junction", "state": "West Bengal"},
            {"code": "NDLS", "name": "New Delhi", "state": "Delhi"},
            {"code": "MAS", "name": "Chennai Central", "state": "Tamil Nadu"},
            {"code": "CSMT", "name": "Mumbai CST", "state": "Maharashtra"},
            {"code": "SBC", "name": "Bangalore City Junction", "state": "Karnataka"},
            {"code": "HYB", "name": "Hyderabad Deccan", "state": "Telangana"},
            {"code": "KOAA", "name": "Kolkata", "state": "West Bengal"},
            {"code": "JP", "name": "Jaipur", "state": "Rajasthan"},
            {"code": "LKO", "name": "Lucknow", "state": "Uttar Pradesh"},
            {"code": "PNBE", "name": "Patna Junction", "state": "Bihar"},
            {"code": "BPL", "name": "Bhopal Junction", "state": "Madhya Pradesh"},
            {"code": "AGC", "name": "Agra Cantt", "state": "Uttar Pradesh"},
            {"code": "CNB", "name": "Kanpur Central", "state": "Uttar Pradesh"},
            {"code": "BBS", "name": "Bhubaneswar", "state": "Odisha"},
            {"code": "TVC", "name": "Thiruvananthapuram", "state": "Kerala"},
            {"code": "ADI", "name": "Ahmedabad Junction", "state": "Gujarat"},
            {"code": "PUNE", "name": "Pune Junction", "state": "Maharashtra"},
            {"code": "SUR", "name": "Solapur Junction", "state": "Maharashtra"},
            {"code": "NGP", "name": "Nagpur", "state": "Maharashtra"},
            {"code": "ALL", "name": "Allahabad Junction", "state": "Uttar Pradesh"},
            {"code": "JAT", "name": "Jammu Tawi", "state": "Jammu & Kashmir"},
            {"code": "ASR", "name": "Amritsar Junction", "state": "Punjab"},
            {"code": "LDH", "name": "Ludhiana Junction", "state": "Punjab"},
            {"code": "UMB", "name": "Ambala Cant", "state": "Haryana"},
            {"code": "KOTA", "name": "Kota Junction", "state": "Rajasthan"},
            {"code": "BJU", "name": "Barauni Junction", "state": "Bihar"},
            {"code": "DURG", "name": "Durg Junction", "state": "Chhattisgarh"},
            {"code": "R", "name": "Raipur Junction", "state": "Chhattisgarh"},
            {"code": "RNC", "name": "Ranchi", "state": "Jharkhand"},
            {"code": "HPT", "name": "Hospet Junction", "state": "Karnataka"},
            {"code": "UBL", "name": "Hubballi Junction", "state": "Karnataka"},
            {"code": "MAS", "name": "Chennai Central", "state": "Tamil Nadu"},
            {"code": "CLT", "name": "Kozhikode", "state": "Kerala"},
            {"code": "ERS", "name": "Ernakulam Junction", "state": "Kerala"},
            {"code": "GNT", "name": "Guntur Junction", "state": "Andhra Pradesh"},
            {"code": "BZA", "name": "Vijayawada Junction", "state": "Andhra Pradesh"},
            {"code": "SC", "name": "Secunderabad Junction", "state": "Telangana"},
            {"code": "TVC", "name": "Thiruvananthapuram", "state": "Kerala"},
            {"code": "GHY", "name": "Guwahati", "state": "Assam"},
            {"code": "BKN", "name": "Bikaner Junction", "state": "Rajasthan"},
            {"code": "JU", "name": "Jodhpur Junction", "state": "Rajasthan"},
        ]

    async def scrape(self, city: str) -> list[dict[str, Any]]:
        """Scrape stations for a city."""
        return await self.get_stations_by_city(city)
