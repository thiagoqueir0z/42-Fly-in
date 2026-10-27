"""Domain model for autonomous drones."""

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from src.model.zone import ZoneType

if TYPE_CHECKING:
    from src.model.zone import Zone


@dataclass(eq=False)
class Drone:
    """Represent a drone moving through the network."""

    drone_id: int
    current_zone: "Zone"
    path: list["Zone"] = field(default_factory=list)
    delivered: bool = field(default=False, init=False)
    turns_in_transit: int = field(default=0, init=False)
    target_zone: "Zone | None" = field(default=None, init=False)
    path_index: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        """Validate the drone configuration."""
        if self.drone_id < 1:
            raise ValueError(
                f"drone_id must be positive, got {self.drone_id}."
            )

    @property
    def name(self) -> str:
        """Return the formatted drone identifier."""
        return f"D{self.drone_id}"

    @property
    def is_in_transit(self) -> bool:
        """Return whether the drone is between two zones."""
        return self.target_zone is not None

    def set_path(self, new_path: list["Zone"]) -> None:
        """Assign a path starting at the drone's current zone.

        Args:
            new_path: Ordered list of zones from the current position to
                the destination.

        Raises:
            ValueError: If the path is invalid or starts at another zone.
        """
        if not new_path:
            raise ValueError(f"Path for {self.name} cannot be empty.")

        if new_path[0] != self.current_zone:
            raise ValueError(
                f"Path for {self.name} must start at "
                f"'{self.current_zone.name}'."
            )

        if any(zone.zone_type == ZoneType.BLOCKED for zone in new_path):
            raise ValueError(
                f"Path for {self.name} cannot contain blocked zones."
            )

        self.path = list(new_path)
        self.path_index = 0
        self.delivered = self.current_zone.is_end

    def get_next_destination(self) -> "Zone | None":
        """Return the next zone in the path.

        Returns:
            The next zone, or None when the path is complete.
        """
        next_index = self.path_index + 1

        if next_index >= len(self.path):
            return None

        return self.path[next_index]

    def advance_to_zone(self, zone: "Zone") -> None:
        """Move the drone to the next zone in its path.

        Args:
            zone: Destination zone.

        Raises:
            ValueError: If the zone is not the next planned destination.
        """
        next_zone = self.get_next_destination()
        valid_transit_arrival = self.is_in_transit and zone == self.target_zone

        if not valid_transit_arrival and next_zone != zone:
            expected = next_zone.name if next_zone else "no zone"
            raise ValueError(
                f"Invalid destination for {self.name}: "
                f"expected '{expected}', got '{zone.name}'."
            )

        self.current_zone = zone
        self.path_index += 1
        self.target_zone = None
        self.turns_in_transit = 0

        if zone.is_end:
            self.delivered = True

    def begin_transit(self, target: "Zone", turns: int) -> None:
        """Start a multi-turn movement toward a restricted zone.

        Args:
            target: Destination zone.
            turns: Number of turns remaining before arrival.

        Raises:
            ValueError: If the transit configuration is invalid.
        """
        if self.is_in_transit:
            raise ValueError(f"{self.name} is already in transit.")

        if turns < 1:
            raise ValueError(
                f"Transit duration must be positive, got {turns}."
            )

        if target == self.current_zone:
            raise ValueError(
                f"{self.name} cannot transit to its current zone."
            )

        if target.zone_type == ZoneType.BLOCKED:
            raise ValueError(
                f"{self.name} cannot transit to blocked zone "
                f"'{target.name}'."
            )

        if target != self.get_next_destination():
            raise ValueError(
                f"'{target.name}' is not the next destination for "
                f"{self.name}."
            )

        self.target_zone = target
        self.turns_in_transit = turns

    def __hash__(self) -> int:
        """Return a hash based on the drone identifier."""
        return hash(self.drone_id)

    def __eq__(self, other: object) -> bool:
        """Compare drones by their identifiers."""
        if not isinstance(other, Drone):
            return NotImplemented

        return self.drone_id == other.drone_id
