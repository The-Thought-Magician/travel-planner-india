"""Application configuration."""

import os
from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""

    # Environment
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = True

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "sqlite:///./data/travel_planner.db"

    # Cache
    cache_ttl_seconds: int = 3600  # 1 hour

    # Scraping
    scraper_user_agent: str = (
        "Mozilla/5.0 (compatible; TravelPlanner-Bot/1.0; +https://github.com/travel-planner)"
    )
    scraper_delay_min: float = 1.0
    scraper_delay_max: float = 3.0
    scraper_timeout: int = 30

    # Routing
    max_connections: int = 3
    min_connection_buffer_minutes: int = 60
    max_journey_hours: int = 48
    top_n_cities: int = 50

    # Paths
    base_dir: Path = Path(__file__).parent.parent
    data_dir: Path = base_dir / "data"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
