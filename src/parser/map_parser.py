from typing import Dict, List, Tuple
from src.model.graph import Graph
from src.model.zone import Zone
from src.model.connection import Connection


class MapParser:
    """Parser for drone network map configuration files.

    Attributes:
        filename (str): Path to the map configuration file.
    """

    def __init__(self, filename: str) -> None:
        """Initialize the map parser.

        Args:
            filename: Path to the map configuration file.
        """
        self.filename = filename

    def parse(self) -> Graph:
        """Parse the map configuration file and return a Graph object.

        Returns:
            A Graph object representing the parsed map.

        Raises:
            FileNotFoundError: If the map file does not exist.
            ValueError: If the map file has invalid format or syntax.
        """
        try:
            with open(self.filename, "r", encoding="utf-8") as file:
                lines = file.readlines()
        except FileNotFoundError:
            raise FileNotFoundError(f"Could Not find map file: {self.filename}")
        
        num_drones = None
        zones = []
        connections = []
        start_zone = None
        end_zone = None

        for idx, Line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                raise ValueError(f"Syntax errorat line {idx}: Missing ':' separator.")
            prefix = prefix.strip()
            rest = rest.strip()
        
        if prefix == "nb_drones":
            if num_drones is not None:
                raise ValueError(f"Duplicated nb_drones at line {idx}")
            try:
                num_drones = int(rest)
                if num_drones < 1:
                    raise ValueError
            except ValueError:
                raise ValueError(
                    f"Invalid nb_drones value at line {idx}: must be a positive integer"
                )
            continue

        elif prefix in ("start_hub", "end_hub", "hub"):
            if "[" in rest:
                parts, meta_str = rest.split("[", 1)
                meta_str = '[' + meta_str
            else:
                parts = rest
                meta_str = ""

            tokens = parts.strip().split()
            if len(tokens) < 3:
                raise ValueError(
                    f"Invalid zone definition at line {idx}: must have name, x, y"
                )
            
            name = tokens[0]
            try:
                x = int(tokens[1])
                y = int(tokens[2])
            except ValueError:
                raise ValueError(
                    f"Invalid coordinates at line {idx} for zone '{name}' (should be integers)"
                )
            






    def _parse_zone_metadata(self, metadata_str: str) -> Dict[str, str]:
        """Parse zone metadata from bracketed string.

        Args:
            metadata_str: Raw metadata string (e.g., "zone=restricted color=red").

        Returns:
            Dictionary with parsed metadata key-value pairs.

        Raises:
            ValueError: If metadata format is invalid.
        """
        pass

    def _parse_connection_metadata(self, metadata_str: str) -> Dict[str, str]:
        """Parse connection metadata from bracketed string.

        Args:
            metadata_str: Raw metadata string (e.g., "max_link_capacity=2").

        Returns:
            Dictionary with parsed metadata key-value pairs.

        Raises:
            ValueError: If metadata format is invalid.
        """
        pass

    def _validate_zone_type(self, zone_type: str) -> None:
        """Validate zone type is one of the allowed types.

        Args:
            zone_type: The zone type to validate.

        Raises:
            ValueError: If zone type is invalid.
        """
        pass
