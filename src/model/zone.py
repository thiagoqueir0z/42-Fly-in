"""Zone class representing locations in the drone network."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Enumeration of valid zone types in the drone network."""
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


@dataclass
class Zone:
    """Represents a zone in the drone network.

    A zone is a location where drones can be positioned. Each zone has
    a position, a type (normal, restricted, priority, blocked), and
    capacity constraints.

    Attributes:
        name (str): Unique identifier for the zone.
        x (int): X coordinate of the zone.
        y (int): Y coordinate of the zone.
        zone_type (ZoneType): Type of zone (normal, restricted, priority, blocked).
        color (Optional[str]): Optional color for visualization.
        max_drones (int): Maximum number of drones in this zone simultaneously.
        is_start (bool): Whether this is the starting zone.
        is_end (bool): Whether this is the ending zone.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    def __post_init__(self) -> None:
        if self.max_drones < 1:
            raise ValueError(f"max_drones must be at least 1, got {self.max_drones}")

    def get_movement_cost(self) -> int:
        """Get the movement cost to enter this zone.

        Returns:
            1 for normal/priority zones, 2 for restricted zones.

        Raises:
            ValueError: If zone is blocked (cannot be entered).
        """
        if self.zone_type == ZoneType.BLOCKED:
            raise ValueError(f"Zone '{self.name}' is blocked and cannot be entered.")
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def can_accommodate_drone(self, drones_in_zone: int) -> bool:
        """Check if the zone can accommodate another drone.

        Args:
            drones_in_zone: Current number of drones in the zone.

        Returns:
            True if capacity allows, False otherwise.
        """
        if self.is_start or self.is_end:
            return True
        return drones_in_zone < self.max_drones

    def __hash__(self) -> int:
        """Return hash of the zone based on its name."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Check equality with another zone based on name."""
        if not isinstance(other, Zone):
            return NotImplemented
        return self.name == other.name
