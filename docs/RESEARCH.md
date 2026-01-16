# Research Notes - India Travel Planner

## Data Sources Research (Development Scraping Only)

### Train Data

| Source | Method | Status | Notes |
|--------|--------|--------|-------|
| **erail.in** | Web scraping | Recommended | HTML-based, easier to scrape; has schedules and routes |
| **railradar.in** | API available | Good | Provides train status, has docs at railradar.in/docs |
| **NTES** | Scraping | Difficult | Official but requires authentication; no public API |
| **indianrailapi.com** | Third-party API | Available | Free tier available, but rate-limited |
| **Kaggle Datasets** | Static CSV | Good for MVP | [Indian Railways Schedule Data](https://www.kaggle.com/datasets/bhavyarajdev/indian-railways-schedule-prices-availability-data) |

**Recommended for MVP**:
1. Use Kaggle dataset for static schedules (top 100 routes)
2. Implement erail.in scraper for dynamic queries
3. Add railradar.in for live status (Phase 2)

### Flight Data

| Source | Method | Status | Notes |
|--------|--------|--------|-------|
| **AviationStack** | API | Free tier available | 100 requests/month free; good for global flights |
| **Ixigo** | Scraping | Difficult | Heavy JavaScript; requires Playwright/Selenium |
| **MakeMyTrip** | Scraping | Difficult | Also JS-heavy; see [scraper repo](https://github.com/andrew-geeks/MakeMyTrip-scraper) |
| **Cleartrip** | Scraping | Moderate | Some HTML content available |
| **Skyscanner** | API | Paid | Has rapid API alternatives |
| **Kaggle Datasets** | Static CSV | Good for MVP | [Flights in India](https://www.kaggle.com/datasets/dhairya903/flights-in-india) |

**Recommended for MVP**:
1. Use static route database (top 50 city pairs)
2. AviationStack free tier for validation
3. Ixigo scraper with Playwright (Phase 2)

### Bus Data

| Source | Method | Status | Notes |
|--------|--------|--------|-------|
| **RedBus** | Scraping | Very difficult | No public API; heavily protected |
| **AbhiBus** | Scraping | Difficult | Similar to RedBus |
| **State RTC sites** | Mixed | Varies | Some have PDF schedules, others nothing |
| **RailYatri** | Scraping | Difficult | Has train+bus info |

**Recommended for MVP**:
1. Skip buses in initial version
2. Add major intercity routes manually (top 10)
3. Phase 2: Partner with operators or use commercial APIs

### Station/Airport Data

| Source | Format | Notes |
|--------|--------|-------|
| **Kaggle - Airports in India** | CSV | 32.6 kB, has coordinates |
| **OpenFlights** | CSV | Global database includes India |
| **Kaggle - Top 500 Cities** | CSV | Has lat/lon, state info |

**Recommended**: Use Kaggle datasets directly; create seed script.

## Routing Algorithm Research

### Connection Scan Algorithm (CSA)

**Paper**: [Connection Scan Algorithm](https://arxiv.org/pdf/1703.05997) by Dibbelt et al. (2018)

**Key Advantages**:
- O(m + n) complexity where m = connections, n = stations
- Single pass through sorted connections
- Very fast for public transit queries

**Implementation Resources**:
- [learning-pt-routing](https://github.com/jlieberherr/learning-pt-routing) - Educational CSA in Python
- [pymmrouting](https://github.com/tumluliu/pymmrouting) - Multimodal routing package

**For Our Use Case**:
- Modified CSA for multi-modal (flight + train + bus)
- Add connection feasibility checks (buffer times)
- Multi-criteria optimization (cost/time/reliability)

### Multi-Criteria Optimization

**Approaches**:
1. **Weighted sum**: Combine criteria with weights
2. **Pareto frontier**: Return non-dominated options
3. **Label-setting**: Track multiple labels per node

**For MVP**: Weighted sum based on user preference

## Delay Data & Reliability

### Sources
- **NTES**: Historical running status (scrape over time)
- **RailYatri**: Has some reliability scores
- **Crowdsourcing**: User reports (future)

### For MVP
- Use static reliability scores:
  - Flights: 85% (domestic), 90% (major routes)
  - Trains: 75% (express), 60% (mail)
  - Buses: 70% (estimated)

## Last-Mile Estimation

### Data Sources
- **Ola/Uber APIs**: Real-time estimates (requires API keys)
- **City auto fare charts**: Publicly available
- **Google Maps**: Distance matrix API (paid)

### For MVP
- City-specific base rates + per-km rates
- Use flat distances for major cities
- Example: Auto ₹25 base + ₹15/km

## Legal Considerations

### Scraping Legality (India)
- No specific anti-scraping laws
- Terms of Service violations are civil matters
- **Best practice**: Use official APIs where available
- **For development**: Low-volume scraping is generally tolerated

### Disclaimer to Include
```
This project is for development and educational purposes only.
Data is scraped from public sources and may not be accurate.
For production use, please establish partnerships with official
data providers and obtain necessary licenses.
```

## References

1. [CSA Paper](https://arxiv.org/pdf/1703.05997)
2. [Multimodal Journey Planning Research](https://www.researchgate.net/publication/348046789_Implementation_of_connection_scan_algorithm_in_tourism_intermodal_transportation_journey_planner_a_case_study)
3. [learning-pt-routing (GitHub)](https://github.com/jlieberherr/learning-pt-routing)
4. [pymmrouting (GitHub)](https://github.com/tumluliu/pymmrouting)
5. [MakeMyTrip Scraper (GitHub)](https://github.com/andrew-geeks/MakeMyTrip-scraper)
6. [RailRadar API Docs](https://railradar.in/docs)
7. [Kaggle - Indian Railways Data](https://www.kaggle.com/datasets/bhavyarajdev/indian-railways-schedule-prices-availability-data)
8. [Kaggle - Airports in India](https://www.kaggle.com/datasets/shivammittal274/airports-in-india/data)
