"""Base scraper with common functionality."""

import asyncio
import random
from abc import ABC, abstractmethod
from typing import Any

import httpx
from bs4 import BeautifulSoup

from app.config import settings


class BaseScraper(ABC):
    """Base scraper with common functionality for all scrapers."""

    def __init__(self) -> None:
        """Initialize the scraper."""
        self.client = httpx.AsyncClient(
            timeout=settings.scraper_timeout,
            headers={
                "User-Agent": settings.scraper_user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate",
                "Connection": "keep-alive",
            },
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def _fetch(
        self, url: str, params: dict[str, Any] | None = None, retry: int = 3
    ) -> httpx.Response:
        """
        Fetch a URL with retry logic and rate limiting.

        Args:
            url: The URL to fetch
            params: Query parameters
            retry: Number of retries

        Returns:
            The HTTP response

        Raises:
            httpx.HTTPError: If all retries fail
        """
        for attempt in range(retry):
            try:
                # Rate limiting
                await asyncio.sleep(
                    random.uniform(settings.scraper_delay_min, settings.scraper_delay_max)
                )

                response = await self.client.get(url, params=params, follow_redirects=True)
                response.raise_for_status()
                return response

            except httpx.HTTPError as e:
                if attempt == retry - 1:
                    raise
                await asyncio.sleep(2**attempt)  # Exponential backoff

    def _parse_html(self, html: str) -> BeautifulSoup:
        """Parse HTML content with BeautifulSoup."""
        return BeautifulSoup(html, "lxml")

    @abstractmethod
    async def scrape(self, *args: Any, **kwargs: Any) -> Any:
        """Scrape data - to be implemented by subclasses."""
        pass
