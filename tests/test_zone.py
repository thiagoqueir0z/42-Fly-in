"""Tests for the zone domain model."""

import pytest

from src.model.zone import Zone, ZoneType


def test_normal_zone_costs_one_turn() -> None:
    """Normal zones must cost one turn to enter."""
    zone = Zone("hall", 1, 2)

    assert zone.get_movement_cost() == 1


def test_priority_zone_costs_one_turn() -> None:
    """Priority zones have the same movement cost as normal zones."""
    zone = Zone("priority", 1, 2, ZoneType.PRIORITY)

    assert zone.get_movement_cost() == 1


def test_restricted_zone_costs_two_turns() -> None:
    """Restricted zones must cost two turns to enter."""
    zone = Zone("tunnel", 1, 2, ZoneType.RESTRICTED)

    assert zone.get_movement_cost() == 2


def test_blocked_zone_cannot_be_entered() -> None:
    """Blocked zones must reject movement."""
    zone = Zone("wall", 1, 2, ZoneType.BLOCKED)

    with pytest.raises(ValueError):
        zone.get_movement_cost()


def test_regular_zone_has_capacity_one_by_default() -> None:
    """A regular zone holds one drone by default."""
    zone = Zone("hall", 1, 2)

    assert zone.can_accommodate_drone(0)
    assert not zone.can_accommodate_drone(1)


def test_zone_with_custom_capacity() -> None:
    """A zone must respect its configured capacity."""
    zone = Zone("hall", 1, 2, max_drones=2)

    assert zone.can_accommodate_drone(1)
    assert not zone.can_accommodate_drone(2)


def test_start_and_end_have_unlimited_capacity() -> None:
    """Start and end zones ignore their normal capacity limit."""
    start = Zone("start", 0, 0, is_start=True)
    end = Zone("end", 10, 10, is_end=True)

    assert start.can_accommodate_drone(100)
    assert end.can_accommodate_drone(100)


def test_empty_zone_name_is_rejected() -> None:
    """A zone must have a name."""
    with pytest.raises(ValueError):
        Zone("", 0, 0)


def test_invalid_zone_name_is_rejected() -> None:
    """Spaces and dashes are forbidden in zone names."""
    with pytest.raises(ValueError):
        Zone("invalid-name", 0, 0)

    with pytest.raises(ValueError):
        Zone("invalid name", 0, 0)


def test_non_positive_capacity_is_rejected() -> None:
    """Zone capacity must be a positive integer."""
    with pytest.raises(ValueError):
        Zone("hall", 0, 0, max_drones=0)
