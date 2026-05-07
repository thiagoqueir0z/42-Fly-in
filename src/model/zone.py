"""Zone class representing locations in the drone network."""

from typing import Optional


class Zone:
    """Represents a zone in the drone network.

    A zone is a location where drones can be positioned. Each zone has
    a position, a type (normal, restricted, priority, blocked), and
    capacity constraints.

    Attributes:
        name (str): Unique identifier for the zone.
        x (int): X coordinate of the zone.
        y (int): Y coordinate of the zone.
        zone_type (str): Type of zone (normal, restricted, priority, blocked).
        color (Optional[str]): Optional color for visualization.
        max_drones (int): Maximum number of drones in this zone simultaneously.
        is_start (bool): Whether this is the starting zone.
        is_end (bool): Whether this is the ending zone.
    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str = "normal",
        color: Optional[str] = None,
        max_drones: int = 1,
        is_start: bool = False,
        is_end: bool = False,
    ) -> None:
        """Initialize a Zone.

        Args:
            name: Unique identifier for the zone.
            x: X coordinate.
            y: Y coordinate.
            zone_type: Type of zone (default: "normal").
            color: Optional color for visualization.
            max_drones: Maximum drones allowed (default: 1).
            is_start: Whether this is the start hub (default: False).
            is_end: Whether this is the end hub (default: False).

        Raises:
            ValueError: If max_drones is less than 1.
            ValueError: If zone_type is invalid.
        """
        pass

    def get_movement_cost(self) -> int:
        """Get the movement cost to enter this zone.

        Returns:
            1 for normal/priority zones, 2 for restricted zones.

        Raises:
            ValueError: If zone is blocked (cannot be entered).
        """
        pass

    def can_accommodate_drone(self, current_count: int) -> bool:
        """Check if the zone can accommodate another drone.

        Args:
            current_count: Current number of drones in the zone.

        Returns:
            True if capacity allows, False otherwise.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of the zone.

        Returns:
            String in format: Zone(name, type, capacity).
        """
        pass

    def __hash__(self) -> int:
        """Return hash of the zone based on its name.

        Returns:
            Hash value of the zone name.
        """
        pass

    def __eq__(self, other: object) -> bool:
        """Check equality with another zone.

        Args:
            other: Object to compare with.

        Returns:
            True if both zones have the same name.
        """
        pass
