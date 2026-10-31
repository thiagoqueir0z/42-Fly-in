"""Drone class representing autonomous delivery units."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional, List

if TYPE_CHECKING:
    from src.model.zone import Zone


@dataclass(eq=False)
class Drone:
    """Represents an autonomous drone traversing the network.

    Attributes:
        drone_id (int): Unique identifier for the drone.
        current_zone (Zone): The zone where the drone is currently located.
        path (List[Zone]): The planned route of zones to traverse.
        delivered (bool): Flag indicating if the drone reached the end zone.
        turns_in_transit (int): Remaining turns if the drone is in multi-turn transit.
        target_zone (Optional[Zone]): The destination zone if currently in transit.
        path_index (int): Current position index within the planned path.
    """

    drone_id: int
    current_zone: "Zone"
    path: List["Zone"] = field(default_factory=list)
    delivered: bool = field(default=False, init=False)
    turns_in_transit: int = field(default=0, init=False)
    target_zone: Optional["Zone"] = field(default=None, init=False)
    path_index: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Validate drone identifier.

        Raises:
            ValueError: If drone_id is less than 1.
        """
        if self.drone_id < 1:
            raise ValueError(f"drone_id must be a positive integer, got {self.drone_id}")

    @property
    def name(self) -> str:
        """Format drone ID for output as required by the subject (e.g., 'D1').

        Returns:
            A string containing 'D' followed by the drone ID.
        """
        return f"D{self.drone_id}"

    def set_path(self, new_path: List["Zone"]) -> None:
        """Assign a planned route to the drone.

        Args:
            new_path: A list of Zone objects representing the route.

        Raises:
            ValueError: If the provided path is empty.
        """
        if not new_path:
            raise ValueError(f"Path for {self.name} cannot be empty.")
        self.path = new_path
        self.path_index = 0

    def get_next_destination(self) -> Optional["Zone"]:
        """Return the next zone in the route without applying movement.

        Returns:
            The next Zone in the path, or None if the path is complete.
        """
        if self.path_index < len(self.path):
            return self.path[self.path_index]
        return None

    def advance_to_zone(self, zone: "Zone") -> None:
        """Complete movement to a zone and evaluate delivery status.

        Args:
            zone: The destination Zone to move into.
        """
        self.current_zone = zone
        self.target_zone = None
        self.turns_in_transit = 0

        if self.get_next_destination() == zone:
            self.path_index += 1

        if zone.is_end:
            self.delivered = True

    def begin_transit(self, target: "Zone", turns: int) -> None:
        """Enter transit state for multi-turn movements (e.g., restricted zones).

        Args:
            target: The destination Zone being traveled to.
            turns: The number of turns required to complete the transit.
        """
        self.target_zone = target
        self.turns_in_transit = turns

    def __hash__(self) -> int:
        """Drone identity is tied strictly to its ID.

        Returns:
            An integer hash of the drone ID.
        """
        return hash(self.drone_id)

    def __eq__(self, other: object) -> bool:
        """Check equality with another drone based on ID.

        Args:
            other: The object to compare with.

        Returns:
            True if the other object is a Drone with the same ID, False otherwise.
        """
        if not isinstance(other, Drone):
            return NotImplemented
        return self.drone_id == other.drone_id
