# Idea: India Travel Planner - Multi-Leg Journey Optimizer

## Overview

A travel planning tool that solves the **complete journey problem** in India - finding the optimal *combination* of flights, trains, buses, and last-mile transport (auto/cab) to get from any point A to any point B. Not just comparing modes, but intelligently combining them.

## The Core Problem

**Existing tools compare. We need to combine.**

When traveling from Ranchi to Hampi, for example, no single mode works well:
- No direct flight
- No direct train
- No reasonable bus

The real journey might be:
```
Ranchi → (flight) → Bangalore → (train) → Hospet → (auto) → Hampi
   or
Ranchi → (train) → Howrah → (train) → Hospet → (auto) → Hampi
   or
Ranchi → (flight) → Hyderabad → (bus) → Hampi
```

**No tool today tells you which combination is cheapest, fastest, or most reliable.**

### What Users Currently Do

1. Open Google Maps - see it doesn't understand Indian trains/buses well
2. Open IRCTC - search for direct trains (often none exist)
3. Open Ixigo - check flights to nearby airports
4. Mentally calculate: "If I land at 2 PM, can I catch the 4 PM train?"
5. Open RedBus - check if bus is better than train for the last leg
6. Wonder about delays: "What if my flight is late and I miss the train?"
7. Forget about auto/cab cost from station to actual destination
8. Give up and overpay for a suboptimal route

This process takes hours and still misses better options.

## Problem Statement

### 1. No Multi-Leg Journey Planning
- Ixigo/MakeMyTrip show flights OR trains OR buses separately
- No tool says: "Take 6 AM flight to BLR, then 11 AM train to Hospet, then auto - total ₹4,500, 9 hours"
- Rome2Rio attempts this but has poor India data and misses local operators

### 2. Connection Risk is Ignored
- If your flight lands at 2 PM, is the 3:30 PM train safe to book?
- What's the historical delay of that flight?
- How long to get from airport to railway station?
- Nobody calculates this - users guess and sometimes miss connections

### 3. Last Mile is Invisible
- Journey doesn't end at "Hospet Junction" - it ends at "Hampi"
- That's another 13 km and ₹300-500 in auto
- No tool includes this in total cost/time

### 4. True Cost is Hidden
- Flight: ₹3,000 + cab to airport ₹400
- Train: ₹800 + auto to station ₹150
- Bus: ₹600 but arrives at 4 AM (need ₹500 hotel wait)
- Actual cheapest option ≠ lowest ticket price

### 5. Reliability Compounds in Multi-Leg Journeys
- Single train delayed = inconvenience
- Flight delayed in a Flight→Train→Auto journey = missed connections, rebooking chaos
- Need reliability scores AND connection buffer recommendations

## Market Gap

| Capability | Google Maps | Ixigo | MakeMyTrip | Rome2Rio | **Our Tool** |
|------------|-------------|-------|------------|----------|--------------|
| Multi-mode combinations | Poor for India | No | No | Yes (poor data) | **Yes** |
| Connection feasibility | No | No | No | No | **Yes** |
| Delay risk in planning | No | Partial | No | No | **Yes** |
| Last-mile included | No | No | No | Partial | **Yes** |
| True door-to-door cost | No | No | No | No | **Yes** |
| Indian transport coverage | Poor | Good | Good | Poor | **Good** |

### Why Doesn't This Exist?

1. **Data fragmentation**: Flights, trains, buses, autos are all separate ecosystems
2. **Algorithmic complexity**: Multi-modal journey planning with time constraints is a hard optimization problem
3. **Connection risk modeling**: Requires historical delay data + transfer time estimation
4. **Last-mile variability**: Auto/cab costs vary by city, time, demand

## Solution

An intelligent journey planner that:

1. **Models India as a transport graph** - airports, railway stations, bus stands, cities as nodes; all transport options as edges with time, cost, reliability attributes
2. **Finds optimal multi-leg paths** - using graph algorithms that optimize for user preference (cheapest/fastest/most reliable)
3. **Calculates connection feasibility** - based on historical delays and transfer times
4. **Includes last-mile** - estimates auto/cab cost and time for first and last legs
5. **Shows complete journeys** - "Door to door: ₹5,200, 11 hours, 94% on-time probability"

## Core Features

### 1. Complete Journey Search
```
FROM: Ranchi (home address or "Ranchi")
TO: Hampi (or "Virupaksha Temple, Hampi")
DATE: 15 Feb 2026
PREFERENCE: [Cheapest] [Fastest] [Most Reliable] [Balanced]
```

