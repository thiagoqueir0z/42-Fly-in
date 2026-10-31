"""MapParser class for reading and validating Fly-in network files."""

import re
from pathlib import Path
from typing import Dict, Tuple

from src.model import Connection, Graph, Zone, ZoneType


class MapParserError(Exception):
    """Custom exception raised when a map file contains invalid syntax."""
    pass


class MapParser:
    """Parses map configuration files and builds the network Graph.

    Attributes:
        filepath (Path): The path to the map configuration file.
    """

    def __init__(self, filepath: str | Path) -> None:
        """Initialize the MapParser.

        Args:
            filepath: String or Path object pointing to the map file.
        """
        self.filepath = Path(filepath)

    def parse(self) -> Graph:
        """Parse the file line by line and build the Graph object.

        Returns:
            A populated Graph object ready for pathfinding and simulation.

        Raises:
            MapParserError: If the file is missing, empty, or lacks start/end hubs.
            ValueError: If the file contains unknown directives or syntax errors.
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
                            raise ValueError("First line must define 'nb_drones:'")
                        drones_count = int(raw_line.split(":")[1].strip())
                        graph = Graph(num_drones=drones_count)
                        continue

                    if (
                        raw_line.startswith("start_hub:")
                        or raw_line.startswith("end_hub:")
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
                "Map must contain exactly one 'start_hub' and one 'end_hub'."
            )
        return graph

    def _extract_metadata(self, line: str) -> Tuple[str, Dict[str, str]]:
        """Extract [key=value] metadata blocks into a dictionary.

        Args:
            line: The raw line string from the file.

        Returns:
            A tuple containing the cleaned line string (without brackets)
            and a dictionary of the extracted metadata key-value pairs.
        """
        metadata = {}
        matches = re.findall(r"\[(.*?)\]", line)
        for match in matches:
            pairs = match.split()
            for pair in pairs:
                if "=" in pair:
                    key, value = pair.split("=", 1)
                    metadata[key.strip()] = value.strip()

        clean_line = re.sub(r"\s*\[.*?\]", "", line).strip()
        return clean_line, metadata

    def _parse_zone(self, graph: Graph, line: str) -> None:
        """Parse a zone directive and inject it into the graph.

        Args:
            graph: The Graph instance being populated.
            line: The raw string line representing a zone/hub.

        Raises:
            ValueError: If the zone format is invalid or contains an unknown ZoneType.
        """
        clean_line, metadata = self._extract_metadata(line)
        parts = clean_line.split()

        if len(parts) != 4:
            raise ValueError(
                f"Invalid zone format. Expected <directive> <name> <x> <y>. Got: {clean_line}"
            )

        hub_directive = parts[0]
        name = parts[1]
        x = int(parts[2])
        y = int(parts[3])

        is_start = hub_directive == "start_hub:"
        is_end = hub_directive == "end_hub:"
        zone_type_str = metadata.get("zone", "NORMAL").upper()

        try:
            zone_type = ZoneType[zone_type_str]
        except KeyError:
            raise ValueError(f"Invalid zone type in metadata: {zone_type_str}")

        max_drones = int(metadata.get("max_drones", 1))
        color = metadata.get("color", None)

        zone = Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
            is_start=is_start,
            is_end=is_end
        )
        graph.add_zone(zone)

    def _parse_connection(self, graph: Graph, line: str) -> None:
        """Parse a connection directive and inject it into the graph.

        Args:
            graph: The Graph instance being populated.
            line: The raw string line representing a connection.

        Raises:
            ValueError: If the connection format is invalid or references unknown zones.
        """
        clean_line, metadata = self._extract_metadata(line)

        if not clean_line.startswith("connection:"):
            raise ValueError("Connection line must start with 'connection:'")

        link_str = clean_line.replace("connection:", "").strip()
        nodes = link_str.split("-")

        if len(nodes) != 2:
            raise ValueError(f"Invalid connection format. Expected zoneA-zoneB. Got: {link_str}")

        zone_a = graph.get_zone(nodes[0].strip())
        zone_b = graph.get_zone(nodes[1].strip())

        if not zone_a or not zone_b:
            raise ValueError(f"Connection references unknown zone(s): {link_str}")

        max_capacity = int(metadata.get("max_link_capacity", 1))
        connection = Connection(
            zone_a=zone_a,
            zone_b=zone_b,
            max_link_capacity=max_capacity
        )
        graph.add_connection(connection)
