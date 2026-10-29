"""Simulation engine for routing drones through the network."""

from typing import Dict, List, Set

from src.model.connection import Connection
from src.model.drone import Drone
from src.model.graph import Graph
from src.model.zone import Zone


class Simulator:
    """Executes the turn-by-turn simulation enforcing physics and constraints."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self.turn_count = 0
        self.drones: List[Drone] = []
        self.history: List[Dict[str, str]] = []

    def _initialize_fleet(self, all_routes: Dict[str, List[Zone]]) -> None:
        """Instantiate drones and assign their initial paths."""
        if not self.graph.start_zone:
            raise ValueError("Cannot initialize fleet: Graph has no start zone.")

        self.drones = []
        for i in range(1, self.graph.num_drones + 1):
            drone = Drone(drone_id=i, current_zone=self.graph.start_zone)
            drone_id_str = f"D{i}"
            if drone_id_str in all_routes:
                drone.set_path(all_routes[drone_id_str])
                drone.path_index = 1
            self.drones.append(drone)

    def is_simulation_complete(self) -> bool:
        """Check if all drones have successfully reached the end hub."""
        return all(drone.delivered for drone in self.drones)

    def run(self, all_routes: Dict[str, List[Zone]]) -> None:
        """Execute the simulation loop until all drones are delivered."""
        self.history = []
        self._initialize_fleet(all_routes)

        initial_state = {f"D{drone.drone_id}": self.graph.start_zone.name for drone in self.drones}
        self.history.append(initial_state)

        while not self.is_simulation_complete():
            self.turn_count += 1
            self._simulate_turn()

            if self.turn_count > 10000:
                print("\n[ERROR] Simulation aborted: Exceeded 10000 turns (Deadlock suspected).")
                break

    def _simulate_turn(self) -> None:
        """Process a single discrete time step for all drones."""
        turn_moves: List[str] = []
        drones_acted_this_turn: Set[int] = set()
        turn_connection_usage: Dict[Connection, int] = {}

        for drone in self.drones:
            if drone.target_zone and drone.turns_in_transit > 0:
                drone.turns_in_transit -= 1
                drones_acted_this_turn.add(drone.drone_id)

                if drone.turns_in_transit == 0:
                    drone.advance_to_zone(drone.target_zone)
                    colored_move = self._format_colored_move(
                        drone.name, drone.current_zone.name, drone.current_zone
                    )
                    turn_moves.append(colored_move)

        progress_made = True
        while progress_made:
            progress_made = False
            for drone in self.drones:
                if drone.delivered or drone.drone_id in drones_acted_this_turn:
                    continue

                next_zone = drone.get_next_destination()
                if not next_zone:
                    continue

                connection = self.graph.get_connection(drone.current_zone, next_zone)
                if not connection:
                    continue

                if self._can_move(drone, next_zone, connection, turn_connection_usage):
                    cost = next_zone.get_movement_cost()
                    self._execute_move(drone, next_zone, connection, turn_connection_usage)

                    if cost > 1:
                        target_name = f"{drone.current_zone.name}-{next_zone.name}"
                    else:
                        target_name = next_zone.name

                    colored_move = self._format_colored_move(drone.name, target_name, next_zone)
                    turn_moves.append(colored_move)

                    drones_acted_this_turn.add(drone.drone_id)
                    progress_made = True

        if turn_moves:
            print(" ".join(turn_moves))

        turn_state = {}
        for drone in self.drones:
            if drone.target_zone and drone.turns_in_transit > 0:
                turn_state[f"D{drone.drone_id}"] = (
                    f"{drone.current_zone.name}-{drone.target_zone.name}"
                )
            else:
                turn_state[f"D{drone.drone_id}"] = drone.current_zone.name
        self.history.append(turn_state)

    def _can_move(
        self,
        drone: Drone,
        next_zone: Zone,
        connection: Connection,
        turn_connection_usage: Dict[Connection, int]
    ) -> bool:
        """Evaluate physical capacities before allowing a transition."""
        connection_occ = (
            self._get_connection_occupancy(connection) + turn_connection_usage.get(connection, 0)
        )
        if not connection.can_accommodate_drone(connection_occ):
            return False

        zone_occ = self._get_zone_occupancy(next_zone)
        if not next_zone.can_accommodate_drone(zone_occ):
            return False

        return True

    def _execute_move(
        self,
        drone: Drone,
        next_zone: Zone,
        connection: Connection,
        turn_connection_usage: Dict[Connection, int]
    ) -> None:
        """Execute the transition (instant or multi-turn transit)."""
        turn_connection_usage[connection] = turn_connection_usage.get(connection, 0) + 1
        cost = next_zone.get_movement_cost()

        if cost > 1:
            drone.begin_transit(next_zone, cost - 1)
        else:
            drone.advance_to_zone(next_zone)

    def _get_zone_occupancy(self, zone: Zone) -> int:
        """Calculate how many drones are physically in or heading to a zone."""
        if zone.is_start or zone.is_end:
            return 0

        count = 0
        for d in self.drones:
            if d.delivered:
                continue
            if d.target_zone == zone:
                count += 1
            elif d.current_zone == zone and d.target_zone is None:
                count += 1
        return count

    def _get_connection_occupancy(self, connection: Connection) -> int:
        """Calculate how many drones are currently stuck in transit on a connection."""
        count = 0
        for d in self.drones:
            if d.delivered:
                continue
            if d.target_zone:
                conn = self.graph.get_connection(d.current_zone, d.target_zone)
                if conn == connection:
                    count += 1
        return count

    def _format_colored_move(self, drone_name: str, target_name: str, zone: Zone) -> str:
        """Format the movement string with ANSI color codes for terminal output."""
        reset = "\033[0m"
        colors = {
            "red": "\033[91m",
            "green": "\033[92m",
            "blue": "\033[94m",
            "yellow": "\033[93m",
            "orange": "\033[33m",
            "gray": "\033[90m",
            "black": "\033[30m",
            "lightblue": "\033[96m"
        }

        if zone.color and zone.color.lower() in colors:
            color_code = colors[zone.color.lower()]
        elif zone.is_start:
            color_code = colors["green"]
        elif zone.is_end:
            color_code = colors["yellow"]
        elif zone.zone_type.name == "RESTRICTED":
            color_code = colors["red"]
        elif zone.zone_type.name == "PRIORITY":
            color_code = colors["orange"]
        else:
            color_code = colors["lightblue"]

        return f"{drone_name}-{color_code}{target_name}-{reset}"
