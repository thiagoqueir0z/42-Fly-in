"""Tests for restricted-transit occupancy in the simulator."""

from src.model.connection import Connection
from src.model.drone import Drone
from src.model.graph import Graph
from src.model.zone import Zone, ZoneType
from src.simulator.simulator import Simulator


def make_restricted_graph() -> tuple[
    Graph, Zone, Zone, Connection
]:
    """Create a graph with one restricted destination."""
    graph = Graph(num_drones=1)
    start = Zone("start", 0, 0, is_start=True)
    restricted = Zone("tunnel", 1, 0, ZoneType.RESTRICTED)
    goal = Zone("goal", 2, 0, is_end=True)
    connection = Connection(start, restricted)

    graph.add_zone(start)
    graph.add_zone(restricted)
    graph.add_zone(goal)
    graph.add_connection(connection)
    graph.add_connection(Connection(restricted, goal))

    return graph, start, restricted, connection


def test_transit_drone_occupies_connection_only() -> None:
    """A drone in transit must not occupy either endpoint zone."""
    graph, start, restricted, connection = make_restricted_graph()
    simulator = Simulator(graph)
    drone = Drone(1, start)
    drone.set_path([start, restricted])
    drone.begin_transit(restricted, 1)
    simulator.drones = [drone]

    assert simulator._get_zone_occupancy(start) == 0
    assert simulator._get_zone_occupancy(restricted) == 0
    assert simulator._get_connection_occupancy(connection) == 1


def test_arriving_drone_leaves_connection_and_enters_zone() -> None:
    """Arrival must transfer occupancy from the connection to the zone."""
    graph, start, restricted, connection = make_restricted_graph()
    simulator = Simulator(graph)
    drone = Drone(1, start)
    drone.set_path([start, restricted])
    drone.begin_transit(restricted, 1)
    simulator.drones = [drone]

    drone.advance_to_zone(restricted)

    assert simulator._get_connection_occupancy(connection) == 0
    assert simulator._get_zone_occupancy(restricted) == 1
