"""Simulation engine for routing drones through the network."""

from typing import Dict, List, Set

from src.model.connection import Connection
from src.model.drone import Drone
from src.model.graph import Graph
from src.model.zone import Zone


class Simulator:
    """Execute the turn-by-turn simulation of the drone fleet."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the simulator."""
        self.graph = graph
        self.turn_count = 0
        self.drones: List[Drone] = []
        self.history: List[Dict[str, str]] = []

    def _initialize_fleet(self, all_routes: Dict[str, List[Zone]]) -> None:
        """Create drones and assign their planned paths."""
        if self.graph.start_zone is None:
            raise ValueError("Cannot initialize fleet: graph has no start zone.")

        self.drones = []
        for drone_id in range(1, self.graph.num_drones + 1):
            drone = Drone(drone_id, self.graph.start_zone)
            route = all_routes.get(drone.name)
            if route is None:
                raise ValueError(f"Missing route for {drone.name}.")
            drone.set_path(route)
            self.drones.append(drone)

    def is_simulation_complete(self) -> bool:
        """Return whether every drone reached the end zone."""
        return all(drone.delivered for drone in self.drones)

    def run(self, all_routes: Dict[str, List[Zone]]) -> None:
        """Run the simulation until all drones are delivered."""
        self.turn_count = 0
        self.history = []
        self._initialize_fleet(all_routes)

        if self.graph.start_zone is None:
            raise ValueError("Cannot start simulation without a start zone.")

        initial_state = {
            drone.name: self.graph.start_zone.name
            for drone in self.drones
        }
        self.history.append(initial_state)

        while not self.is_simulation_complete():
            self.turn_count += 1
            self._simulate_turn()
            if self.turn_count > 10000:
                raise RuntimeError("Simulation exceeded 10000 turns.")

    def _simulate_turn(self) -> None:
        """Process one simultaneous simulation turn."""
        turn_moves: List[str] = []
        acted: Set[int] = set()
        connection_usage: Dict[Connection, int] = {}

        for drone in self.drones:
            if drone.target_zone is None:
                continue

            drone.turns_in_transit -= 1
            acted.add(drone.drone_id)
            if drone.turns_in_transit == 0:
                target = drone.target_zone
                drone.advance_to_zone(target)
                turn_moves.append(
                    self._format_colored_move(
                        drone.name, target.name, target
                    )
                )

        for drone in self.drones:
            if drone.delivered or drone.drone_id in acted:
                continue

            next_zone = drone.get_next_destination()
            if next_zone is None:
                continue

            if next_zone == drone.current_zone:
                acted.add(drone.drone_id)
                continue

            connection = self.graph.get_connection(
                drone.current_zone,
                next_zone,
            )
            if connection is None:
                continue

            if not self._can_move(
                drone,
                next_zone,
                connection,
                connection_usage,
            ):
                continue

            self._execute_move(
                drone,
                next_zone,
                connection,
                connection_usage,
            )
            turn_moves.append(
                self._format_colored_move(
                    drone.name, next_zone.name, next_zone
                )
            )
            acted.add(drone.drone_id)

        if turn_moves:
            print(" ".join(turn_moves))

        state = {
            drone.name: drone.current_zone.name
            for drone in self.drones
        }
        self.history.append(state)

    def _can_move(
        self,
        drone: Drone,
        next_zone: Zone,
        connection: Connection,
        turn_connection_usage: Dict[Connection, int],
    ) -> bool:
        """Check connection and destination-zone capacity."""
        connection_occupancy = (
            self._get_connection_occupancy(connection)
            + turn_connection_usage.get(connection, 0)
        )
        if not connection.can_accommodate_drone(connection_occupancy):
            return False

        zone_occupancy = self._get_zone_occupancy(next_zone)
        return next_zone.can_accommodate_drone(zone_occupancy)

    def _execute_move(
        self,
        drone: Drone,
        next_zone: Zone,
        connection: Connection,
        turn_connection_usage: Dict[Connection, int],
    ) -> None:
        """Apply one movement and update connection usage."""
        turn_connection_usage[connection] = (
            turn_connection_usage.get(connection, 0) + 1
        )

        cost = next_zone.get_movement_cost()
        if cost == 1:
            drone.advance_to_zone(next_zone)
        else:
            drone.begin_transit(next_zone, cost - 1)

    def _get_zone_occupancy(self, zone: Zone) -> int:
        """Count drones occupying or entering a zone."""
        if zone.is_start or zone.is_end:
            return 0

        return sum(
            1
            for drone in self.drones
            if not drone.delivered
            and (
                drone.current_zone == zone
                or drone.target_zone == zone
            )
        )

    def _get_connection_occupancy(self, connection: Connection) -> int:
        """Count drones currently crossing a connection."""
        count = 0
        for drone in self.drones:
            if drone.delivered or drone.target_zone is None:
                continue

            active_connection = self.graph.get_connection(
                drone.current_zone,
                drone.target_zone,
            )
            if active_connection == connection:
                count += 1

        return count

    def _format_colored_move(
        self,
        drone_name: str,
        target_name: str,
        zone: Zone,
    ) -> str:
        """Format a movement with optional terminal color."""
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "orange": "\033[33m",
            "gray": "\033[90m",
            "black": "\033[30m",
            "lightblue": "\033[96m",
        }
        reset = "\033[0m"

        if zone.color and zone.color.lower() in colors:
            color = colors[zone.color.lower()]
        elif zone.is_start:
            color = colors["green"]
        elif zone.is_end:
            color = colors["yellow"]
        elif zone.zone_type.name == "RESTRICTED":
            color = colors["red"]
        elif zone.zone_type.name == "PRIORITY":
            color = colors["orange"]
        else:
            color = colors["lightblue"]

        return f"{drone_name}-{color}{target_name}-{reset}"
