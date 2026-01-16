"""Web scraping modules for transport data."""

from app.scrapers.base import BaseScraper
from app.scrapers.train_scraper import TrainScraper
from app.scrapers.flight_scraper import FlightScraper
from app.scrapers.station_scraper import StationScraper

__all__ = ["BaseScraper", "TrainScraper", "FlightScraper", "StationScraper"]
