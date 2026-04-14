# India Travel Planner — Multi-Leg Journey Optimizer

An intelligent travel planner that **combines** flights, trains, buses, and last-mile autos into a single door-to-door journey for India. It plans the kind of trip no other tool plans well today:

```
Ranchi → (auto) → IXR → (flight 6E234) → BLR → (transfer) → SBC → (train 16592) → HPT → (auto) → Hampi
```

It factors in connection risk (airport↔station buffer + historical delay), real last-mile cost, per-leg reliability, and true door-to-door totals. The vision lives in [`docs/travel-planner-india.md`](docs/travel-planner-india.md).

## What's different

| Capability | Google Maps | Ixigo / MMT | Rome2Rio | **This tool** |
|------------|-------------|-------------|----------|---------------|
| Multi-mode combinations | Poor for India | No | Yes (poor data) | **Yes** |
| Connection feasibility + buffer | No | No | No | **Yes** |
| Delay-aware risk | No | Partial | No | **Yes** |
| Last-mile always included | No | No | Partial | **Yes** |
| True door-to-door cost breakdown | No | No | No | **Yes** |
| Disruption replanning | No | No | No | **Yes** |

## Tech stack

- **Backend:** Python 3.11 + FastAPI + SQLAlchemy (SQLite), managed with **uv** (`pyproject.toml` + `uv.lock`, existing `.venv`)
- **Routing:** custom Connection Scan Algorithm with a shared multi-hub pool and synthetic transfer edges (see `app/routing/connection_scan.py` + `app/services/journey_planner.py`)
- **Frontend:** Next.js 16 + React 19 + Tailwind v4, managed with **pnpm**
- **Data:** curated JSON seeds under `data/seeds/` (trains, flights, buses, transfer times, popular pairs); optional harvesters under `scripts/` for Ixigo / RailRadar / RedBus

## Installation