**Output:**
```
Option 1: ₹4,850 | 10h 30m | 89% reliable
├── Auto: Home → Ranchi Airport (₹250, 30 min)
├── Flight: 6E 234 Ranchi → Bangalore (₹3,200, 2h 15m) - 92% on-time
├── Buffer: 2h recommended (airport to station)
├── Train: 16592 Hampi Exp Bangalore → Hospet (₹450, 7h) - 85% on-time
└── Auto: Hospet Junction → Hampi (₹350, 25 min)

Option 2: ₹3,100 | 18h | 78% reliable
├── Auto: Home → Ranchi Station (₹150, 20 min)
├── Train: 18615 Hatia-Ypr Exp → Bangalore (₹1,100, 26h) - 72% on-time
├── Bus: Bangalore → Hampi (₹800, 7h) - overnight sleeper
└── Walk: Bus stop → Hampi center (10 min)

Option 3: ₹6,200 | 7h 45m | 95% reliable
├── Cab: Home → Ranchi Airport (₹350, 30 min)
├── Flight: 6E 234 Ranchi → Bangalore (₹3,200, 2h 15m)
├── Flight: UK 852 Bangalore → Hubli (₹2,100, 1h)
└── Cab: Hubli Airport → Hampi (₹1,500, 1h 30m)
```

### 2. Connection Intelligence
- "⚠️ This train is delayed >1 hour on 40% of days. Consider 2h buffer instead of 1h"
- "✓ Safe connection: Flight usually arrives by 2:15 PM, train departs 5:30 PM"
- "❌ Risky: Only 45 min between flight landing and train departure"

### 3. Reliability Scores Per Leg
- Each leg shows historical on-time percentage
- Overall journey reliability = probability all connections work
- Factor in: mode reliability, connection buffer, day of week, season

### 4. True Cost Breakdown
```
Ticket costs:     ₹3,650
Platform fees:    ₹50
Last-mile:        ₹600
Meals (est.):     ₹200
────────────────────────
Total:            ₹4,500
```

### 5. Alternative Dates View
"Same journey on Thursday is ₹1,200 cheaper and 15% more reliable"

### 6. Disruption Replanning
During journey: "Your flight is delayed 2 hours. Here are alternative connections from Bangalore..."

## Technical Architecture

### The Transport Graph

```
Nodes:
- Airports (140+ in India)
- Major railway stations (8,000+)
- Bus stands (major ones in each city)
- Cities (as abstract nodes for last-mile)

Edges:
- Flights (with schedule, price, delay history)
- Trains (with schedule, price, delay history)
- Buses (with schedule, price, operator rating)
- Auto/Cab estimates (city-specific, time-based)
- Walking/Metro (for airport↔station transfers)
```

### Multi-Modal Routing Algorithm

