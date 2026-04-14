"""Journey planner service — orchestrates multi-leg search and routing.

Key design points:

- For each search we build a *single* connection pool that includes routes
  touching the origin hubs, destination hubs, and a fixed set of top-8 transit
  hubs (DEL, BOM, BLR, HYD, MAA, CCU, AMD, COK). That's what lets the Connection
  Scan Algorithm find paths like Ranchi→BLR (flight) → SBC (transfer) → Hospet
  (train) in one search.
- Airport↔station moves within a city are injected as synthetic ``transfer``
  Connections whose cost and duration come from the TransferTime table.
- Bus routes are keyed by city name; flights by airport IATA; trains by station
  code. Buses at a city hop into the same "city node" used by transfer edges
  so a flight→bus handoff works.
- Reliability is normalized to 0-1 throughout (on_time_percentage is divided
  by 100 where it came in as 0-100).
- Cost breakdown splits ticket cost, last-mile, booking fees, and meal
  incidentals so the UI can show true door-to-door cost.
"""

from datetime import date, datetime
from hashlib import sha1
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import City, Station, Airport, TrainRoute, FlightRoute, BusRoute
from app.routing.connection_scan import Connection, ConnectionScanAlgorithm, Journey
from app.services.geospatial import GeospatialService, Location
from app.services import connection_risk

# Top-8 transit hubs always included in the connection pool. These names come
# from the cities table; the corresponding airport/station codes are resolved
# at build-time.
TRANSIT_HUB_CITIES = ["Delhi", "Mumbai", "Bangalore", "Hyderabad",
                      "Chennai", "Kolkata", "Ahmedabad", "Kochi"]

# Booking-fee rates applied to ticket cost per mode
BOOKING_FEE_RATE = {"flight": 0.03, "train": 0.0, "bus": 0.01}


