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

        # 2. Pathfinding (To be implemented)
        # pathfinder = Pathfinder(graph)
        # paths = pathfinder.find_optimal_paths()

        # 3. Simulation (To be implemented)
        # simulator = Simulator(graph, paths)
        # simulator.run()

        return 0

    except MapParserError as e:
        print(f"Error parsing map: {e}")
        return 1

    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
