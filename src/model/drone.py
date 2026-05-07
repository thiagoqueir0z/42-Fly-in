"""Drone class representing autonomous delivery units."""

from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from src.model.zone import Zone


class Drone:
    """Represents an autonomous drone in the network.

    A drone has a unique ID, current position, and a path to follow.
    It can move between connected zones and has state tracking for
    simulation purposes.

    Attributes:
        drone_id (int): Unique identifier for the drone.
        current_zone (Zone): Current zone of the drone.
        path (List[Zone]): Planned path from start to end.
        delivered (bool): Whether the drone has reached the end zone.
        turns_in_transit (int): Turns remaining if in restricted zone transit.
    """

    def __init__(self, drone_id: int, start_zone: "Zone") -> None:
        """Initialize a Drone.

        Args:
            drone_id: Unique identifier for this drone.
            start_zone: The zone where the drone starts.
        """
        pass

    def set_path(self, path: List["Zone"]) -> None:
        """Set the planned path for this drone.

        Args:
            path: List of zones representing the path from start to end.

        Raises:
            ValueError: If path is empty.
        """
        pass

    def move_to_zone(self, zone: "Zone") -> bool:
        """Move the drone to an adjacent zone.

        Args:
            zone: The destination zone.

        Returns:
            True if movement was successful, False otherwise.
        """
        pass

    def mark_delivered(self) -> None:
        """Mark the drone as delivered (reached end zone)."""
        pass

    def is_delivered(self) -> bool:
        """Check if the drone has reached the end zone.

        Returns:
            True if drone is delivered, False otherwise.
        """
        pass

    def get_next_destination(self) -> Optional["Zone"]:
        """Get the next zone in the planned path.

        Returns:
            The next zone to visit, or None if path is complete.
        """
        pass

    def __repr__(self) -> str:
        """Return string representation of the drone.

        Returns:
            String in format: Drone(ID, current_zone, status).
        """
        pass

    def __hash__(self) -> int:
        """Return hash of the drone based on its ID.

        Returns:
            Hash value of the drone ID.
        """
        pass

    def __eq__(self, other: object) -> bool:
        """Check equality with another drone.

        Args:
            other: Object to compare with.

        Returns:
            True if both drones have the same ID.
        """
        pass
