"""Tests for the drone domain model."""

import pytest

from src.model.drone import Drone
from src.model.zone import Zone, ZoneType


def make_path() -> tuple[Zone, Zone, Zone]:
    """Create a simple start-to-goal path."""
    start = Zone("start", 0, 0, is_start=True)
    middle = Zone("middle", 1, 0)
    goal = Zone("goal", 2, 0, is_end=True)

    return start, middle, goal


def test_drone_name_uses_its_identifier() -> None:
    """The drone name must use the D<ID> format."""
    start, _, _ = make_path()
    drone = Drone(3, start)

    assert drone.name == "D3"


def test_drone_identifier_must_be_positive() -> None:
    """Drone identifiers must start at one."""
    start, _, _ = make_path()

    with pytest.raises(ValueError):
        Drone(0, start)


def test_set_path_starts_at_current_zone() -> None:
    """A path must start where the drone currently is."""
    start, middle, goal = make_path()
    drone = Drone(1, start)

    drone.set_path([start, middle, goal])

    assert drone.get_next_destination() == middle
    assert drone.path_index == 0


def test_path_cannot_start_at_another_zone() -> None:
    """A path beginning elsewhere must be rejected."""
    start, middle, goal = make_path()
    drone = Drone(1, start)

    with pytest.raises(ValueError):
        drone.set_path([middle, goal])


def test_empty_path_is_rejected() -> None:
    """An empty path must be rejected."""
    start, _, _ = make_path()
    drone = Drone(1, start)

    with pytest.raises(ValueError):
        drone.set_path([])


def test_blocked_zone_is_rejected_from_path() -> None:
    """A path cannot contain blocked zones."""
    start, _, goal = make_path()
    blocked = Zone("blocked", 1, 1, ZoneType.BLOCKED)
    drone = Drone(1, start)

    with pytest.raises(ValueError):
        drone.set_path([start, blocked, goal])


def test_advance_moves_to_the_next_zone() -> None:
    """Advancing must update the position and path index."""
    start, middle, goal = make_path()
    drone = Drone(1, start)
    drone.set_path([start, middle, goal])

    drone.advance_to_zone(middle)

    assert drone.current_zone == middle
    assert drone.path_index == 1
    assert drone.get_next_destination() == goal


def test_wrong_destination_is_rejected() -> None:
    """A drone cannot skip the next planned zone."""
    start, middle, goal = make_path()
    drone = Drone(1, start)
    drone.set_path([start, middle, goal])

    with pytest.raises(ValueError):
        drone.advance_to_zone(goal)


def test_arriving_at_end_marks_drone_as_delivered() -> None:
    """A drone is delivered when it reaches the end zone."""
    start, middle, goal = make_path()
    drone = Drone(1, start)
    drone.set_path([start, middle, goal])

    drone.advance_to_zone(middle)
    drone.advance_to_zone(goal)

    assert drone.delivered
    assert drone.get_next_destination() is None


def test_transit_requires_positive_duration() -> None:
    """Transit duration must be positive."""
    start = Zone("start", 0, 0, is_start=True)
    restricted = Zone("tunnel", 1, 0, ZoneType.RESTRICTED)
    drone = Drone(1, start)
    drone.set_path([start, restricted])

    with pytest.raises(ValueError):
        drone.begin_transit(restricted, 0)


def test_begin_transit_sets_target_and_duration() -> None:
    """Starting transit must store its target and remaining turns."""
    start = Zone("start", 0, 0, is_start=True)
    restricted = Zone("tunnel", 1, 0, ZoneType.RESTRICTED)
    drone = Drone(1, start)
    drone.set_path([start, restricted])

    drone.begin_transit(restricted, 1)

    assert drone.is_in_transit
    assert drone.target_zone == restricted
    assert drone.turns_in_transit == 1


def test_transit_arrival_clears_transit_state() -> None:
    """Arriving after transit must clear the temporary state."""
    start = Zone("start", 0, 0, is_start=True)
    restricted = Zone("tunnel", 1, 0, ZoneType.RESTRICTED)
    drone = Drone(1, start)
    drone.set_path([start, restricted])
    drone.begin_transit(restricted, 1)

    drone.advance_to_zone(restricted)

    assert drone.current_zone == restricted
    assert not drone.is_in_transit
    assert drone.turns_in_transit == 0


def test_second_transit_is_rejected() -> None:
    """A drone cannot start a second transit before arriving."""
    start = Zone("start", 0, 0, is_start=True)
    restricted = Zone("tunnel", 1, 0, ZoneType.RESTRICTED)
    drone = Drone(1, start)
    drone.set_path([start, restricted])
    drone.begin_transit(restricted, 1)

    with pytest.raises(ValueError):
        drone.begin_transit(restricted, 1)
