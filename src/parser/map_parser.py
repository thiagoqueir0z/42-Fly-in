"""Parser for Fly-in map configuration files."""

from pathlib import Path

from src.model import Connection, Graph, Zone, ZoneType


class MapParserError(Exception):
    """Raised when a map file is invalid."""


class MapParser:
    """Parse a map file and build a drone network graph."""

    ZONE_METADATA = {"zone", "color", "max_drones"}
    CONNECTION_METADATA = {"max_link_capacity"}

    def __init__(self, filepath: str | Path) -> None:
        """Store the map file path."""
        self.filepath = Path(filepath)

    def parse(self) -> Graph:
        """Parse the map and return the resulting graph.

        Raises:
            MapParserError: If the file contains invalid syntax or data.
        """
        if not self.filepath.is_file():
            raise MapParserError(f"Map file not found: {self.filepath}")

        graph: Graph | None = None

        try:
            with self.filepath.open("r", encoding="utf-8") as map_file:
                for line_number, raw_line in enumerate(map_file, start=1):
                    line = self._remove_comment(raw_line)
                    if not line:
                        continue

                    try:
                        if graph is None:
                            graph = self._parse_header(line)
                        else:
                            self._parse_line(graph, line)
                    except (ValueError, KeyError) as error:
                        raise MapParserError(
                            f"Error on line {line_number}: {error}"
                        ) from error
        except OSError as error:
            raise MapParserError(
                f"Could not read map file '{self.filepath}': {error}"
            ) from error

        if graph is None:
            raise MapParserError("Map file is empty.")

        if graph.start_zone is None:
            raise MapParserError("Map must contain one 'start_hub'.")

        if graph.end_zone is None:
            raise MapParserError("Map must contain one 'end_hub'.")

        return graph

    @staticmethod
    def _remove_comment(line: str) -> str:
        """Remove an optional inline comment."""
        return line.split("#", 1)[0].strip()

    def _parse_header(self, line: str) -> Graph:
        """Parse the mandatory first directive."""
        prefix = "nb_drones:"
        if not line.startswith(prefix):
            raise ValueError(
                "first line must be 'nb_drones: <positive_integer>'"
            )

        value = line[len(prefix):].strip()
        if not value or not value.isdigit() or int(value) < 1:
            raise ValueError("number of drones must be a positive integer")

        return Graph(num_drones=int(value))

    def _parse_line(self, graph: Graph, line: str) -> None:
        """Parse one zone or connection directive."""
        if line.startswith(("start_hub:", "end_hub:", "hub:")):
            self._parse_zone(graph, line)
            return

        if line.startswith("connection:"):
            self._parse_connection(graph, line)
            return

        raise ValueError(f"unknown map directive: {line}")

    def _extract_metadata(
        self,
        line: str,
        allowed_keys: set[str],
    ) -> tuple[str, dict[str, str]]:
        """Extract and validate one metadata block."""
        open_bracket = line.find("[")
        close_bracket = line.rfind("]")

        if open_bracket == -1 and close_bracket == -1:
            return line.strip(), {}

        if open_bracket == -1 or close_bracket == -1:
            raise ValueError("metadata must be enclosed in '[...]'")

        if line.find("[", open_bracket + 1) != -1:
            raise ValueError("only one metadata block is allowed")

        if line.find("]", close_bracket + 1) != -1:
            raise ValueError("only one metadata block is allowed")

        trailing_text = line[close_bracket + 1:].strip()
        if trailing_text:
            raise ValueError("unexpected text after metadata block")

        clean_line = line[:open_bracket].strip()
        content = line[open_bracket + 1:close_bracket].strip()
        if not content:
            raise ValueError("metadata block cannot be empty")

        metadata: dict[str, str] = {}
        for token in content.split():
            if "=" not in token:
                raise ValueError(
                    f"invalid metadata token '{token}', expected key=value"
                )

            key, value = token.split("=", 1)
            if not key or not value:
                raise ValueError(f"invalid metadata token '{token}'")

            if key not in allowed_keys:
                raise ValueError(f"unknown metadata key '{key}'")

            if key in metadata:
                raise ValueError(f"duplicate metadata key '{key}'")

            metadata[key] = value

        return clean_line, metadata

    def _parse_zone(self, graph: Graph, line: str) -> None:
        """Parse and add a zone."""
        clean_line, metadata = self._extract_metadata(
            line,
            self.ZONE_METADATA,
        )
        parts = clean_line.split()

        if len(parts) != 4:
            raise ValueError(
                "zone format must be: <directive> <name> <x> <y>"
            )

        directive, name, x_text, y_text = parts
        if directive not in {"start_hub:", "end_hub:", "hub:"}:
            raise ValueError(f"invalid zone directive '{directive}'")

        try:
            x = int(x_text)
            y = int(y_text)
        except ValueError as error:
            raise ValueError("zone coordinates must be integers") from error

        try:
            zone_type = ZoneType(metadata.get("zone", "normal").lower())
        except ValueError as error:
            raise ValueError(
                f"invalid zone type '{metadata.get('zone')}'"
            ) from error

        is_start = directive == "start_hub:"
        is_end = directive == "end_hub:"
        max_drones = 1 if is_start or is_end else self._positive_integer(
            metadata.get("max_drones", "1"),
            "max_drones",
        )

        graph.add_zone(
            Zone(
                name=name,
                x=x,
                y=y,
                zone_type=zone_type,
                color=metadata.get("color"),
                max_drones=max_drones,
                is_start=is_start,
                is_end=is_end,
            )
        )

    def _parse_connection(self, graph: Graph, line: str) -> None:
        """Parse and add a bidirectional connection."""
        clean_line, metadata = self._extract_metadata(
            line,
            self.CONNECTION_METADATA,
        )
        prefix = "connection:"
        link_text = clean_line[len(prefix):].strip()
        zones = link_text.split("-")

        if len(zones) != 2 or not all(zone.strip() for zone in zones):
            raise ValueError(
                "connection format must be: connection: <zone1>-<zone2>"
            )

        zone_a = graph.get_zone(zones[0].strip())
        zone_b = graph.get_zone(zones[1].strip())
        if zone_a is None or zone_b is None:
            raise ValueError(
                f"connection references unknown zone(s): {link_text}"
            )

        capacity = self._positive_integer(
            metadata.get("max_link_capacity", "1"),
            "max_link_capacity",
        )
        graph.add_connection(
            Connection(zone_a, zone_b, max_link_capacity=capacity)
        )

    @staticmethod
    def _positive_integer(value: str, field_name: str) -> int:
        """Parse a positive integer metadata value."""
        try:
            number = int(value)
        except ValueError as error:
            raise ValueError(
                f"{field_name} must be a positive integer"
            ) from error

        if number < 1:
            raise ValueError(f"{field_name} must be a positive integer")

        return number
