"""Graph class representing the entire drone network."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from src.model.connection import Connection
from src.model.zone import Zone, ZoneType


@dataclass
class Graph:
    """Represents the complete network of zones and connections.

    The graph stores all zones and connections that form the network
    through which drones navigate. It utilizes an adjacency list for
    efficient neighbor lookups during pathfinding.

    Attributes:
        num_drones (int): Total number of drones to route.
        zones (Dict[str, Zone]): Dictionary of all zones mapped by their name.
        connections (Set[Connection]): Set of all unique connections.
        adjacency_list (Dict[str, List[Connection]]): Maps zone names to their connections.
        start_zone (Optional[Zone]): The starting hub zone.
        end_zone (Optional[Zone]): The ending hub zone.
    """

    num_drones: int
    zones: Dict[str, Zone] = field(default_factory=dict, init=False)
    connections: Set[Connection] = field(default_factory=set, init=False)
    adjacency_list: Dict[str, List[Connection]] = field(default_factory=dict, init=False)
    start_zone: Optional[Zone] = field(default=None, init=False)
    end_zone: Optional[Zone] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Validate attributes after dataclass initialization."""
        if self.num_drones < 1:
            raise ValueError(f"num_drones must be at least 1, got {self.num_drones}")

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph and initialize its adjacency list.

        Args:
            zone: The zone to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"Zone '{zone.name}' already exists in the graph.")

        self.zones[zone.name] = zone
        self.adjacency_list[zone.name] = []

        if zone.is_start:
            if self.start_zone is not None:
                raise ValueError("Graph cannot have multiple start zones.")
            self.start_zone = zone

        if zone.is_end:
            if self.end_zone is not None:
                raise ValueError("Graph cannot have multiple end zones.")
            self.end_zone = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a bidirectional connection between two zones.

        Args:
            connection: The connection to add.

        Raises:
            ValueError: If the connection links unknown zones or is a duplicate one.
        """
        if (
            connection.zone_a.name not in self.zones
            or connection.zone_b.name not in self.zones
        ):
            raise ValueError(
                f"Cannot add connection {connection.zone_a.name}-{connection.zone_b.name}: "
                "One or both zones are not in the graph"
            )

        if connection in self.connections:
            raise ValueError(
                f"Duplicate connection detected: {connection.zone_a.name}-{connection.zone_b.name}"
            )

        self.connections.add(connection)

        self.adjacency_list[connection.zone_a.name].append(connection)
        self.adjacency_list[connection.zone_b.name].append(connection)

    def get_zone(self, name: str) -> Optional[Zone]:
        """Retrieve a zone by its name."""
        return self.zones.get(name)

    def get_neighbors(self, zone: Zone) -> List[Zone]:
        """Get all accessible zones adjacent to the given zone.

        Args:
            zone: The zone to find neighbors for.

        Returns:
            List of adjacent, non-blocked zones.
        """
        if zone.name not in self.adjacency_list:
            return []

        neighbors = []
        for connect in self.adjacency_list[zone.name]:
            neighbor = connect.get_neighbor(zone)
            if neighbor and neighbor.zone_type != ZoneType.BLOCKED:
                neighbors.append(neighbor)

        return neighbors

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        """Get the specific connection linking two zones if it exists."""
        if zone_a.name not in self.adjacency_list:
            return None
        for connect in self.adjacency_list[zone_a.name]:
            if connect.get_neighbor(zone_a) == zone_b:
                return connect

        return None

    def is_valid_path(self, path: List[Zone]) -> bool:
        """Check if a path is contiguous and free of blocked zones.

        Args:
            path: Ordered list of zones forming a route.

        Returns:
            True if the path is fully connected and valid.
        """
        if not path:
            return False

        for i in range(len(path) - 1):
            current_zone = path[i]
            next_zone = path[i + 1]

            if (
                current_zone.zone_type == ZoneType.BLOCKED
                or next_zone.zone_type == ZoneType.BLOCKED
            ):
                return False

            if not self.get_connection(current_zone, next_zone):
                return False

        return True