Prerequisites: [uv](https://docs.astral.sh/uv/) and [pnpm](https://pnpm.io).

```bash
cd travel-planner-india

uv sync                        # creates .venv + uv.lock
pnpm -C frontend install       # installs pnpm deps
uv run python -m app.init_db   # seeds cities, airports, stations, routes, transfers
```

## Running

```bash
bash run-all.sh                # both servers on :8000 and :3000
# or individually:
uv run uvicorn app.main:app --reload --port 8000
pnpm -C frontend dev
```

Open `http://localhost:3000` for the UI and `http://localhost:8000/docs` for the auto-generated API reference.

## Testing

```bash
uv run pytest                  # backend — 17 tests at last count
pnpm -C frontend build         # turbopack build
pnpm -C frontend exec tsc --noEmit   # TypeScript typecheck
```

## Project structure

```
travel-planner-india/
├── app/
│   ├── api/              # FastAPI routers (search, routes, cities, stations, airports)
│   ├── models/           # SQLAlchemy models (city, station, airport, route, transfer_time)
│   ├── routing/          # connection_scan.py — CSA implementation
│   ├── scrapers/         # BS4/playwright scrapers (dev-only)
│   └── services/
│       ├── journey_planner.py  # graph builder + multi-leg search orchestration
│       ├── connection_risk.py  # recommended-buffer calculation
│       ├── geospatial.py       # haversine, nearby-hub queries
│       └── data_importers.py   # harvester → DB adapters
├── data/
│   ├── seeds/            # curated JSON (trains, flights, buses, transfer_times, popular_pairs)
│   └── travel_planner.db # generated SQLite
├── scripts/              # ad-hoc harvesters and sync tools
├── tests/                # pytest suite
├── frontend/
│   ├── app/              # Next.js pages: /, /results, /journey/[id]
│   └── components/       # SearchForm, JourneyCard, RouteVisualization, CostBreakdownRow,
│                         # ConnectionRiskBadge, ReliabilityBar, PopularRoutes,
│                         # AlternativeDatesStrip, DisruptionReplan, …
└── docs/                 # vision, roadmap, research
```

## API endpoints

All endpoints are under `/api/v1`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/search` | Multi-leg journey search. Query: `from`, `to`, `date`, `preference` (fastest / cheapest / balanced / reliable), `max_transfers`, `max_journeys`. |
| `GET`  | `/locations?q=…` | Autocomplete across cities / stations / airports. |
| `GET`  | `/cities`, `/stations`, `/airports` | List endpoints. |
| `GET`  | `/routes/popular?limit=…` | Curated popular pairs for the home page. |
| `GET`  | `/routes/popular/{index}/plan` | Run the planner for a popular pair. |
| `GET`  | `/journeys/{id}` | Retrieve a previously-returned journey by its deterministic id (30-min LRU). |
| `GET`  | `/journeys/{id}/alternatives?window=7` | Daily cheapest totals ±window/2 days. |
| `POST` | `/journeys/{id}/replan?exclude_vehicle_id=…` | Re-plan the same search excluding a disrupted leg. |

### Example

```bash
curl "http://localhost:8000/api/v1/search?from=Ranchi&to=Hampi&date=2026-05-01&preference=balanced&max_journeys=3"
```

Returns journeys containing `cost_breakdown`, `connection_risks`, per-leg `reliability_score`, per-leg booking deep-links, and a stable `journey_id` suitable for `/journey/{id}` deep-linking.

```json
{
  "journeys": [
    {
      "journey_id": "5fa0da5c006ef31b",
      "rank": 1,
      "total_cost": 6956,
      "total_duration_minutes": 760,
      "transfers": 3,
      "reliability_score": 0.58,
      "legs": [
        {"mode": "auto",     "from_name": "Ranchi",                   "to_name": "Birsa Munda",             "cost": 90,   "duration_minutes": 15},
        {"mode": "flight",   "from_name": "IXR",                      "to_name": "BLR",                     "cost": 5200, "flight_train_bus_no": "6E234"},
        {"mode": "transfer", "from_name": "Kempegowda International", "to_name": "Bangalore City Junction", "cost": 330},
        {"mode": "train",    "from_name": "SBC",                      "to_name": "HPT",                     "cost": 650,  "flight_train_bus_no": "16592"},
        {"mode": "auto",     "from_name": "Hospet Junction",          "to_name": "Hampi",                   "cost": 156}
      ],
      "cost_breakdown": {
        "tickets": 5850, "last_mile": 650,
        "booking_fees": 156, "meals_incidentals": 300,
        "total": 6956
      },
      "connection_risks": [],
      "booking_links": {
        "per_leg": [
          {"mode": "flight", "vehicle_id": "6E234",  "url": "https://www.ixigo.com/flights?flightNumber=6E234"},
          {"mode": "train",  "vehicle_id": "16592",  "url": "https://www.irctc.co.in/nget/train-search?trainNumber=16592"}
        ]
      }
    }
  ],
  "metadata": {
    "origin_hubs":        [{"type": "station", "code": "RNC"}, {"type": "airport", "code": "IXR"}],
    "destination_hubs":   [{"type": "station", "code": "HPT"}],
    "transit_hubs_considered": ["NDLS", "DEL", "BOM", "BLR", "HYD", "MAA", "CCU", "AMD", "COK"],
    "connection_pool_size": 279
  }
}
```

## How it works

1. Resolve origin and destination cities (`app/services/journey_planner.py:_find_city`).
2. Gather nearby stations/airports within a radius (`GeospatialService.find_nearby_*`), then enrich the hub set with the top-8 transit hubs (DEL, BOM, BLR, HYD, MAA, CCU, AMD, COK).
3. Build one connection pool covering:
   - scheduled flights/trains/buses between any two hubs in that set;
   - synthetic `transfer` edges for airport↔station moves within the same city, weighted by the `TransferTime` table (typical / p90 / recommended buffer);
   - synthetic `last-mile` edges between city centroids and hubs for bus↔flight/train stitching.
4. Run the Connection Scan Algorithm (`app/routing/connection_scan.py`) across every `(origin hub, destination hub)` pair, preserving buffer feasibility.
5. Deduplicate by leg signature, rank by user preference (cheapest / fastest / balanced / reliable), and assemble each journey dict with `cost_breakdown`, `connection_risks`, per-leg `reliability_score`, booking deep-links, and a deterministic `journey_id`.

## Data

Data lives in `data/seeds/*.json` (reviewable, diffable). Extend by editing the JSON and re-running `uv run python -m app.init_db`.

The `scripts/` directory contains optional harvesters (Ixigo / RailRadar / RedBus) for when you want to refresh from live sources; they write JSON that `app/services/data_importers.py` imports into the DB. None of them are on the demo path — the seed files are the source of truth for the MVP.

## Disclaimer

Development and educational use only. Web scraping is for MVP validation; a production deployment needs official APIs and carrier partnerships.

## License

MIT
