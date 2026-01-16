"""
Connection Scan Algorithm (CSA) for multi-modal routing.

Based on: Dibbelt et al., "Connection Scan Algorithm" (2017)
https://arxiv.org/pdf/1703.05997

CSA is efficient for public transit routing as it scans connections
chronologically rather than exploring a graph.
"""

import heapq
from dataclasses import dataclass, field
from datetime import datetime, time, timedelta
from typing import Any


@dataclass
class Connection:
    """A transport connection (leg of a journey)."""

    mode: str  # "flight", "train", "bus"
    from_code: str
    to_code: str
    departure_time: time
    arrival_time: time
    cost: int
    vehicle_id: str  # Flight/train/bus number
    reliability: float = 0.8  # On-time probability
    duration_minutes: int = 0

    def __post_init__(self) -> None:
        """Calculate duration after initialization."""
        if self.duration_minutes == 0:
            dep_mins = self.departure_time.hour * 60 + self.departure_time.minute
            arr_mins = self.arrival_time.hour * 60 + self.arrival_time.minute
            if arr_mins < dep_mins:
                arr_mins += 24 * 60
            self.duration_minutes = arr_mins - dep_mins


@dataclass
class Journey:
    """A complete journey consisting of multiple connections."""

    connections: list[Connection] = field(default_factory=list)
    total_cost: int = 0
    total_duration: int = 0  # minutes
    reliability: float = 1.0  # Combined probability
    transfers: int = 0

    def add_connection(self, conn: Connection) -> None:
        """Add a connection to this journey."""
        self.connections.append(conn)
        self.total_cost += conn.cost
        self.total_duration += conn.duration_minutes
        self.transfers = max(0, len(self.connections) - 1)
        # Combined reliability = product of individual reliabilities
        self.reliability *= conn.reliability


@dataclass(order=True)
class PriorityJourney:
    """Journey with priority for heap operations."""

    priority: float  # Lower is better
    journey: Journey = field(compare=False)


class ConnectionScanAlgorithm:
    """
    Implementation of Connection Scan Algorithm for multi-modal routing.

    For MVP, we use a simplified approach. The full CSA would:
    1. Load all connections for the day
    2. Sort by departure time
    3. Scan connections once, tracking best-known arrival at each station
    """

    def __init__(
        self,
        connections: list[Connection],
        min_connection_buffer: int = 60,  # minutes
    ) -> None:
        """
        Initialize CSA with a set of connections.

        Args:
            connections: All possible connections (flights, trains, buses)
            min_connection_buffer: Minimum time required for transfers (minutes)
        """
        self.connections = sorted(connections, key=lambda c: (
            c.departure_time.hour * 60 + c.departure_time.minute
        ))
        self.min_buffer = min_connection_buffer

    def find_k_best(
        self,
        from_code: str,
        to_code: str,
        k: int = 5,
        max_transfers: int = 3,
        preference: str = "balanced",
    ) -> list[Journey]:
        """
        Find k best journeys using modified CSA.

        Args:
            from_code: Origin station/airport code
            to_code: Destination station/airport code
            k: Number of journeys to return
            max_transfers: Maximum transfers allowed
            preference: Optimization criteria ("cheapest", "fastest", "reliable", "balanced")

        Returns:
            List of k best journeys (sorted by preference)
        """
        # For MVP, use Dijkstra-like approach on connections
        # Full CSA would be more efficient for large datasets

        journeys: list[Journey] = []
        visited: set[tuple[str, int]] = set()  # (location, time_minutes)

        # Priority queue: (cost/duration/reliability, journey)
        queue: list[PriorityJourney] = []

        # Initialize with all connections from origin
        for conn in self.connections:
            if conn.from_code == from_code:
                journey = Journey()
                journey.add_connection(conn)
                priority = self._calculate_priority(journey, preference)
                heapq.heappush(queue, PriorityJourney(priority, journey))

        while queue and len(journeys) < k * 2:  # Get more, then filter
            current = heapq.heappop(queue)
            journey = current.journey

            # Check if we reached destination
            last_conn = journey.connections[-1]
            state = (last_conn.to_code, journey.total_duration)

            if state in visited:
                continue
            visited.add(state)

            if last_conn.to_code == to_code:
                journeys.append(journey)
                continue

            # Don't exceed transfer limit
            if journey.transfers >= max_transfers:
                continue

            # Find connecting connections
            arrival_minutes = (
                last_conn.arrival_time.hour * 60 + last_conn.arrival_time.minute
            )

            for next_conn in self.connections:
                if next_conn.from_code == last_conn.to_code:
                    # Check if connection is feasible
                    next_dep_minutes = (
                        next_conn.departure_time.hour * 60 + next_conn.departure_time.minute
                    )

                    # Handle overnight connections
                    if next_dep_minutes < arrival_minutes:
                        next_dep_minutes += 24 * 60

                    buffer = next_dep_minutes - arrival_minutes

                    if buffer >= self.min_buffer:
                        new_journey = Journey()
                        new_journey.connections = journey.connections.copy()
                        new_journey.total_cost = journey.total_cost
                        new_journey.total_duration = journey.total_duration
                        new_journey.reliability = journey.reliability
                        new_journey.transfers = journey.transfers
                        new_journey.add_connection(next_conn)

                        priority = self._calculate_priority(new_journey, preference)
                        heapq.heappush(queue, PriorityJourney(priority, new_journey))

        # Rank by preference and return top k
        ranked = sorted(
            journeys,
            key=lambda j: self._calculate_priority(j, preference),
        )[:k]

        return ranked

    def _calculate_priority(self, journey: Journey, preference: str) -> float:
        """
        Calculate priority score for sorting.

        Lower is better.
        """
        if preference == "cheapest":
            return float(journey.total_cost)

        if preference == "fastest":
            return float(journey.total_duration)

        if preference == "most_reliable":
            return float(1.0 - journey.reliability)

        # Balanced: normalize and combine
        # Cost: 0-10000, Duration: 0-1440, Reliability: 0-1
        cost_score = journey.total_cost / 10000.0
        time_score = journey.total_duration / 1440.0
        reliability_score = 1.0 - journey.reliability

        return (cost_score + time_score + reliability_score) / 3.0
