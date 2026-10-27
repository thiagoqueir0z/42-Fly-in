"""Domain model for a zone in the drone network."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class ZoneType(Enum):
    """Types of zones supported by the simulation."""

    NORMAL = "normal"
    PRIORITY = "priority"
    RESTRICTED = "restricted"
    BLOCKED = "blocked"


@dataclass(eq=False)
class Zone:
    """Represent a location where drones can be placed."""

    name: str
    x: int
    y: int
    zone_type: ZoneType = ZoneType.NORMAL
    color: Optional[str] = None
    max_drones: int = 1
    is_start: bool = False
    is_end: bool = False

    def __post_init__(self) -> None:
        """Validate the basic invariants of the zone."""
        if not self.name:
            raise ValueError("Zone name cannot be empty.")

        if " " in self.name or "-" in self.name:
            raise ValueError(
                f"Invalid zone name '{self.name}': spaces and dashes are forbidden."
            )

        if self.max_drones < 1:
            raise ValueError(
                f"max_drones must be positive, got {self.max_drones}."
            )

    def get_movement_cost(self) -> int:
        """Return the number of turns needed to enter this zone.

        Returns:
            One turn for normal and priority zones, or two turns for
            restricted zones.

        Raises:
            ValueError: If the zone is blocked.
        """
        if self.zone_type == ZoneType.BLOCKED:
            raise ValueError(f"Zone '{self.name}' is blocked.")

        if self.zone_type == ZoneType.RESTRICTED:
            return 2

        return 1

    def can_accommodate_drone(self, drones_in_zone: int) -> bool:
        """Check whether another drone can enter this zone.

        The start and end zones have unlimited capacity according to the
        project specification.

        Args:
            drones_in_zone: Number of drones currently occupying the zone.

        Returns:
            True if the drone can enter, otherwise False.
        """
        if self.is_start or self.is_end:
            return True

        return drones_in_zone < self.max_drones

    def __hash__(self) -> int:
        """Return a hash based on the zone name."""
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        """Compare zones by their unique names."""
        if not isinstance(other, Zone):
            return NotImplemented

        return self.name == other.name
