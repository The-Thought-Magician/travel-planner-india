# India Travel Planner - Multi-Leg Journey Optimizer

An intelligent travel planning tool that finds optimal combinations of flights, trains, buses, and last-mile transport for journeys within India.

## Overview

Existing travel platforms compare transport modes separately. This tool **combines** them intelligently to solve multi-leg journey problems like:

```
Ranchi → (flight) → Bangalore → (train) → Hospet → (auto) → Hampi
```

## MVP Scope (Phase 1)

- **Top 50 cities** as origins/destinations
- **Flight + Train combinations** (most common use case)
- Basic last-mile estimates (flat rates by city)
- 3-5 journey options ranked by price/time
- Web interface with link-outs to booking platforms
- **No paid APIs** - development scraping only

## Tech Stack

- **Backend**: Python 3.11+ with FastAPI
- **Routing**: Custom Connection Scan Algorithm (CSA) implementation
- **Database**: SQLite (MVP), PostgreSQL + PostGIS (production)
- **Scraping**: requests, BeautifulSoup4, playwright (for JS-heavy sites)
- **Frontend**: Next.js 14 (planned)

## Data Sources (Development Scraping)

| Transport | Source | Method |
|-----------|--------|--------|
| **Flights** | Ixigo, MakeMyTrip | BeautifulSoup/playwright |
| **Trains** | erail.in, NTES | API-style scraping |
| **Stations** | Indian Railways static datasets | Kaggle/GitHub CSV |
| **Airports** | OpenFlights, Kaggle | Static CSV |
| **Last-mile** | City-based fare charts | Configured estimates |

## Installation

Prerequisites: [uv](https://docs.astral.sh/uv/) for Python and [pnpm](https://pnpm.io) for the frontend.

```bash
cd travel-planner-india

# Backend deps (creates .venv/ and uv.lock)
uv sync

# Frontend deps
pnpm -C frontend install

# Initialize database (seeds cities, airports, stations, routes)
uv run python -m app.init_db
```

## Running

```bash
# Both backend and frontend
bash run-all.sh

# Or individually:
uv run uvicorn app.main:app --reload --port 8000
pnpm -C frontend dev

# API docs
open http://localhost:8000/docs
```

## Testing

```bash
uv run pytest
pnpm -C frontend build  # type-check + build
```

## Project Structure

```
travel-planner-india/
├── app/
│   ├── api/          # FastAPI endpoints
│   ├── models/       # Database models
│   ├── scrapers/     # Data collection modules
│   ├── routing/      # Journey planning algorithms
│   └── services/     # Business logic
├── data/             # Static datasets and cache
├── tests/            # Test suite
└── docs/             # Additional documentation
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /search` | Multi-modal journey search |
| `GET /stations` | List railway stations |
| `GET /airports` | List airports |
| `GET /cities` | List supported cities |

## Example Request

```bash
curl "http://localhost:8000/search?from=Ranchi&to=Hampi&date=2026-02-15&preference=cheapest"
```

## Example Response

```json
{
  "options": [
    {
      "rank": 1,
      "total_cost": 4850,
      "total_duration": "10h 30m",
      "reliability": 0.89,
      "legs": [
        {"mode": "auto", "from": "Home", "to": "Ranchi Airport", "cost": 250, "duration": "30min"},
        {"mode": "flight", "from": "IXR", "to": "BLR", "cost": 3200, "duration": "2h 15m", "flight": "6E 234"},
        {"mode": "train", "from": "SBC", "to": "HPT", "cost": 450, "duration": "7h", "train": "16592"},
        {"mode": "auto", "from": "Hospet Junction", "to": "Hampi", "cost": 350, "duration": "25min"}
      ]
      "booking_links": {"flight": "...", "train": "..."}
    }
  ]
}
```

## Disclaimer

This project is for **development and educational purposes only**. Web scraping is used for MVP development to validate the concept. For production, official APIs and partnerships with transport providers should be established.

## License

MIT

## Sources

- [Indian Railways Datasets (Kaggle)](https://www.kaggle.com/datasets/bhavyarajdev/indian-railways-schedule-prices-availability-data)
- [Airports in India (Kaggle)](https://www.kaggle.com/datasets/shivammittal274/airports-in-india/data)
- [CSA Algorithm Paper](https://arxiv.org/pdf/1703.05997)
- [MakeMyTrip Scraper (GitHub)](https://github.com/andrew-geeks/MakeMyTrip-scraper)
- [learning-pt-routing (GitHub)](https://github.com/jlieberherr/learning-pt-routing)
- [pymmrouting (GitHub)](https://github.com/tumluliu/pymmrouting)
