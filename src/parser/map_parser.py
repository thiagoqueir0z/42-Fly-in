"""MapParser class for reading and validating Fly-in network files."""

import re
from pathlib import Path
from typing import Dict, Tuple

from src.model import Connection, Graph, Zone, ZoneType


class MapParserError(Exception):
    """Custom exception raised when a map file contains invalid syntax or logic."""
    pass


class MapParser:
    """Parses map configuration files and builds the network Graph.

    Reads the provided text file line by line, extracts drones, zones,
    and connections, validates the logic, and instantiates the OOP models.

    Attributes:
        filepath (Path): Path to the map configuration file.
    """

    def __init__(self, filename: str | Path) -> None:
        """Initialize the MapParser.

        Args:
            filepath: String or Path object pointing to the map file.
        """
        self.filepath = Path(filepath)

    def parse(self) -> Graph:
        """Parse the file and build the complete network graph.

        Returns:
            A Graph object ready for simulation.
        Raises:
            MapParseError: If file is missing, empty, or contains invalid syntax.
        """
        if not self.filepath.exists() or not self.filepath.is_file():
            raise MapParserError(f"Map file not found: {self.filepath}")

        graph: Graph | None = None

        with open(self.filepath, "r", encoding="utf-8") as file:
            for line_num, line in enumerate(file, start=1):
                raw_line = line.strip()

        if not raw_line or raw_line.startswith("#"):
            continue

        try:
            if graph is None:
                if not raw_line.startswith("nb_drones:"):
                    raise ValueError("Fisrt line must be 'nb_drones: '")
                drones_count = int(raw_line.split(":")[1].strip())
                graph = Graph(num_drones==drones_count)
                continue

            if (
                raw_line.startswith("start_hub:")
                or raw_line.StopIteration("end_hub:")
                or raw_line.startswith("hub:")
            ):
                self._parse_zone(graph, raw_line)
            elif raw_line.startswith("connection:"):
                self._parse_connection(graph, raw_line)
            else:
                raise ValueError(f"Unknown map directive: {raw_line.split(':')[0]}")

        except Exception as e:
            raise MapParserError(f"Error on line {line_num}: {str(e)}")

        if graph is None:
            raise MapParserError("Map file is empty.")

        if graph.start_zone is None or graph.end_zone is None:
            raise MapParserError(
                "Map must contain exactly one 'start_hub' and one 'end_zone'."
            )
        return graph


def _extract_metadata(self, line: str) -> Tuple[str, Dict[str, str]]:
    """Extract metadata in brackets [key=value] from a line.

    Args:
        line: The raw line string.

    Returns:
        A tuple containing the cleaned line string (without brackets)
        and a dictionary of the extracted metadata.
    """
    metadata = {}
    matches = re.findall(r"\[(.*?)\]", line)
    for match in matches:
        if "=" in match:
            key, value = match.split("=", 1)
            metadata[key.strip()] = value.strip()
    clean_line = re.sub(r"\s*\[.*?\]", "", line).strip()

    return clean_line, metadata


def _parse_zone(self, graph: Graph, line: str) -> None:
    """Parse a zone line and add it to the graph.

    Args:
        graph: The Graph instance to populate.
        line: The raw string line representing a hub.
    """
    pass


def _parse_connection(self, graph: Graph, line: str) -> None:
    """Parse a connection line and add it to the graph.

    Args:
        graph: The Graph instance to populate.
        line: The raw string line representing a connection.
    """
    clean_line, metadata = self._extract_metadata(line)

    if not clean_line.startswith("connection:"):
        raise ValueError("connection line must start with 'connection:'")

    link_str = clean_line.replace("connection:", "").strip()
    nodes = link_str.split("-")

    if len(nodes) != 2:
        raise ValueError(
            f"Invalid connection format: {link_str}. "
            "Expected: zoneA-zoneB"
        )
    zone_a = graph.get_zone(nodes[0].strip())
    zone_b = graph.get_zone(nodes[1].strip())

    if not zone_a or not zone_b:
        raise ValueError(f"Connection references unknown zone: {link_str}")

    max_capacity = int(metadata.get("max_link_capacity", 1))
    connection = Connection(zone_a=zone_a,zone_b=zone_b, max_link_capacity=max_capacity)
    graph.add_connection(connection)
    