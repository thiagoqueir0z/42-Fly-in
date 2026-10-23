"""Pathfinder algorithm module for the Fly-in simulation using Dijkstra."""

import heapq
from typing import Dict, List, Tuple

from src.model.graph import Graph
from src.model.zone import Zone


class PathNotFound(Exception):
    """Exception raised when no valid path exists between start and end zones."""
    pass


class Pathfinder:
    """Calculates optimal routes for drones within the network graph.

    Uses Dijkstra's algorithm to account for varying movement costs
    (e.g., restricted zones costing multiple turns) when calculating
    the shortest path.

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
        """Find the path with the lowest movement cost using Dijkstra's Algorithm.

        Returns:
            A list of Zones representing the optimal path from start to end.

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

        priority_queue: List[Tuple[int, int, Zone, List[Zone]]] = []
        counter = 0

        heapq.heappush(priority_queue, (0, counter, start, [start]))

        lowest_costs: Dict[Zone, int] = {start: 0}

        while priority_queue:
            current_cost, _, current_zone, current_path = heapq.heappop(priority_queue)

            if current_zone == goal:
                return current_path

            if current_cost > lowest_costs.get(current_zone, float('inf')):
                continue

            for neighbor in self.graph.get_neighbors(current_zone):
                movement_cost = neighbor.get_movement_cost()
                new_cost = current_cost + movement_cost

                if new_cost < lowest_costs.get(neighbor, float('inf')):
                    lowest_costs[neighbor] = new_cost
                    counter += 1
                    new_path = list(current_path)
                    new_path.append(neighbor)

                    heapq.heappush(
                        priority_queue, (new_cost, counter, neighbor, new_path)
                    )

        raise PathNotFound(f"No valid path exists from {start.name} to {goal.name}.")
