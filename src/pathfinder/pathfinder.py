"""Pathfinder algorithm module for the Fly-in simulation using Cooperative A*."""

import heapq
import random
from collections import defaultdict
from typing import Dict, List, Tuple

from src.model.graph import Graph
from src.model.zone import Zone


class PathNotFound(Exception):
    """Exception raised when no valid path exists between start and end zones."""
    pass


class Pathfinder:
    """Calculates optimal, collision-free routes for multiple drones."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.zone_reservations = defaultdict(lambda: defaultdict(int))
        self.edge_reservations = defaultdict(lambda: defaultdict(int))
        self.strategic_map: Dict[Zone, int] = self._calculate_strategic_map()

    def _calculate_strategic_map(self) -> Dict[Zone, int]:
        """Computes true heuristic distances from all zones to the end_hub."""
        if not self.graph.end_zone:
            return {}

        end_zone = self.graph.end_zone
        distances: Dict[Zone, int] = {end_zone: 0}
        counter = 0
        priority_queue: List[Tuple[int, int, Zone]] = [(0, counter, end_zone)]

        while priority_queue:
            current_dist, _, current_zone = heapq.heappop(priority_queue)

            if current_dist > distances.get(current_zone, float('inf')):
                continue

            for neighbor in self.graph.get_neighbors(current_zone):
                cost = current_zone.get_movement_cost()
                new_dist = current_dist + cost

                if new_dist < distances.get(neighbor, float('inf')):
                    distances[neighbor] = new_dist
                    counter += 1
                    heapq.heappush(priority_queue, (new_dist, counter, neighbor))

        return distances

    def _plan_for_order(self, drone_order: List[str]) -> Tuple[Dict[str, List[Zone]], int]:
        """Attempts to plan routes for a specific sequence of drones."""
        self.zone_reservations.clear()
        self.edge_reservations.clear()
        routes = {}
        makespan = 0

        for drone_id in drone_order:
            path = self._find_time_aware_path()
            final_turn = self._reserve_path(path)

            if final_turn > makespan:
                makespan = final_turn

            # Removes consecutive duplicate zones (waiting states) for the final output
            routes[drone_id] = [z for i, z in enumerate(path) if i == 0 or z != path[i-1]]

        return routes, makespan

    def plan_all_routes(self) -> Dict[str, List[Zone]]:
        """Finds conflict-free routes for all drones, optimizing the makespan."""
        base_drones = [f"D{i}" for i in range(1, self.graph.num_drones + 1)]
        best_routes: Dict[str, List[Zone]] = {}
        best_makespan = float('inf')
        max_attempts = 40

        for attempt in range(max_attempts):
            current_order = base_drones.copy()
            if attempt > 0:
                random.shuffle(current_order)

            try:
                routes, makespan = self._plan_for_order(current_order)

                if makespan < best_makespan:
                    best_makespan = makespan
                    best_routes = routes

                    if best_makespan <= 43:
                        break
            except PathNotFound:
                continue

        if not best_routes:
            raise PathNotFound("Could not find a valid routing configuration.")

        # Re-run the best order to properly populate the reservation tables for the simulator
        self._plan_for_order(list(best_routes.keys()))
        return best_routes

    def _find_time_aware_path(self) -> List[Zone]:
        """A* algorithm incorporating time-space reservations and zone capacities."""
        if not self.graph.start_zone or not self.graph.end_zone:
            raise ValueError("Graph must have both a start and an end zone.")

        start = self.graph.start_zone
        goal = self.graph.end_zone
        counter = 0

        initial_h = self.strategic_map.get(start, 999)
        priority_queue: List[Tuple[float, int, int, Zone, List[Zone]]] = [
            (initial_h, 0, counter, start, [start])
        ]
        lowest_costs: Dict[Tuple[Zone, int], float] = {(start, 0): initial_h}

        while priority_queue:
            _, current_turn, _, current_zone, current_path = heapq.heappop(priority_queue)

            if current_zone == goal:
                return current_path

            possible_moves = self.graph.get_neighbors(current_zone) + [current_zone]

            for next_zone in possible_moves:
                is_waiting = (next_zone == current_zone)

                if not is_waiting and next_zone in current_path:
                    continue

                is_dead_end = len(self.graph.get_neighbors(next_zone)) == 1 and next_zone != goal

                base_cost = 1 if is_waiting else next_zone.get_movement_cost()
                arrival_turn = current_turn + base_cost
                path_blocked = False

                for t in range(current_turn + 1, arrival_turn + 1):
                    max_zone_cap = (
                        float('inf')
                        if (next_zone.is_start or next_zone.is_end)
                        else next_zone.max_drones
                    )

                    if self.zone_reservations[t][next_zone] >= max_zone_cap:
                        if not (is_waiting and current_zone.is_start):
                            path_blocked = True
                            break

                    if not is_waiting:
                        edge = frozenset([current_zone, next_zone])
                        conn = self.graph.get_connection(current_zone, next_zone)

                        if conn and self.edge_reservations[t][edge] >= conn.max_link_capacity:
                            path_blocked = True
                            break

                if path_blocked:
                    continue

                real_arrival = current_turn + base_cost
                state_key = (next_zone, real_arrival)

                h_cost = self.strategic_map.get(next_zone, 999)
                p_bonus = 0.5 if next_zone.zone_type.name == "PRIORITY" else 0.0
                congestion = self.zone_reservations[real_arrival][next_zone] * 0.2

                estimated_cost = (
                    real_arrival + h_cost - p_bonus + congestion + (50 if is_dead_end else 0)
                )

                if estimated_cost < lowest_costs.get(state_key, float('inf')):
                    lowest_costs[state_key] = estimated_cost
                    counter += 1

                    new_path = list(current_path)
                    new_path.append(next_zone)
                    heapq.heappush(
                        priority_queue,
                        (estimated_cost, real_arrival, counter, next_zone, new_path)
                    )

        raise PathNotFound(f"No valid path exists from {start.name} to {goal.name}.")

    def _reserve_path(self, path: List[Zone]) -> int:
        """Records a resolved path into the time-space reservation tables."""
        current_turn = 0
        for i, zone in enumerate(path):
            if i == 0:
                continue

            prev_zone = path[i - 1]
            cost = 1 if prev_zone == zone else zone.get_movement_cost()
            arrival_turn = current_turn + cost

            for t in range(current_turn + 1, arrival_turn + 1):
                self.zone_reservations[t][zone] += 1

                if prev_zone != zone:
                    edge = frozenset([prev_zone, zone])
                    self.edge_reservations[t][edge] += 1

            current_turn = arrival_turn

        return current_turn
