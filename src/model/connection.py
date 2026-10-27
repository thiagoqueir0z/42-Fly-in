"""Domain model for bidirectional connections between zones."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.model.zone import Zone


@dataclass(eq=False)
class Connection:
    """Represent a bidirectional connection between two zones."""

    zone_a: "Zone"
    zone_b: "Zone"
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """Validate the connection configuration."""
        if self.max_link_capacity < 1:
            raise ValueError(
                "max_link_capacity must be positive, "
                f"got {self.max_link_capacity}."
            )

        if self.zone_a == self.zone_b:
            raise ValueError(
                f"Connection cannot link a zone to itself: {self.zone_a.name}."
            )

    def connects(self, zone_1: "Zone", zone_2: "Zone") -> bool:
        """Return whether this connection links the two given zones."""
        return (
            (self.zone_a == zone_1 and self.zone_b == zone_2)
            or (self.zone_a == zone_2 and self.zone_b == zone_1)
        )

    def get_neighbor(self, zone: "Zone") -> Optional["Zone"]:
        """Return the zone on the opposite end of the connection.

        Args:
            zone: Zone from which the neighbor is requested.

        Returns:
            The opposite zone, or None when the given zone is not connected.
        """
        if zone == self.zone_a:
            return self.zone_b

        if zone == self.zone_b:
            return self.zone_a

        return None

    def can_accommodate_drone(self, drones_in_transit: int) -> bool:
        """Return whether another drone can use this connection.

        Args:
            drones_in_transit: Number of drones currently using the link.

        Returns:
            True when the connection still has capacity.

        Raises:
            ValueError: If the occupancy is negative.
        """
        if drones_in_transit < 0:
            raise ValueError("drones_in_transit cannot be negative.")

        return drones_in_transit < self.max_link_capacity

    def __hash__(self) -> int:
        """Return a hash based on the two endpoint names."""
        return hash(frozenset((self.zone_a.name, self.zone_b.name)))

    def __eq__(self, other: object) -> bool:
        """Compare connections without considering endpoint order."""
        if not isinstance(other, Connection):
            return NotImplemented

        return self.connects(other.zone_a, other.zone_b)
