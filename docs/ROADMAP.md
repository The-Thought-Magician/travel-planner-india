# India Travel Planner - Roadmap

## MVP (Phase 1) - Current Focus

**Timeline**: 4-6 weeks

**Scope**:
- [x] Project setup and architecture
- [x] Database models (cities, stations, airports, routes)
- [x] Basic FastAPI backend
- [x] Connection Scan Algorithm implementation
- [ ] Scrapers for train/flight data
- [ ] Seed data for top 50 cities
- [ ] Basic search endpoint working
- [ ] Simple web UI (optional)

**Success Criteria**:
- User can search "Ranchi to Hampi"
- Returns 3-5 journey options combining flight + train
- Shows cost, duration, and basic reliability
- Links to booking sites

## Phase 2: Complete Coverage

**Timeline**: 8-12 weeks after MVP

**Features**:
- Add bus routes (major intercity)
- Expand to 200+ cities
- Real last-mile estimates (Ola/Uber integration)
- Connection risk warnings
- Mobile app (React Native)
- User accounts and saved journeys

**Technical**:
- PostgreSQL + PostGIS for spatial queries
- Redis for caching
- Daily data refresh jobs

## Phase 3: Intelligence Layer

**Timeline**: 3-4 months after Phase 2

**Features**:
- Historical delay data collection
- Connection feasibility scores
- Disruption alerts and replanning
- Price trend predictions
- "Flexible date" recommendations

## Phase 4: Full Platform

**Features**:
- Direct booking integration
- Payment gateway
- Loyalty program integration
- Social features (group trip planning)
- B2B API for travel agents

## Open Questions

1. **Business model**:
   - Freemium (free search, paid booking)?
   - Affiliate commission?
   - B2B SaaS for travel agents?
   - All of the above?

2. **Data partnerships**:
   - Contact IRCTC for official API access?
   - Partnership with airlines for direct data?
   - Use established aggregators (Amadeus, Sabre)?

3. **Geographic expansion**:
   - Start with top 50 cities?
   - Focus on specific corridors (Delhi-South, Mumbai-West)?
   - Pan-India from day 1?

4. **Last-mile integration**:
   - Just estimates (MVP)?
   - Ola/Uber API integration?
   - Partner with local cab operators?
