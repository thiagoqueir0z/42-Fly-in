"""Entry point for the Fly-in drone routing simulation."""

import sys
from pathlib import Path

from src.parser.map_parser import MapParser, MapParserError


def main() -> int:
    """Run the main simulation program.

    Parses command-line arguments, loads the graph from the map file,
    and initializes the simulation pipeline.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    if len(sys.argv) != 2:
      print("Usage: python3 src/main.py <path_to_map_file>")
      return 1

    map_path = Path(sys.argv[1])
    

if __name__ == "__main__":
    main()
