"""Connection class representing edges between zones."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.model.zone import Zone


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones."""

    zone_a: "Zone"
    zone_b: "Zone"
    max_link_capacity: int = 1

    def __post_init__(self) -> None:
        """Validate connection rules required by the subject."""
        if self.max_link_capacity < 1:
            raise ValueError(
                f"max_link_capacity must be a positive integer. Got {self.max_link_capacity}"
            )
        if self.zone_a == self.zone_b:
            raise ValueError(
                f"Connection cannot link a zone to itself: {self.zone_a.name}"
            )

    def connects(self, zone_1: "Zone", zone_2: "Zone") -> bool:
        """Check if this connection links z1-z2 or z2-z1 bidirectionally."""
        return (self.zone_a == zone_1 and self.zone_b == zone_2) or \
            (self.zone_a == zone_2 and self.zone_b == zone_1)

    def get_neighbor(self, zone: "Zone") -> Optional["Zone"]:
        """Return the zone on the other end of the connection."""
        if zone == self.zone_a:
            return self.zone_b
        if zone == self.zone_b:
            return self.zone_a
        return None

    def can_accommodate_drone(self, drones_in_transit: int) -> bool:
        """Check if connection capacity allows another drone."""
        return drones_in_transit < self.max_link_capacity

    def __hash__(self) -> int:
        """Hash must be identical for A-B and B-A to prevent duplicates."""
        return hash(frozenset([self.zone_a.name, self.zone_b.name]))

    def __eq__(self, other: object) -> bool:
        """Ensure connection A-B is treated as equal to B-A."""
        if not isinstance(other, Connection):
            return NotImplemented
        return self.connects(other.zone_a, other.zone_b)
