"""Graph class representing the entire drone network."""

from typing import Dict, List, Set, Optional
from src.model.zone import Zone
from src.model.connection import Connection


class Graph:
    """Represents the complete network of zones and connections.

    The graph stores all zones and connections that form the network
    through which drones navigate. It provides methods for accessing
    neighbors, validating paths, and retrieving specific zones.

    Attributes:
        zones (Dict[str, Zone]): All zones in the network by name.
        connections (List[Connection]): All connections in the network.
        start_zone (Zone): The starting hub zone.
        end_zone (Zone): The ending hub zone.
        num_drones (int): Total number of drones to route.
    """

    def __init__(self, num_drones: int) -> None:
        """Initialize an empty Graph.

        Args:
            num_drones: Total number of drones to route through the network.

        Raises:
            ValueError: If num_drones is less than 1.
        """
        pass

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: The zone to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        pass

    def add_connection(self, connection: Connection) -> None:
        """Add a connection between two zones.

        Args:
            connection: The connection to add.

        Raises:
            ValueError: If the connection already exists or if it
                        connects zones that are not in the graph.
        """
        pass

    def set_start_zone(self, zone: Zone) -> None:
        """Set the starting hub zone.

        Args:
            zone: The zone to set as start.

        Raises:
            ValueError: If the zone is not in the graph.
        """
        pass

    def set_end_zone(self, zone: Zone) -> None:
        """Set the ending hub zone.

        Args:
            zone: The zone to set as end.

        Raises:
            ValueError: If the zone is not in the graph.
        """
        pass

    def get_zone(self, name: str) -> Optional[Zone]:
        """Retrieve a zone by name.

        Args:
            name: The name of the zone.

        Returns:
            The Zone object, or None if not found.
        """
        pass

    def get_neighbors(self, zone: Zone) -> List[Zone]:
        """Get all zones adjacent to the given zone.

        Args:
            zone: The zone to find neighbors for.

        Returns:
            List of adjacent zones.
        """
        pass

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        """Get the connection between two zones if it exists.

        Args:
            zone_a: First zone.
            zone_b: Second zone.

        Returns:
            The Connection object, or None if no connection exists.
        """
        pass

    def is_valid_path(self, path: List[Zone]) -> bool:
        """Check if a path is valid (all zones connected, no blocked zones).

        Args:
            path: List of zones forming a potential path.

        Returns:
            True if the path is valid, False otherwise.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of the graph.

        Returns:
            String describing zones and connections count.
        """
        pass
