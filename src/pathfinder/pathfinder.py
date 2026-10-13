"""Pathfinder algorithm module for the Fly-in simulation."""

from collections import deque
from typing import List

from src.model.graph import Graph
from src.model.zone import Zone


class PathNotFound(Exception):
    """Exception raised when no valid path exists between start and end zones."""
    pass


class Pathfinder:
    """Calculates optimal routes for drones within the network graph.

    Attributes:
        graph (Graph): The network graph containing zones and connections.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the Pathfinder with a network graph.

        Args:
            graph: The fully populated Graph object.
        """
        self.graph = graph

    def find_shortest_path(self) -> List[Zone]:
        """Find the shortest path in terms of zone count using Breadth-First Search (BFS).

        Returns:
            A list of Zones representing the path from start_hub to end_hub.

        Raises:
            ValueError: If the graph is missing start or end zones.
            PathNotFound: If the graph is disconnected and no path can be found.
        """
        if not self.graph.start_zone or not self.graph.end_zone:
            raise ValueError(
                "Graph must have both a start and an end zone to calculate paths."
            )

        start = self.graph.start_zone
        goal = self.graph.end_zone

        initial_path: List[Zone] = [start]
        initial_state: tuple[Zone, List[Zone]] = (start, initial_path)
        queue: deque[tuple[Zone, List[Zone]]] = deque()
        queue.append(initial_state)
        visited: set[Zone] = {start}

        while queue:
            current_zone, current_path = queue.popleft()

            if current_zone == goal:
                return current_path

            for neighbor in self.graph.get_neighbors(current_zone):
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append((neighbor, current_path + [neighbor]))

        raise PathNotFound(
            f"No valid path exists from {start.name} to {goal.name}."
        )
