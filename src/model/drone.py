"""Drone class representing autonomous delivery units."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from src.model.zone import Zone


@dataclass(eq=False)
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
    drone_id: int
    current_zone: "Zone"
    path: List["Zone"] = field(default_factory=list)
    delivered: bool = field(default=False, init=False)
    turns_in_transit: int = field(default=0, init=False)
    target_zone: Optional["Zone"] = field(default=None, init=False)
    path_index: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Validate attributes after dataclass initialization."""
        if self.drone_id < 1:
            raise ValueError(f"drone_id must be a positive integer, got {self.drone_id}")

    @property
    def name(self) -> str:
        """Return the formatted drone ID as required by the simulation output.

        Returns:
            String in format 'D' (e.g., 'D1', 'D2').
        """
        return f"D{self.drone_id}"

    def set_path(self, new_path: List["Zone"]) -> None:
        """Set or update the planned path for this drone.

        Args:
            new_path: List of zones representing the path from start to end.

        Raises:
            ValueError: If path is empty.
        """
        if not new_path:
            raise ValueError(f"Path for {self.name} cannot be empty.")
        self.path = new_path
        self.path_index = 0

    def get_next_destination(self) -> Optional["Zone"]:
        """Get the next zone in the planned path without moving.

        Returns:
            The next zone to visit, or None if path is complete.
        """
        if self.path_index < len(self.path):
            return self.path[self.path_index]
        return None

    def advance_to_zone(self, zone: "Zone") -> None:
        """Instantly move the drone to a new zone and update its path progress.

        Args:
            zone: The destination zone.
        """
        self.current_zone = zone
        self.target_zone = None
        self.turns_in_transit = 0
        if self.get_next_destination() == zone:
            self.path_index += 1
        if zone.is_end:
            self.delivered = True

    def begin_transit(self, target: "Zone", turns: int) -> None:
        """Put the drone in a transit state towards a zone requiring multiple turns.

        Args:
            target: The destination zone it is traveling towards.
            turns: How many turns the transit will take.
        """
        self.target_zone = target
        self.turns_in_transit = turns

    def __hash__(self) -> int:
        """Return hash of the drone based on its immutable ID."""
        return hash(self.drone_id)

    def __eq__(self, other: object) -> bool:
        """Check equality with another drone based on ID."""
        if not isinstance(other, Drone):
            return NotImplemented
        return self.drone_id == other.drone_id