class JourneyPlanner:
    """Plan multi-modal journeys between two Indian cities."""

    def __init__(self, db: Optional[Session] = None) -> None:
        self.db = db if db else next(get_db())
        self.geo = GeospatialService(self.db)

    # ------------------------------------------------------------------ #
    # Public entrypoint
    # ------------------------------------------------------------------ #

    def find_journeys(
        self,
        from_city: str,
        to_city: str,
        travel_date: date | None = None,
        preference: str = "balanced",
        max_transfers: int = 3,
        max_journeys: int = 5,
        excluded_vehicle_ids: set[str] | None = None,
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """Top-level search. See module docstring.

        ``excluded_vehicle_ids`` lets callers re-plan around a disrupted leg —
        any Connection whose vehicle_id is in the set is dropped from the pool.
        """
        origin = self._find_city(from_city)
        destination = self._find_city(to_city)

        if not origin or not destination:
            return self._create_fallback_journeys(
                origin or City(name=from_city, state="Unknown", latitude=0, longitude=0, code=None),
                destination or City(name=to_city, state="Unknown", latitude=0, longitude=0, code=None),
            )

        origin_hubs = self._hubs_near(origin)
        dest_hubs = self._hubs_near(destination)
        transit_hubs = self._transit_hubs(exclude_city_ids={origin.id, destination.id})

        if not origin_hubs or not dest_hubs:
            return self._create_fallback_journeys(origin, destination)

        # All hub codes that can appear as edge endpoints in the connection pool
        all_hubs: List[Location] = list({(h.code, h.location_type): h for h in
                                         origin_hubs + dest_hubs + transit_hubs}.values())

        connections = self._build_connection_pool(all_hubs, origin, destination)
        if excluded_vehicle_ids:
            connections = [c for c in connections if c.vehicle_id not in excluded_vehicle_ids]
        if not connections:
            return self._create_fallback_journeys(origin, destination)

        csa = ConnectionScanAlgorithm(
            connections,
            min_connection_buffer=settings.min_connection_buffer_minutes,
        )

        # Search across every (origin hub, destination hub) pair, gather, rank.
        all_journeys: List[Journey] = []
        for from_loc in origin_hubs:
            if not from_loc.code:
                continue
            for to_loc in dest_hubs:
                if not to_loc.code or from_loc.code == to_loc.code:
                    continue
                found = csa.find_k_best(
                    from_code=from_loc.code,
                    to_code=to_loc.code,
                    k=max_journeys,
                    max_transfers=max_transfers,
                    preference=preference,
                )
                all_journeys.extend(found)

        if not all_journeys:
            return self._create_fallback_journeys(origin, destination)

        # Deduplicate by (ordered tuple of vehicle_ids) so we don't return
        # three cosmetic permutations of the same underlying path.
        seen_signatures: set[str] = set()
        unique_journeys: List[Journey] = []
        for j in all_journeys:
            sig = "|".join(f"{c.mode}:{c.vehicle_id}:{c.from_code}-{c.to_code}"
                           for c in j.connections)
            if sig in seen_signatures:
                continue
            seen_signatures.add(sig)
            unique_journeys.append(j)

        # Rank by chosen preference
        def rank(j: Journey) -> float:
            if preference == "cheapest":
                return float(j.total_cost)
            if preference == "fastest":
                return float(j.total_duration)
            if preference in ("most_reliable", "reliable"):
                return 1.0 - j.reliability
            return (j.total_cost / 10000.0 + j.total_duration / 1440.0 + (1 - j.reliability)) / 3

        unique_journeys.sort(key=rank)
        top = unique_journeys[:max_journeys]

        journey_dicts = []
        for idx, j in enumerate(top, start=1):
            d = self._journey_to_dict(j, origin, destination, preference, origin_hubs, dest_hubs)
            d["rank"] = idx
            d["journey_id"] = self._journey_id(origin.id, destination.id, travel_date, preference, idx)
            journey_dicts.append(d)

        metadata = {
            "origin_hubs": [{"type": h.location_type, "code": h.code, "name": h.name} for h in origin_hubs],
            "destination_hubs": [{"type": h.location_type, "code": h.code, "name": h.name} for h in dest_hubs],
            "transit_hubs_considered": [h.code for h in transit_hubs],
            "connection_pool_size": len(connections),
        }
        return journey_dicts, metadata

    # ------------------------------------------------------------------ #
    # Hub discovery
    # ------------------------------------------------------------------ #

    def _find_city(self, name: str) -> Optional[City]:
        return (
            self.db.query(City)
            .filter(City.name.ilike(name))
            .first()
            or self.db.query(City).filter(City.name.ilike(f"%{name}%")).first()
        )

    def _hubs_near(self, city: City, radius_stn: float = 50, radius_air: float = 100) -> List[Location]:
        if city.latitude is None or city.longitude is None:
            return []
        stations = self.geo.find_nearby_stations(city.latitude, city.longitude, radius_km=radius_stn, limit=3)
        airports = self.geo.find_nearby_airports(city.latitude, city.longitude, radius_km=radius_air, limit=2)
        return stations + airports

    def _transit_hubs(self, exclude_city_ids: set[int]) -> List[Location]:
        hubs: List[Location] = []
        for name in TRANSIT_HUB_CITIES:
            city = self.db.query(City).filter(City.name == name).first()
            if not city or city.id in exclude_city_ids:
                continue
            hubs.extend(self._hubs_near(city, radius_stn=40, radius_air=80))
        return hubs

    # ------------------------------------------------------------------ #
    # Connection pool
    # ------------------------------------------------------------------ #

    def _build_connection_pool(
        self,
        hubs: List[Location],
        origin: City,
        destination: City,
    ) -> List[Connection]:
        """Collect flight/train/bus routes that touch any of the hubs, plus
        synthetic airport↔station transfer edges per city."""
        airport_codes = {h.code for h in hubs if h.location_type == "airport"}
        station_codes = {h.code for h in hubs if h.location_type == "station"}

        # Also include origin/destination city names as bus endpoints, since
        # the bus table uses city names not codes.
        city_names = {origin.name, destination.name}
        for name in TRANSIT_HUB_CITIES:
            city_names.add(name)

        connections: List[Connection] = []

        # Flights — where both endpoints are in the hub set
        flights = (
            self.db.query(FlightRoute)
            .filter(
                FlightRoute.is_active == True,  # noqa: E712
                FlightRoute.from_airport_code.in_(airport_codes),
                FlightRoute.to_airport_code.in_(airport_codes),
            )
            .all()
        )
        for f in flights:
            connections.append(self._flight_to_connection(f))

        # Trains — both station endpoints in hub set
        trains = (
            self.db.query(TrainRoute)
            .filter(
                TrainRoute.is_active == True,  # noqa: E712
                TrainRoute.from_station_code.in_(station_codes),
                TrainRoute.to_station_code.in_(station_codes),
            )
            .all()
        )
        for t in trains:
            connections.append(self._train_to_connection(t))

        # Buses — either endpoint matches a hub city
        buses = (
            self.db.query(BusRoute)
            .filter(
                BusRoute.is_active == True,  # noqa: E712,
                BusRoute.from_city.in_(city_names),
                BusRoute.to_city.in_(city_names),
            )
            .all()
        )
        for b in buses:
            connections.append(self._bus_to_connection(b))

        # Synthetic transfer edges: for every hub pair in the same city where
        # we have both an airport and a station, allow a transfer hop.
        connections.extend(self._transfer_edges_for(hubs))

        # Bus↔city bridging: for each bus endpoint, emit a transfer edge linking
        # the city name to the closest station/airport in that city so a
        # flight→bus or train→bus chain can be built.
        connections.extend(self._city_bus_bridges(hubs, city_names))

        return connections

    def _transfer_edges_for(self, hubs: List[Location]) -> List[Connection]:
        """Airport↔station transfer Connections, driven by TransferTime data.

        We also always emit a generic 60min transfer edge if no data exists so
        the graph is still connected (reliability lowered accordingly)."""
        edges: List[Connection] = []
        # Group hubs by city (via nearest_city join on models — we use the
        # Location.city_id if set, otherwise skip). The Location dataclass only
        # carries city_id for stations/airports returned by GeospatialService.
        by_city: dict[int, list[Location]] = {}
        for h in hubs:
            if h.city_id is None:
                continue
            by_city.setdefault(h.city_id, []).append(h)

        for _city_id, city_hubs in by_city.items():
            for i, a in enumerate(city_hubs):
                for b in city_hubs[i + 1:]:
                    if not a.code or not b.code or a.code == b.code:
                        continue
                    if a.location_type == b.location_type:
                        continue  # don't connect station↔station or airport↔airport here
                    edges.append(self._make_transfer(a.code, b.code, a.name, b.name))
                    edges.append(self._make_transfer(b.code, a.code, b.name, a.name))
        return edges

    def _city_bus_bridges(self, hubs: List[Location], city_names: set[str]) -> List[Connection]:
        """Bridge bus endpoints (city-name nodes) to each hub in that city."""
        from datetime import time as _time
        edges: List[Connection] = []
        for h in hubs:
            if h.city_id is None or not h.code:
                continue
            city = self.db.query(City).get(h.city_id)
            if not city or city.name not in city_names:
                continue
            if city.latitude is None or city.longitude is None:
                continue
            # Use city.name as a code; cost ≈ last-mile estimate
            dist_km = self.geo.calculate_distance(city.latitude, city.longitude, h.latitude, h.longitude)
            cost = self.geo.estimate_last_mile_cost(city.id, max(1.0, dist_km))
            dur = max(15, int(dist_km * 3))  # 20 kmh avg urban transit
            for hour in (6, 10, 14, 18, 22):
                dep = _time(hour, 0)
                arr_h = (hour + dur // 60) % 24
                arr_m = dur % 60
                arr = _time(arr_h, arr_m)
                edges.append(Connection(
                    mode="transfer",
                    from_code=city.name,
                    to_code=h.code,
                    from_city=city.name,
                    to_city=h.name,
                    departure_time=dep,
                    arrival_time=arr,
                    cost=cost,
                    vehicle_id="LOCAL",
                    reliability=0.9,
                    duration_minutes=dur,
                ))
                edges.append(Connection(
                    mode="transfer",
                    from_code=h.code,
                    to_code=city.name,
                    from_city=h.name,
                    to_city=city.name,
                    departure_time=dep,
                    arrival_time=arr,
                    cost=cost,
                    vehicle_id="LOCAL",
                    reliability=0.9,
                    duration_minutes=dur,
                ))
        return edges

    def _make_transfer(self, from_code: str, to_code: str,
                       from_name: str, to_name: str) -> Connection:
        """Build a transfer Connection from TransferTime data (or a default)."""
        from datetime import time as _time
        info = connection_risk.lookup_transfer(self.db, from_code, to_code)
        if info:
            dur = info.buffer_minutes
            notes = info.notes or ""
        else:
            dur = 60
            notes = "estimated"
        # Emit the transfer across the day so CSA can pick a compatible slot
        # regardless of arrival time of the previous leg.
        cost = int(250 + dur * 3)  # cab-like fare heuristic
        connections = []
        for hour in (6, 10, 13, 16, 19, 22):
            dep = _time(hour, 0)
            arr_mins = hour * 60 + dur
            arr = _time((arr_mins // 60) % 24, arr_mins % 60)
            connections.append(Connection(
                mode="transfer",
                from_code=from_code,
                to_code=to_code,
                from_city=from_name,
                to_city=to_name,
                departure_time=dep,
                arrival_time=arr,
                cost=cost,
                vehicle_id=f"XFR-{from_code}-{to_code}",
                reliability=0.92,
                duration_minutes=dur,
            ))
        # Return just one — CSA handles feasibility checks
        return connections[0]

    # ------------------------------------------------------------------ #
    # Route → Connection converters
    # ------------------------------------------------------------------ #

    def _flight_to_connection(self, f: FlightRoute) -> Connection:
        return Connection(
            mode="flight",
            from_code=f.from_airport_code,
            to_code=f.to_airport_code,
            departure_time=f.departure_time,
            arrival_time=f.arrival_time,
            cost=int(f.price_avg or 0),
            vehicle_id=f.flight_no,
            reliability=self._norm_reliability(f.on_time_percentage),
            duration_minutes=f.duration_minutes,
            avg_delay_minutes=getattr(f, "avg_delay_minutes", None) or 0,
        )

    def _train_to_connection(self, t: TrainRoute) -> Connection:
        price = 500
        if t.pricing:
            price = int(t.pricing.get("3A") or t.pricing.get("SL") or t.pricing.get("CC") or 500)
        return Connection(
            mode="train",
            from_code=t.from_station_code,
            to_code=t.to_station_code,
            departure_time=t.departure_time,
            arrival_time=t.arrival_time,
            cost=price,
            vehicle_id=str(t.train_no),
            reliability=self._norm_reliability(t.on_time_percentage),
            duration_minutes=t.duration_minutes,
            avg_delay_minutes=t.avg_delay_minutes or 0,
        )

    def _bus_to_connection(self, b: BusRoute) -> Connection:
        # Rating is 0-5; normalise to reliability
        reliability = 0.7 if not b.rating else max(0.5, min(0.95, b.rating / 5.0))
        return Connection(
            mode="bus",
            from_code=b.from_city,
            to_code=b.to_city,
            from_city=b.from_city,
            to_city=b.to_city,
            departure_time=b.departure_time,
            arrival_time=b.arrival_time,
            cost=int(b.price_avg or 0),
            vehicle_id=b.operator,
            reliability=reliability,
            duration_minutes=b.duration_minutes,
        )

    @staticmethod
    def _norm_reliability(pct: float | None) -> float:
        """Normalize on-time percentage to 0-1 probability."""
        if pct is None:
            return 0.8
        return max(0.4, min(0.99, pct / 100.0 if pct > 1.5 else pct))

    # ------------------------------------------------------------------ #
    # Response assembly
    # ------------------------------------------------------------------ #

    def _journey_to_dict(
        self,
        journey: Journey,
        origin: City,
        destination: City,
        preference: str,
        origin_hubs: List[Location],
        dest_hubs: List[Location],
    ) -> Dict[str, Any]:
        legs: List[Dict[str, Any]] = []
        connection_risks: List[Dict[str, Any]] = []

        tickets_cost = 0
        last_mile_cost = 0
        total_duration = 0

        # -- origin last-mile leg (home → first hub) --
        first_conn = journey.connections[0]
        first_hub = self._hub_by_code(origin_hubs, first_conn.from_code)
        if (first_hub and origin.latitude is not None and origin.longitude is not None):
            origin_distance = self.geo.calculate_distance(
                origin.latitude, origin.longitude,
                first_hub.latitude, first_hub.longitude,
            )
        else:
            origin_distance = 10.0
        origin_lm_cost = self.geo.estimate_last_mile_cost(origin.id, origin_distance)
        origin_lm_dur = max(15, int(origin_distance * 3))
        legs.append({
            "mode": "auto",
            "from_name": origin.name,
            "to_name": first_hub.name if first_hub else first_conn.from_code,
            "from_code": origin.code,
            "to_code": first_conn.from_code,
            "cost": origin_lm_cost,
            "duration_minutes": origin_lm_dur,
            "distance_km": round(origin_distance, 1),
            "departure_time": None,
            "arrival_time": None,
            "reliability_score": 0.95,
        })
        last_mile_cost += origin_lm_cost
        total_duration += origin_lm_dur

        # -- transport legs, with inter-leg connection-risk assessments --
        prev_conn: Connection | None = None
        for conn in journey.connections:
            if prev_conn is not None and conn.mode != "transfer" and prev_conn.mode != "transfer":
                # Compute actual buffer between prev arrival and this departure
                prev_arr = prev_conn.arrival_time.hour * 60 + prev_conn.arrival_time.minute
                this_dep = conn.departure_time.hour * 60 + conn.departure_time.minute
                if this_dep < prev_arr:
                    this_dep += 24 * 60
                actual_buffer = this_dep - prev_arr
                info = connection_risk.lookup_transfer(self.db, prev_conn.to_code, conn.from_code)
                assessment = connection_risk.assess(
                    actual_minutes=actual_buffer,
                    transfer=info,
                    from_leg_reliability=prev_conn.reliability,
                    from_leg_avg_delay_min=prev_conn.avg_delay_minutes or 0,
                )
                connection_risks.append({
                    "between_legs": [len(legs) - 1, len(legs)],
                    "actual_buffer_minutes": assessment.actual_buffer_minutes,
                    "recommended_buffer_minutes": assessment.recommended_buffer_minutes,
                    "risk": assessment.risk,
                    "reason": assessment.reason,
                    "hub_from": prev_conn.to_code,
                    "hub_to": conn.from_code,
                })

            leg = {
                "mode": conn.mode,
                "from_name": conn.from_city or conn.from_code,
                "to_name": conn.to_city or conn.to_code,
                "from_code": conn.from_code,
                "to_code": conn.to_code,
                "cost": conn.cost,
                "duration_minutes": conn.duration_minutes,
                "departure_time": conn.departure_time.isoformat() if hasattr(conn.departure_time, "isoformat") else str(conn.departure_time),
                "arrival_time": conn.arrival_time.isoformat() if hasattr(conn.arrival_time, "isoformat") else str(conn.arrival_time),
                "flight_train_bus_no": conn.vehicle_id,
                "reliability_score": round(conn.reliability, 2),
            }
            legs.append(leg)
            if conn.mode == "transfer":
                last_mile_cost += conn.cost
            else:
                tickets_cost += conn.cost
            total_duration += conn.duration_minutes
            prev_conn = conn

        # -- destination last-mile leg --
        last_conn = journey.connections[-1]
        last_hub = self._hub_by_code(dest_hubs, last_conn.to_code)
        if (last_hub and destination.latitude is not None and destination.longitude is not None):
            dest_distance = self.geo.calculate_distance(
                destination.latitude, destination.longitude,
                last_hub.latitude, last_hub.longitude,
            )
        else:
            dest_distance = 10.0
        dest_lm_cost = self.geo.estimate_last_mile_cost(destination.id, dest_distance)
        dest_lm_dur = max(15, int(dest_distance * 3))
        legs.append({
            "mode": "auto",
            "from_name": last_hub.name if last_hub else last_conn.to_code,
            "to_name": destination.name,
            "from_code": last_conn.to_code,
            "to_code": destination.code,
            "cost": dest_lm_cost,
            "duration_minutes": dest_lm_dur,
            "distance_km": round(dest_distance, 1),
            "departure_time": None,
            "arrival_time": None,
            "reliability_score": 0.95,
        })
        last_mile_cost += dest_lm_cost
        total_duration += dest_lm_dur

        # -- cost breakdown --
        booking_fees = 0
        for conn in journey.connections:
            if conn.mode in BOOKING_FEE_RATE:
                booking_fees += int(conn.cost * BOOKING_FEE_RATE[conn.mode])
        meals = self._meals_cost(total_duration)
        total_cost = tickets_cost + last_mile_cost + booking_fees + meals

        # -- journey reliability: product of transport legs, penalised for last-mile --
        journey_reliability = journey.reliability * 0.95  # last-mile uncertainty

        warnings = []
        for r in connection_risks:
            if r["risk"] != "safe":
                warnings.append(
                    f"⚠️ {r['risk'].upper()} transfer at {r['hub_from']}→{r['hub_to']}: {r['reason']}"
                )

        # Booking links — per-leg deep links where possible
        booking_links = self._booking_links(journey.connections)

        return {
            "total_cost": total_cost,
            "total_duration_minutes": total_duration,
            "reliability_score": round(journey_reliability, 2),
            "transfers": journey.transfers,
            "legs": legs,
            "cost_breakdown": {
                "tickets": tickets_cost,
                "last_mile": last_mile_cost,
                "booking_fees": booking_fees,
                "meals_incidentals": meals,
                "total": total_cost,
            },
            "connection_risks": connection_risks,
            "warnings": warnings,
            "booking_links": booking_links,
        }

    @staticmethod
    def _meals_cost(duration_minutes: int) -> int:
        if duration_minutes <= 360:  # < 6h
            return 0
        meals = (duration_minutes - 360) // 240 + 1  # one meal per 4h block after the first 6h
        return 150 * meals

    @staticmethod
    def _hub_by_code(hubs: List[Location], code: str) -> Optional[Location]:
        for h in hubs:
            if h.code == code:
                return h
        return None

    @staticmethod
    def _booking_links(connections: List[Connection]) -> Dict[str, Any]:
        links: Dict[str, Any] = {
            "flights": "https://www.ixigo.com/flights",
            "trains": "https://www.irctc.co.in",
            "buses": "https://www.redbus.in",
        }
        per_leg: List[Dict[str, str]] = []
        for c in connections:
            if c.mode == "flight":
                per_leg.append({
                    "mode": "flight",
                    "vehicle_id": c.vehicle_id,
                    "url": f"https://www.ixigo.com/flights?flightNumber={c.vehicle_id}",
                })
            elif c.mode == "train":
                per_leg.append({
                    "mode": "train",
                    "vehicle_id": c.vehicle_id,
                    "url": f"https://www.irctc.co.in/nget/train-search?trainNumber={c.vehicle_id}",
                })
            elif c.mode == "bus":
                per_leg.append({
                    "mode": "bus",
                    "vehicle_id": c.vehicle_id,
                    "url": f"https://www.redbus.in/bus-tickets/{c.from_code}-to-{c.to_code}".replace(" ", "-"),
                })
        links["per_leg"] = per_leg
        return links

    @staticmethod
    def _journey_id(origin_id: int, dest_id: int,
                    travel_date: date | None, preference: str, rank: int) -> str:
        key = f"{origin_id}:{dest_id}:{travel_date or ''}:{preference}:{rank}"
        return sha1(key.encode()).hexdigest()[:16]

    # ------------------------------------------------------------------ #
    # Fallback for empty searches
    # ------------------------------------------------------------------ #

    def _create_fallback_journeys(
        self, origin: City, destination: City
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        if (origin.latitude is not None and origin.longitude is not None
                and destination.latitude is not None and destination.longitude is not None):
            distance_km = self.geo.calculate_distance(
                origin.latitude, origin.longitude,
                destination.latitude, destination.longitude,
            )
        else:
            distance_km = 500.0
        estimated_cost = max(500, int(distance_km * 2))
        estimated_duration = int(distance_km / 50 * 60)
        journey = {
            "rank": 1,
            "journey_id": self._journey_id(origin.id or 0, destination.id or 0, None, "balanced", 1),
            "total_cost": estimated_cost + 500,
            "total_duration_minutes": estimated_duration + 60,
            "reliability_score": 0.7,
            "transfers": 0,
            "legs": [
                {"mode": "auto", "from_name": origin.name, "to_name": origin.name,
                 "cost": 0, "duration_minutes": 0, "notes": "Start your journey"},
                {"mode": "multi-modal", "from_name": origin.name, "to_name": destination.name,
                 "cost": estimated_cost, "duration_minutes": estimated_duration,
                 "reliability_score": 0.7,
                 "notes": "Estimated — check IRCTC/RedBus/Ixigo for real schedules"},
                {"mode": "auto", "from_name": destination.name, "to_name": destination.name,
                 "cost": 0, "duration_minutes": 0, "notes": "End destination"},
            ],
            "cost_breakdown": {
                "tickets": estimated_cost, "last_mile": 500,
                "booking_fees": 0, "meals_incidentals": 0,
                "total": estimated_cost + 500,
            },
            "connection_risks": [],
            "warnings": ["No curated routes between these cities yet."],
            "booking_links": {
                "flights": "https://www.ixigo.com/flights",
                "trains": "https://www.irctc.co.in",
                "buses": "https://www.redbus.in",
            },
        }
        return [journey], {
            "error": "No routes in database for this pair. Falling back to estimate.",
            "origin": f"{origin.name} ({origin.code or '—'})",
            "destination": f"{destination.name} ({destination.code or '—'})",
            "distance_km": round(distance_km, 1),
        }

    def search_locations(self, query: str, limit: int = 10) -> List[Dict]:
        locations = self.geo.find_locations_by_name(query, limit)
        return [
            {
                "type": loc.location_type,
                "name": loc.name,
                "code": loc.code,
                "latitude": loc.latitude,
                "longitude": loc.longitude,
                "distance_from_origin": loc.distance_to_origin,
                "city_id": loc.city_id,
            }
            for loc in locations
        ]
