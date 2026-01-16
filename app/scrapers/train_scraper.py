"""Indian Railways train route scraper using erail.in."""

import asyncio
from datetime import time
from typing import Any

from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper


class TrainScraper(BaseScraper):
    """
    Scrape Indian Railways train data from erail.in.

    Note: For development purposes only.
    For production, use official APIs or datasets.
    """

    BASE_URL = "https://erail.in"

    async def get_trains_between_stations(
        self, from_station: str, to_station: str, date: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Get trains running between two stations.

        Args:
            from_station: Source station code (e.g., "HWH")
            to_station: Destination station code (e.g., "HPT")
            date: Date in DD-MM-YYYY format (optional)

        Returns:
            List of train dictionaries
        """
        url = f"{self.BASE_URL}/trains-between-stations"
        params = {
            "st1": from_station,
            "st2": to_station,
        }
        if date:
            params["date"] = date

        response = await self._fetch(url, params=params)
        soup = self._parse_html(response.text)

        trains = []

        # erail.in structure - this needs to be verified with actual HTML
        table = soup.find("table", class_("train-list")) or soup.find(
            "table", {"id": "cmsTable"}
        )

        if table:
            rows = table.find_all("tr")[1:]  # Skip header row

            for row in rows:
                try:
                    cells = row.find_all("td")
                    if len(cells) < 5:
                        continue

                    # Extract train number and name
                    train_info = cells[0].find("a")
                    if not train_info:
                        continue

                    train_text = train_info.text.strip()
                    parts = train_text.split("-", 1)
                    train_no = parts[0].strip() if parts else ""
                    train_name = parts[1].strip() if len(parts) > 1 else ""

                    # Extract times
                    dep_text = cells[2].text.strip() if len(cells) > 2 else ""
                    arr_text = cells[3].text.strip() if len(cells) > 3 else ""

                    departure_time = self._parse_time(dep_text)
                    arrival_time = self._parse_time(arr_text)

                    # Calculate duration
                    duration = self._calculate_duration(departure_time, arrival_time)

                    trains.append(
                        {
                            "train_no": train_no,
                            "train_name": train_name,
                            "from_station": from_station,
                            "to_station": to_station,
                            "departure_time": departure_time,
                            "arrival_time": arrival_time,
                            "duration_minutes": duration,
                            "classes": cells[4].text.strip() if len(cells) > 4 else None,
                            "days_run": "Daily",  # Would need to parse from actual page
                        }
                    )

                except Exception:
                    continue

        return trains

    def _parse_time(self, time_str: str) -> time | None:
        """Parse time string (HH:MM) to time object."""
        try:
            if ":" not in time_str:
                return None
            parts = time_str.strip().split(":")
            hour = int(parts[0])
            minute = int(parts[1])
            return time(hour=hour, minute=minute)
        except (ValueError, IndexError):
            return None

    def _calculate_duration(self, dep: time | None, arr: time | None) -> int:
        """Calculate duration in minutes between departure and arrival."""
        if not dep or not arr:
            return 0

        dep_mins = dep.hour * 60 + dep.minute
        arr_mins = arr.hour * 60 + arr.minute

        # Handle overnight trains
        if arr_mins < dep_mins:
            arr_mins += 24 * 60

        return arr_mins - dep_mins

    async def scrape(self, from_station: str, to_station: str) -> list[dict[str, Any]]:
        """Scrape trains between two stations."""
        return await self.get_trains_between_stations(from_station, to_station)
