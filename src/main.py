"""Entry point for the Fly-in drone routing simulation."""

import sys
from pathlib import Path

from src.parser.map_parser import MapParser, MapParserError
from src.pathfinder.pathfinder import Pathfinder, PathNotFound


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

    try:

        parser = MapParser(map_path)
        graph = parser.parse()

        print("=== Fly-in Simulation ===")
        print(f"Map loaded successfully: {map_path.name}")
        print(f"Zones: {len(graph.zones)} | Connections: {len(graph.connections)}")

        if graph.start_zone and graph.end_zone:
            print(
                f"Routing {graph.num_drones} drones from '{graph.start_zone.name}' "
                f"to '{graph.end_zone.name}'...\n")

        pathfinder = Pathfinder(graph)
        optimal_path = pathfinder.find_shortest_path()

        path_names = [zone.name for zone in optimal_path]
        print(f"Optimal path found: {' ->'.join(path_names)}")
        print(f"Total steps: {len(optimal_path)} zone\n")

        # 3. Simulation (To be implemented)
        # simulator = Simulator(graph, paths)
        # simulator.run()

        return 0

    except MapParserError as e:
        print(f"Error parsing map: {e}")
        return 1

    except PathNotFound as e:
        print(f"Routing Error {e}")
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
