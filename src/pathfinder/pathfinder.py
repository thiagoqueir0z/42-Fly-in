"""Deterministic cooperative pathfinding for the drone network."""

import heapq
from collections import defaultdict

from src.model.graph import Graph
from src.model.zone import Zone, ZoneType


class PathNotFound(Exception):
    """Raised when no valid route can be found."""


class Pathfinder:
    """Plan deterministic routes while respecting shared reservations."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the pathfinder and calculate heuristic distances."""
        self.graph = graph
        self.zone_reservations: dict[int, dict[Zone, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        self.edge_reservations: dict[
            int, dict[frozenset[Zone], int]
        ] = defaultdict(lambda: defaultdict(int))
        self.strategic_map = self._calculate_strategic_map()

    def _calculate_strategic_map(self) -> dict[Zone, int]:
        """Calculate the cheapest remaining movement cost to the goal."""
        if self.graph.end_zone is None:
            return {}

        distances: dict[Zone, int] = {self.graph.end_zone: 0}
        queue: list[tuple[int, int, Zone]] = [(0, 0, self.graph.end_zone)]
        counter = 0

        while queue:
            distance, _, zone = heapq.heappop(queue)
            if distance != distances[zone]:
                continue

            for neighbor in self.graph.get_neighbors(zone):
                new_distance = distance + neighbor.get_movement_cost()
                if new_distance >= distances.get(neighbor, 10**9):
                    continue

                distances[neighbor] = new_distance
                counter += 1
                heapq.heappush(queue, (new_distance, counter, neighbor))

        return distances

    def plan_all_routes(self) -> dict[str, list[Zone]]:
        """Plan one deterministic route for every drone."""
        drone_order = [
            f"D{drone_id}"
            for drone_id in range(1, self.graph.num_drones + 1)
        ]
        return self._plan_for_order(drone_order)

    def _plan_for_order(self, drone_order: list[str]) -> dict[str, list[Zone]]:
        """Plan and reserve routes in the requested drone order."""
        self.zone_reservations.clear()
        self.edge_reservations.clear()
        routes: dict[str, list[Zone]] = {}

        for drone_id in drone_order:
            path = self._find_time_aware_path()
            self._reserve_path(path)
            routes[drone_id] = path

        return routes

    def _find_time_aware_path(self) -> list[Zone]:
        """Find the earliest valid route using A* with reservations."""
        start = self.graph.start_zone
        goal = self.graph.end_zone
        if start is None or goal is None:
            raise PathNotFound("Graph must have one start and one end zone.")

        # (estimated finish, arrival turn, priority tie-break, counter,
        # current zone, path)
        queue: list[tuple[float, int, int, int, Zone, list[Zone]]] = []
        counter = 0
        initial_estimate = self.strategic_map.get(start, 10**9)
        heapq.heappush(
            queue,
            (initial_estimate, 0, 0, counter, start, [start]),
        )
        best_cost: dict[tuple[Zone, int], float] = {(start, 0): 0.0}

        while queue:
            _, current_turn, _, _, current, path = heapq.heappop(queue)
            if current == goal:
                return path

            for next_zone in self._possible_moves(current):
                waiting = next_zone == current
                duration = 1 if waiting else next_zone.get_movement_cost()
                arrival = current_turn + duration

                if not self._can_reserve_move(
                    current,
                    next_zone,
                    current_turn,
                    arrival,
                    waiting,
                ):
                    continue

                state = (next_zone, arrival)
                score = float(arrival + self.strategic_map.get(next_zone, 10**9))
                if score >= best_cost.get(state, float("inf")):
                    continue

                best_cost[state] = score
                counter += 1
                priority = (
                    0
                    if next_zone.zone_type == ZoneType.PRIORITY
                    else 1
                )
                new_path = [*path, next_zone]
                heapq.heappush(
                    queue,
                    (score, arrival, priority, counter, next_zone, new_path),
                )

        raise PathNotFound(
            f"No valid path exists from {start.name} to {goal.name}."
        )

    def _possible_moves(self, zone: Zone) -> list[Zone]:
        """Return neighbors followed by the option to wait."""
        return [*self.graph.get_neighbors(zone), zone]

    def _can_reserve_move(
        self,
        current: Zone,
        next_zone: Zone,
        current_turn: int,
        arrival: int,
        waiting: bool,
    ) -> bool:
        """Check destination and connection capacity for one move."""
        if waiting:
            return self._zone_has_capacity(next_zone, arrival)

        connection = self.graph.get_connection(current, next_zone)
        if connection is None:
            return False

        if not self._zone_has_capacity(next_zone, arrival):
            return False

        edge = frozenset((current, next_zone))
        edge_turns = self._edge_turns(current_turn, arrival)
        return all(
            self.edge_reservations[turn][edge]
            < connection.max_link_capacity
            for turn in edge_turns
        )

    def _zone_has_capacity(self, zone: Zone, turn: int) -> bool:
        """Return whether the zone has room at a specific turn."""
        if zone.is_start or zone.is_end:
            return True

        return self.zone_reservations[turn][zone] < zone.max_drones

    @staticmethod
    def _edge_turns(current_turn: int, arrival: int) -> range:
        """Return turns during which a connection is occupied."""
        if arrival - current_turn == 1:
            return range(current_turn + 1, arrival + 1)

        return range(current_turn + 1, arrival)

    def _reserve_path(self, path: list[Zone]) -> int:
        """Reserve a path and return its final arrival turn."""
        current_turn = 0

        for current, next_zone in zip(path, path[1:]):
            waiting = current == next_zone
            duration = 1 if waiting else next_zone.get_movement_cost()
            arrival = current_turn + duration

            self.zone_reservations[arrival][next_zone] += 1

            if not waiting:
                edge = frozenset((current, next_zone))
                for turn in self._edge_turns(current_turn, arrival):
                    self.edge_reservations[turn][edge] += 1

            current_turn = arrival

        return current_turn
