"""Tests for the map parser."""

from pathlib import Path

import pytest

from src.parser.map_parser import MapParser, MapParserError


def write_map(tmp_path: Path, content: str) -> Path:
    """Write a temporary map file."""
    path = tmp_path / "map.txt"
    path.write_text(content, encoding="utf-8")
    return path


def valid_map() -> str:
    """Return a minimal valid map."""
    return """\
nb_drones: 2
start_hub: start 0 0
hub: middle 1 0 [max_drones=2 color=blue]
end_hub: goal 2 0 [max_drones=10]
connection: start-middle [max_link_capacity=2]
connection: middle-goal
"""


def test_parse_valid_map(tmp_path: Path) -> None:
    """A valid map must produce a populated graph."""
    graph = MapParser(write_map(tmp_path, valid_map())).parse()

    assert graph.num_drones == 2
    assert graph.start_zone is not None
    assert graph.end_zone is not None
    assert len(graph.zones) == 3
    assert len(graph.connections) == 2
    assert graph.zones["middle"].max_drones == 2


def test_inline_comments_are_ignored(tmp_path: Path) -> None:
    """Comments after valid content must be ignored."""
    content = valid_map().replace(
        "nb_drones: 2",
        "nb_drones: 2 # number of drones",
    )

    graph = MapParser(write_map(tmp_path, content)).parse()

    assert graph.num_drones == 2


def test_missing_file_is_rejected(tmp_path: Path) -> None:
    """A missing map file must raise a parser error."""
    with pytest.raises(MapParserError, match="Map file not found"):
        MapParser(tmp_path / "missing.txt").parse()


def test_invalid_drone_count_is_rejected(tmp_path: Path) -> None:
    """The number of drones must be positive."""
    path = write_map(tmp_path, "nb_drones: 0\n")

    with pytest.raises(MapParserError, match="positive integer"):
        MapParser(path).parse()


def test_first_line_must_define_drones(tmp_path: Path) -> None:
    """The header must be the first meaningful line."""
    path = write_map(tmp_path, "hub: start 0 0\n")

    with pytest.raises(MapParserError, match="first line"):
        MapParser(path).parse()


def test_invalid_zone_type_is_rejected(tmp_path: Path) -> None:
    """Zone types must be supported by the subject."""
    content = valid_map().replace(
        "hub: middle 1 0 [max_drones=2 color=blue]",
        "hub: middle 1 0 [zone=unknown]",
    )

    with pytest.raises(MapParserError, match="invalid zone type"):
        MapParser(write_map(tmp_path, content)).parse()


def test_invalid_zone_capacity_is_rejected(tmp_path: Path) -> None:
    """Regular zone capacity must be positive."""
    content = valid_map().replace(
        "max_drones=2",
        "max_drones=0",
    )

    with pytest.raises(MapParserError, match="max_drones"):
        MapParser(write_map(tmp_path, content)).parse()


def test_start_and_end_capacity_metadata_is_ignored(tmp_path: Path) -> None:
    """Start and end capacities are ignored by the subject rules."""
    content = valid_map().replace(
        "start_hub: start 0 0",
        "start_hub: start 0 0 [max_drones=0]",
    ).replace(
        "end_hub: goal 2 0 [max_drones=10]",
        "end_hub: goal 2 0 [max_drones=0]",
    )

    graph = MapParser(write_map(tmp_path, content)).parse()

    assert graph.start_zone is not None
    assert graph.end_zone is not None


def test_unknown_metadata_is_rejected(tmp_path: Path) -> None:
    """Unknown metadata keys must not be silently ignored."""
    content = valid_map().replace(
        "max_drones=2",
        "max_drone=2",
    )

    with pytest.raises(MapParserError, match="unknown metadata key"):
        MapParser(write_map(tmp_path, content)).parse()


def test_duplicate_metadata_is_rejected(tmp_path: Path) -> None:
    """The same metadata key cannot appear twice."""
    content = valid_map().replace(
        "color=blue",
        "color=blue color=red",
    )

    with pytest.raises(MapParserError, match="duplicate metadata key"):
        MapParser(write_map(tmp_path, content)).parse()


def test_malformed_metadata_is_rejected(tmp_path: Path) -> None:
    """Metadata tokens must use the key=value form."""
    content = valid_map().replace(
        "color=blue",
        "color",
    )

    with pytest.raises(MapParserError, match="invalid metadata token"):
        MapParser(write_map(tmp_path, content)).parse()


def test_unclosed_metadata_is_rejected(tmp_path: Path) -> None:
    """Metadata blocks must have both brackets."""
    content = valid_map().replace(
        "[max_drones=2 color=blue]",
        "[max_drones=2 color=blue",
    )

    with pytest.raises(MapParserError, match="enclosed"):
        MapParser(write_map(tmp_path, content)).parse()


def test_unknown_zone_directive_is_rejected(tmp_path: Path) -> None:
    """Only hub, start_hub, and end_hub are valid zone directives."""
    content = valid_map().replace("hub: middle", "station: middle")

    with pytest.raises(MapParserError, match="unknown map directive"):
        MapParser(write_map(tmp_path, content)).parse()


def test_unknown_zone_reference_is_rejected(tmp_path: Path) -> None:
    """Connections must reference declared zones."""
    content = valid_map().replace(
        "connection: middle-goal",
        "connection: middle-missing",
    )

    with pytest.raises(MapParserError, match="unknown zone"):
        MapParser(write_map(tmp_path, content)).parse()


def test_invalid_link_capacity_is_rejected(tmp_path: Path) -> None:
    """Link capacity must be a positive integer."""
    content = valid_map().replace(
        "max_link_capacity=2",
        "max_link_capacity=0",
    )

    with pytest.raises(MapParserError, match="max_link_capacity"):
        MapParser(write_map(tmp_path, content)).parse()


def test_missing_start_is_rejected(tmp_path: Path) -> None:
    """A map must contain one start hub."""
    content = valid_map().replace("start_hub: start 0 0\n", "")

    with pytest.raises(MapParserError, match="start_hub"):
        MapParser(write_map(tmp_path, content)).parse()


def test_missing_end_is_rejected(tmp_path: Path) -> None:
    """A map must contain one end hub."""
    content = valid_map().replace(
        "end_hub: goal 2 0 [max_drones=10]\n",
        "",
    )

    with pytest.raises(MapParserError, match="end_hub"):
        MapParser(write_map(tmp_path, content)).parse()
