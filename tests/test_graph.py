"""Tests for the graph domain model."""

import pytest

from src.model.connection import Connection
from src.model.graph import Graph
from src.model.zone import Zone, ZoneType


def make_graph() -> tuple[Graph, Zone, Zone, Zone]:
    """Create a small graph for tests."""
    graph = Graph(num_drones=2)
    start = Zone("start", 0, 0, is_start=True)
    middle = Zone("middle", 1, 0)
    goal = Zone("goal", 2, 0, is_end=True)

    graph.add_zone(start)
    graph.add_zone(middle)
    graph.add_zone(goal)

    return graph, start, middle, goal


def test_graph_rejects_non_positive_drone_count() -> None:
    """The graph must contain at least one drone."""
    with pytest.raises(ValueError):
        Graph(num_drones=0)


def test_graph_adds_zone_and_initializes_adjacency() -> None:
    """Adding a zone must create an empty adjacency list."""
    graph = Graph(num_drones=1)
    zone = Zone("start", 0, 0, is_start=True)

    graph.add_zone(zone)

    assert graph.get_zone("start") == zone
    assert graph.adjacency_list["start"] == []


def test_graph_rejects_duplicate_zone_names() -> None:
    """Zone names must be unique."""
    graph = Graph(num_drones=1)
    graph.add_zone(Zone("start", 0, 0, is_start=True))

    with pytest.raises(ValueError):
        graph.add_zone(Zone("start", 10, 10))


def test_graph_rejects_multiple_start_zones_without_partial_update() -> None:
    """A second start zone must not modify the graph."""
    graph = Graph(num_drones=1)
    first = Zone("start", 0, 0, is_start=True)
    second = Zone("other", 1, 1, is_start=True)

    graph.add_zone(first)

    with pytest.raises(ValueError):
        graph.add_zone(second)

    assert "other" not in graph.zones
    assert "other" not in graph.adjacency_list
    assert graph.start_zone == first


def test_graph_rejects_multiple_end_zones_without_partial_update() -> None:
    """A second end zone must not modify the graph."""
    graph = Graph(num_drones=1)
    first = Zone("goal", 0, 0, is_end=True)
    second = Zone("other", 1, 1, is_end=True)

    graph.add_zone(first)

    with pytest.raises(ValueError):
        graph.add_zone(second)

    assert "other" not in graph.zones
    assert graph.end_zone == first


def test_graph_adds_bidirectional_connection() -> None:
    """Connections must be available from both endpoints."""
    graph, start, middle, _ = make_graph()
    connection = Connection(start, middle)

    graph.add_connection(connection)

    assert graph.get_connection(start, middle) == connection
    assert graph.get_connection(middle, start) == connection
    assert middle in graph.get_neighbors(start)
    assert start in graph.get_neighbors(middle)


def test_graph_rejects_connection_with_unknown_zone() -> None:
    """Connections must reference zones already in the graph."""
    graph, start, _, _ = make_graph()
    unknown = Zone("unknown", 5, 5)

    with pytest.raises(ValueError):
        graph.add_connection(Connection(start, unknown))


def test_graph_rejects_duplicate_connections() -> None:
    """A-B and B-A must be treated as the same connection."""
    graph, start, middle, _ = make_graph()
    graph.add_connection(Connection(start, middle))

    with pytest.raises(ValueError):
        graph.add_connection(Connection(middle, start))


def test_blocked_neighbors_are_hidden() -> None:
    """Blocked zones must not be returned as accessible neighbors."""
    graph = Graph(num_drones=1)
    start = Zone("start", 0, 0, is_start=True)
    blocked = Zone("blocked", 1, 0, ZoneType.BLOCKED)

    graph.add_zone(start)
    graph.add_zone(blocked)
    graph.add_connection(Connection(start, blocked))

    assert graph.get_neighbors(start) == []


def test_valid_path_is_accepted() -> None:
    """A connected path without blocked zones is valid."""
    graph, start, middle, goal = make_graph()
    graph.add_connection(Connection(start, middle))
    graph.add_connection(Connection(middle, goal))

    assert graph.is_valid_path([start, middle, goal])


def test_empty_path_is_invalid() -> None:
    """An empty path is not valid."""
    graph = Graph(num_drones=1)

    assert not graph.is_valid_path([])


def test_single_blocked_zone_is_invalid() -> None:
    """A path containing one blocked zone is invalid."""
    graph = Graph(num_drones=1)
    blocked = Zone("blocked", 0, 0, ZoneType.BLOCKED)
    graph.add_zone(blocked)

    assert not graph.is_valid_path([blocked])


def test_path_with_blocked_zone_is_invalid() -> None:
    """Blocked zones cannot appear in the middle of a path."""
    graph, start, _, goal = make_graph()
    blocked = Zone("blocked", 1, 1, ZoneType.BLOCKED)

    graph.add_zone(blocked)
    graph.add_connection(Connection(start, blocked))
    graph.add_connection(Connection(blocked, goal))

    assert not graph.is_valid_path([start, blocked, goal])


def test_disconnected_path_is_invalid() -> None:
    """A path without a connection between zones is invalid."""
    graph, start, middle, _ = make_graph()

    assert not graph.is_valid_path([start, middle])


def test_external_zone_is_invalid() -> None:
    """Zones not registered in the graph cannot form a valid path."""
    graph = Graph(num_drones=1)
    external_a = Zone("a", 0, 0)
    external_b = Zone("b", 1, 0)

    assert not graph.is_valid_path([external_a, external_b])
