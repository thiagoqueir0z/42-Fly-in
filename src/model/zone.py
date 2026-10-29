"""Zone class representing locations in the drone network."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Enumeration of valid zone types defined by the subject."""
    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


@dataclass
class Zone:
    """Represents a discrete location in the drone network."""

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    def __post_init__(self) -> None:
        """Validate zone capacity rules."""
        if self.max_drones < 1:
            raise ValueError(
                f"max_drones must be a positive integer, got {self.max_drones}"
            )

    def get_movement_cost(self) -> int:
        """Determine the turn cost to enter this zone."""
        if self.zone_type == ZoneType.BLOCKED:
            raise ValueError(f"Zone '{self.name}' is blocked and inaccessible.")
        if self.zone_type == ZoneType.RESTRICTED:
            return 2
        return 1

    def can_accommodate_drone(self, drones_in_zone: int) -> bool:
        """Check if the zone can accept another drone based on capacity."""
        if self.is_start or self.is_end:
            return True
        return drones_in_zone < self.max_drones

    def __hash__(self) -> int:
        """Zone identity is strictly tied to its unique name."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Check equality with another zone based on name."""
        if not isinstance(other, Zone):
            return NotImplemented
        return self.name == other.name
