"""Entry point for the Fly-in drone routing simulation."""

import sys
from pathlib import Path

from src.parser.map_parser import MapParser, MapParserError
from src.pathfinder.pathfinder import PathNotFound, Pathfinder
from src.simulator.simulator import Simulator


def main(argv: list[str] | None = None) -> int:
    """Run the simulation from a map file.

    Args:
        argv: Command-line arguments without the program name.

    Returns:
        Zero on success, one on failure.
    """
    arguments = sys.argv[1:] if argv is None else argv

    if len(arguments) != 1:
        print(
            "Usage: python3 src/main.py <path_to_map_file>",
            file=sys.stderr,
        )
        return 1

    try:
        graph = MapParser(Path(arguments[0])).parse()
        routes = Pathfinder(graph).plan_all_routes()
        Simulator(graph).run(routes)
        return 0

    except MapParserError as error:
        print(f"Error parsing map: {error}", file=sys.stderr)
        return 1

    except PathNotFound as error:
        print(f"Routing error: {error}", file=sys.stderr)
        return 1

    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
