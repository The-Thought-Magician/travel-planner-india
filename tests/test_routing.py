"""Tests for routing algorithms."""

from datetime import time

from app.routing.connection_scan import Connection, ConnectionScanAlgorithm, Journey


def test_connection_creation():
    """Test creating a connection."""
    conn = Connection(
        mode="train",
        from_code="SBC",
        to_code="HPT",
        departure_time=time(6, 0),
        arrival_time=time(13, 30),
        cost=450,
        vehicle_id="16592",
        reliability=0.85,
    )
    assert conn.mode == "train"
    assert conn.duration_minutes == 450  # 7h 30m
    assert conn.cost == 450


def test_journey_creation():
    """Test creating a journey with connections."""
    journey = Journey()
    conn1 = Connection(
        mode="flight",
        from_code="IXR",
        to_code="BLR",
        departure_time=time(6, 0),
        arrival_time=time(8, 30),
        cost=4500,
        vehicle_id="6E 234",
        reliability=0.9,
    )
    conn2 = Connection(
        mode="train",
        from_code="SBC",
        to_code="HPT",
        departure_time=time(11, 0),
        arrival_time=time(18, 0),
        cost=450,
        vehicle_id="16592",
        reliability=0.85,
    )

    journey.add_connection(conn1)
    journey.add_connection(conn2)

    assert journey.total_cost == 4950
    assert journey.transfers == 1
    assert len(journey.connections) == 2


def test_csa_basic():
    """Test basic CSA functionality."""
    connections = [
        Connection(
            mode="train",
            from_code="SBC",
            to_code="HPT",
            departure_time=time(6, 0),
            arrival_time=time(13, 30),
            cost=450,
            vehicle_id="16592",
            reliability=0.85,
        ),
    ]

    csa = ConnectionScanAlgorithm(connections)
    journeys = csa.find_k_best("SBC", "HPT", k=1)

    assert len(journeys) == 1
    assert journeys[0].total_cost == 450


def test_csa_with_transfer():
    """Test CSA with transfers."""
    connections = [
        Connection(
            mode="flight",
            from_code="IXR",
            to_code="BLR",
            departure_time=time(6, 0),
            arrival_time=time(8, 30),
            cost=3200,
            vehicle_id="6E 234",
            reliability=0.9,
        ),
        Connection(
            mode="train",
            from_code="SBC",
            to_code="HPT",
            departure_time=time(11, 0),
            arrival_time=time(18, 0),
            cost=450,
            vehicle_id="16592",
            reliability=0.85,
        ),
        # Connecting train
        Connection(
            mode="train",
            from_code="BLR",
            to_code="HPT",
            departure_time=time(10, 0),
            arrival_time=time(17, 0),
            cost=450,
            vehicle_id="16592",
            reliability=0.85,
        ),
    ]

    csa = ConnectionScanAlgorithm(connections, min_connection_buffer=90)
    journeys = csa.find_k_best("IXR", "HPT", k=1, max_transfers=1)

    # Should find the connecting journey
    assert len(journeys) >= 1


def test_connection_from_city_label():
    """Regression: Connection should accept optional from_city/to_city kwargs."""
    c = Connection(
        mode="bus",
        from_code="Bangalore",
        to_code="Hampi",
        from_city="Bangalore",
        to_city="Hampi",
        departure_time=time(22, 0),
        arrival_time=time(6, 30),
        cost=1150,
        vehicle_id="KSRTC",
        reliability=0.82,
    )
    assert c.from_city == "Bangalore"
    assert c.duration_minutes == 510


def test_csa_respects_min_buffer():
    """If transfer buffer < min_buffer, the leg should not be accepted."""
    connections = [
        Connection(
            mode="flight", from_code="A", to_code="B",
            departure_time=time(10, 0), arrival_time=time(11, 0),
            cost=1000, vehicle_id="F1", reliability=0.9,
        ),
        # Tight connection: 15 min buffer, needs 60
        Connection(
            mode="train", from_code="B", to_code="C",
            departure_time=time(11, 15), arrival_time=time(13, 0),
            cost=500, vehicle_id="T1", reliability=0.9,
        ),
        # Safe connection: 90 min buffer
        Connection(
            mode="train", from_code="B", to_code="C",
            departure_time=time(12, 30), arrival_time=time(14, 30),
            cost=600, vehicle_id="T2", reliability=0.9,
        ),
    ]
    csa = ConnectionScanAlgorithm(connections, min_connection_buffer=60)
    journeys = csa.find_k_best("A", "C", k=2, max_transfers=1)
    # Only T2 should be reachable; no journey should use T1
    for j in journeys:
        vehicle_ids = [c.vehicle_id for c in j.connections]
        assert "T1" not in vehicle_ids
