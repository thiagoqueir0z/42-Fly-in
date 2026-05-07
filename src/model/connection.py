"""Connection class representing edges between zones."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.model.zone import Zone


class Connection:
    """Represents a bidirectional connection between two zones.

    A connection is an edge in the graph allowing drone movement between
    zones. It can have capacity constraints limiting simultaneous traversal.

    Attributes:
        zone_a (Zone): First zone in the connection.
        zone_b (Zone): Second zone in the connection.
        max_link_capacity (int): Max drones traversing simultaneously.
    """

    def __init__(
        self,
        zone_a: "Zone",
        zone_b: "Zone",
        max_link_capacity: int = 1,
    ) -> None:
        """Initialize a Connection.

        Args:
            zone_a: First zone.
            zone_b: Second zone.
            max_link_capacity: Maximum drones on this connection (default: 1).

        Raises:
            ValueError: If max_link_capacity is less than 1.
        """
        pass

    def connects(self, zone_a: "Zone", zone_b: "Zone") -> bool:
        """Check if this connection links the two given zones.

        Args:
            zone_a: First zone to check.
            zone_b: Second zone to check.

        Returns:
            True if connection links these zones in any direction.
        """
        pass

    def get_neighbor(self, zone: "Zone") -> "Zone | None":
        """Get the neighbor zone on the other end of this connection.

        Args:
            zone: The starting zone.

        Returns:
            The connected zone, or None if the given zone is not part
            of this connection.
        """
        pass

    def can_accommodate_drone(self, current_count: int) -> bool:
        """Check if the connection can accommodate another drone.

        Args:
            current_count: Current number of drones using this connection.

        Returns:
            True if capacity allows, False otherwise.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of the connection.

        Returns:
            String in format: Connection(zone_a - zone_b, capacity).
        """
        pass

    def __hash__(self) -> int:
        """Return hash of the connection.

        Returns:
            Hash value based on both zones.
        """
        pass

    def __eq__(self, other: object) -> bool:
        """Check equality with another connection.

        Args:
            other: Object to compare with.

        Returns:
            True if both connections link the same zones.
        """
        pass
