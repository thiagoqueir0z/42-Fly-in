"""Entry point for the Fly-in drone routing simulation."""

import sys
from pathlib import Path

from src.parser.map_parser import MapParser, MapParserError
from src.pathfinder.pathfinder import Pathfinder, PathNotFound
from src.simulator.simulator import Simulator
from src.visualizer.visualizer import NetworkVisualizer


def main() -> int:
    """Run the main simulation program.

    Parses command-line arguments, loads the graph from the map file,
    and initializes the simulation and visualization pipeline.

    Returns:
        int: Exit code (0 for success, 1 for error).
    """
    if len(sys.argv) != 2:
        print("Usage: python3 src/main.py <path_to_map_file>")
        return 1

    map_path = Path(sys.argv[1])

    try:
        parser = MapParser(map_path)
        graph = parser.parse()

        print("\n=============== Fly-in Simulation ===============\n")
        print(f"Map loaded successfully: {map_path.name}\n")

        pathfinder = Pathfinder(graph)
        all_routes = pathfinder.plan_all_routes()

        simulator = Simulator(graph)
        simulator.run(all_routes)

        visualizer = NetworkVisualizer(graph)
        visualizer.animate_simulation(simulator.history)

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
