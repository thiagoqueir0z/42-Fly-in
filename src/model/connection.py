"""Connection class representing edges between zones."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.model.zone import Zone


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones.

    A connection is an edge in the graph allowing drone movement between
    zones. It can have capacity constraints limiting simultaneous traversal.

    Attributes:
        zone_a (Zone): First zone in the connection.
        zone_b (Zone): Second zone in the connection.
        max_link_capacity (int): Max drones traversing simultaneously.
    """

    zone_a: "Zone"
    zone_b: "Zone"
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """Validate attributes after dataclass initialization."""
        if self.max_link_capacity < 1:
            raise ValueError(
                f"max_link_capacity must be at least 1. got {self.max_link_capacity}"
            )
        if self.zone_a == self.zone_b:
            raise ValueError(
                f"Connection cannot link a zone to itself: {self.zone_a.name}"
            )

    def connects(self, zone_1: "Zone", zone_2: "Zone") -> bool:
        """Check if this connection links the two given zones."""
        return (self.zone_a == zone_1 and self.zone_b == zone_2) or \
            (self.zone_a == zone_2 and self.zone_b == zone_1)

    def get_neighbor(self, zone: "Zone") -> Optional["Zone"]:
        """Get the neighbor zone on the other end of this connection.

        Args:
            zone: The starting zone.

        Returns:
            The connected zone, or None if the given zone is not part
            of this connection.
        """
        if zone == self.zone_a:
            return self.zone_b
        if zone == self.zone_b:
            return self.zone_a
        return None

    def can_accommodate_drone(self, drones_in_transit: int) -> bool:
        """Check if the connection can accommodate another drone.

        Args:
            drones_in_transit: Current number of drones using this connection.

        Returns:
            True if capacity allows, False otherwise.
        """
        return drones_in_transit < self.max_link_capacity

    def __hash__(self) -> int:
        """Return hash of the connection.

        Returns:
            Hash value based on both zones.
        """
        return hash(frozenset([self.zone_a.name, self.zone_b.name]))

    def __eq__(self, other: object) -> bool:
        """Check equality with another connection.

        Args:
            other: Object to compare with.

        Returns:
            True if both connections link the same zones.
        """
        if not isinstance(other, Connection):
            return NotImplemented
        return self.connects(other.zone_a, other.zone_b)
