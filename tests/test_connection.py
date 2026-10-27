"""Tests for the connection domain model."""

import pytest

from src.model.connection import Connection
from src.model.zone import Zone


def make_zones() -> tuple[Zone, Zone]:
    """Create two zones for connection tests."""
    return Zone("start", 0, 0), Zone("goal", 1, 1)


def test_connection_has_default_capacity() -> None:
    """A connection must allow one drone by default."""
    start, goal = make_zones()
    connection = Connection(start, goal)

    assert connection.max_link_capacity == 1
    assert connection.can_accommodate_drone(0)
    assert not connection.can_accommodate_drone(1)


def test_connection_respects_custom_capacity() -> None:
    """A connection must respect its configured capacity."""
    start, goal = make_zones()
    connection = Connection(start, goal, max_link_capacity=2)

    assert connection.can_accommodate_drone(1)
    assert not connection.can_accommodate_drone(2)


def test_zero_capacity_is_rejected() -> None:
    """A connection cannot have zero capacity."""
    start, goal = make_zones()

    with pytest.raises(ValueError):
        Connection(start, goal, max_link_capacity=0)


def test_negative_capacity_is_rejected() -> None:
    """A connection cannot have negative capacity."""
    start, goal = make_zones()

    with pytest.raises(ValueError):
        Connection(start, goal, max_link_capacity=-1)


def test_self_connection_is_rejected() -> None:
    """A zone cannot be connected to itself."""
    zone = Zone("start", 0, 0)

    with pytest.raises(ValueError):
        Connection(zone, zone)


def test_connection_is_bidirectional() -> None:
    """The same connection must work in both directions."""
    start, goal = make_zones()
    connection = Connection(start, goal)

    assert connection.connects(start, goal)
    assert connection.connects(goal, start)


def test_get_neighbor_returns_the_opposite_zone() -> None:
    """The neighbor method must return the opposite endpoint."""
    start, goal = make_zones()
    connection = Connection(start, goal)

    assert connection.get_neighbor(start) == goal
    assert connection.get_neighbor(goal) == start


def test_get_neighbor_returns_none_for_unrelated_zone() -> None:
    """An unrelated zone must not have a neighbor in this connection."""
    start, goal = make_zones()
    other = Zone("other", 2, 2)
    connection = Connection(start, goal)

    assert connection.get_neighbor(other) is None


def test_connections_are_equal_regardless_of_order() -> None:
    """Endpoint order must not affect connection equality."""
    start, goal = make_zones()

    first = Connection(start, goal)
    second = Connection(goal, start, max_link_capacity=2)

    assert first == second
    assert hash(first) == hash(second)


def test_negative_occupancy_is_rejected() -> None:
    """Connection occupancy cannot be negative."""
    start, goal = make_zones()
    connection = Connection(start, goal)

    with pytest.raises(ValueError):
        connection.can_accommodate_drone(-1)
