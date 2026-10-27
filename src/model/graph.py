"""Graph model for the drone network."""

from dataclasses import dataclass, field

from src.model.connection import Connection
from src.model.zone import Zone, ZoneType


@dataclass
class Graph:
    """Represent the zones and connections of the drone network."""

    num_drones: int
    zones: dict[str, Zone] = field(default_factory=dict, init=False)
    connections: set[Connection] = field(default_factory=set, init=False)
    adjacency_list: dict[str, list[Connection]] = field(
        default_factory=dict,
        init=False,
    )
    start_zone: Zone | None = field(default=None, init=False)
    end_zone: Zone | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Validate the graph configuration."""
        if self.num_drones < 1:
            raise ValueError(
                f"num_drones must be positive, got {self.num_drones}."
            )

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: Zone to add.

        Raises:
            ValueError: If the name already exists or a second start/end
                zone is added.
        """
        if zone.name in self.zones:
            raise ValueError(f"Zone '{zone.name}' already exists.")

        if zone.is_start and self.start_zone is not None:
            raise ValueError("Graph cannot have multiple start zones.")

        if zone.is_end and self.end_zone is not None:
            raise ValueError("Graph cannot have multiple end zones.")

        self.zones[zone.name] = zone
        self.adjacency_list[zone.name] = []

        if zone.is_start:
            self.start_zone = zone

        if zone.is_end:
            self.end_zone = zone

    def add_connection(self, connection: Connection) -> None:
        """Add a bidirectional connection to the graph.

        Args:
            connection: Connection to add.

        Raises:
            ValueError: If either zone is unknown or the connection is
                already registered.
        """
        self._validate_connection_zones(connection)

        if connection in self.connections:
            raise ValueError(
                f"Duplicate connection: "
                f"{connection.zone_a.name}-{connection.zone_b.name}."
            )

        self.connections.add(connection)
        self.adjacency_list[connection.zone_a.name].append(connection)
        self.adjacency_list[connection.zone_b.name].append(connection)

    def get_zone(self, name: str) -> Zone | None:
        """Return a zone by name, or None when it does not exist."""
        return self.zones.get(name)

    def get_neighbors(self, zone: Zone) -> list[Zone]:
        """Return accessible neighboring zones.

        Blocked zones are not returned.
        """
        connections = self.adjacency_list.get(zone.name, [])

        neighbors: list[Zone] = []
        for connection in connections:
            neighbor = connection.get_neighbor(zone)
            if neighbor is not None and neighbor.zone_type != ZoneType.BLOCKED:
                neighbors.append(neighbor)

        return neighbors

    def get_connection(
        self,
        zone_a: Zone,
        zone_b: Zone,
    ) -> Connection | None:
        """Return the connection between two zones, if it exists."""
        for connection in self.adjacency_list.get(zone_a.name, []):
            if connection.connects(zone_a, zone_b):
                return connection

        return None

    def is_valid_path(self, path: list[Zone]) -> bool:
        """Return whether a path is connected and avoids blocked zones."""
        if not path:
            return False

        if any(zone.zone_type == ZoneType.BLOCKED for zone in path):
            return False

        if any(zone.name not in self.zones for zone in path):
            return False

        return all(
            self.get_connection(current, next_zone) is not None
            for current, next_zone in zip(path, path[1:])
        )

    def _validate_connection_zones(self, connection: Connection) -> None:
        """Ensure both connection endpoints belong to this graph."""
        unknown_zones = [
            zone.name
            for zone in (connection.zone_a, connection.zone_b)
            if zone.name not in self.zones
        ]

        if unknown_zones:
            names = ", ".join(unknown_zones)
            raise ValueError(f"Unknown zone(s) in connection: {names}.")