Based on research into [Connection Scan Algorithm](https://www.researchgate.net/publication/324558562_Multimodal_Dynamic_Journey_Planning) and [Multi-criteria optimization](https://drops.dagstuhl.de/storage/01oasics/oasics-vol106-atmos2022/OASIcs.ATMOS.2022.14/OASIcs.ATMOS.2022.14.pdf):

1. Build time-expanded graph with all departures for the day
2. Apply modified Dijkstra/A* with multi-criteria optimization (time, cost, reliability, transfers)
3. Prune infeasible connections (not enough transfer time)
4. Rank by user preference
5. Return Pareto-optimal set of journeys

### Data Sources

**Flights:**
- Skyscanner/Amadeus APIs for schedules and prices
- FlightStats/OAG for delay history
- Airport transfer time estimates (crowdsourced + maps)

**Trains:**
- Indian Rail API / eRail API for schedules
- NTES for live running status
- Self-collected delay history (poll every train daily)
- Station-to-station transfer times

**Buses:**
- RedBus API, AbhiBus API
- State RTC APIs where available
- Operator reliability from reviews + live tracking

**Last Mile:**
- Ola/Uber API estimates (or build estimation model)
- City-specific auto fare charts
- Google Maps for transfer walking/driving times

**Transfer Points:**
- Airport to nearest railway station (time + cost)
- Railway station to bus stand
- Metro connections in major cities

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        User Interface                           │
│                   (Web / Mobile App)                            │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                      API Gateway                                 │
│              /search, /journey/{id}, /alerts                    │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                   Journey Planner Engine                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │   Graph     │  │  Router     │  │  Connection Risk        │  │
│  │   Builder   │  │  (CSA/A*)   │  │  Calculator             │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                     Data Layer                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │
│  │ Flights  │  │ Trains   │  │ Buses    │  │ Last-Mile      │   │
│  │ Cache    │  │ Cache    │  │ Cache    │  │ Estimates      │   │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘   │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                  Data Collection Workers                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐   │
│  │ Flight   │  │ Train    │  │ Bus      │  │ Delay History  │   │
│  │ Fetcher  │  │ Fetcher  │  │ Fetcher  │  │ Collector      │   │
│  └──────────┘  └──────────┘  └──────────┘  └────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Tech Stack

- **Backend**: Python (FastAPI) - great for data processing and ML
- **Routing Engine**: Custom implementation based on CSA, or extend OpenTripPlanner
- **Database**:
  - PostgreSQL + PostGIS (spatial queries for nearby stations)
  - TimescaleDB (delay time-series)
  - Redis (real-time schedule cache)
- **Frontend**: Next.js (web), React Native (mobile)
- **ML**: scikit-learn/XGBoost for delay prediction

## User Stories

1. **Budget traveler**: "Show me the cheapest way to get from Patna to Goa for under ₹3,000, I don't mind if it takes 30 hours"

2. **Business traveler**: "I need to reach Coimbatore from Delhi by 10 AM tomorrow with 95%+ reliability - show me options"

3. **Family trip planner**: "We're 4 people going from Mumbai to Hampi. Show combined journey costs and comfortable options"

4. **Spontaneous traveler**: "What's the fastest way to reach Manali from Bangalore right now?"

5. **Connection anxiety**: "I'm considering Flight→Train combo. What's the risk of missing my train if the flight is delayed?"

## MVP Scope

### Phase 1: Core Multi-Leg Search (MVP)
- Support top 50 cities as origins/destinations
- Flight + Train combinations (most common need)
- Basic last-mile estimates (flat rates by city)
- Show 3-5 journey options ranked by price/time
- No booking - link to respective platforms
- Web only

### Phase 2: Complete Coverage
- Add buses to the mix
- Expand to 200+ cities
- Real last-mile estimates (Ola/Uber integration or model)
- Connection risk warnings (basic)
- Mobile app

### Phase 3: Intelligence Layer
- Historical delay data collection and display
- Connection feasibility scores
- Disruption alerts and replanning
- Price trend predictions

### Phase 4: Full Platform
- Direct booking (aggregate tickets)
- Saved journeys and preferences
- Social features (group trip planning)

## Key Differentiators

1. **Multi-leg combinations**: The core feature no one else does well for India
2. **Connection intelligence**: "Is this connection safe?" with data to back it
3. **True door-to-door**: Last mile included, not an afterthought
4. **India-specific**: Built for Indian transport quirks (tatkal, waitlists, RTCs, etc.)

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Algorithm complexity | Start simple (2-leg journeys), expand gradually |
| Data freshness | Real-time APIs + aggressive caching + fallbacks |
| Last-mile estimation errors | Conservative estimates, user feedback loop |
| Cold start for delay data | Start with publicly available data, build over time |
| User trust | Show data sources, be transparent about estimates |

## Research Sources

- [Multimodal Dynamic Journey Planning](https://www.researchgate.net/publication/324558562_Multimodal_Dynamic_Journey_Planning) - Algorithm foundations
- [Connection Scan Algorithm](https://drops.dagstuhl.de/storage/01oasics/oasics-vol106-atmos2022/OASIcs.ATMOS.2022.14/OASIcs.ATMOS.2022.14.pdf) - Efficient routing
- [Trainline Combined Journeys](https://support.thetrainline.com/en/support/solutions/articles/78000000791-through-journeys-and-combined-journeys) - How European platforms handle this
- [Google Route Optimization API](https://developers.google.com/maps/documentation/route-optimization/overview) - Reference architecture
- [Indian Rail API](https://indianrailapi.com/api-collection) - Train data source
- [DMRC Last Mile Connectivity](https://metrorailnews.in/dmrc-to-introduce-last-mile-connectivity-service/) - Last mile integration examples

## Open Questions

1. **Starting scope**: Top 50 cities enough for MVP? Or focus on specific corridors (Delhi-South India)?
2. **Booking model**: Stay as planner only, or aggregate bookings eventually?
3. **Last-mile depth**: Just estimates, or integrate with Ola/Uber for actual booking?
4. **Offline support**: Cache common routes for areas with poor connectivity?
5. **B2B opportunity**: Travel agents might pay for this - explore early?

---

*Created: 2026-01-16*
*Updated: 2026-01-16*
*Status: Draft - Pending Refinement*
