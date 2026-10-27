*This project has been created as part of the 42 curriculum by thiferre.*

## Description

Fly-in is an autonomous drone routing system that efficiently navigates multiple drones through a network of connected zones while minimizing simulation turns and handling complex movement constraints.

The system must:
- Parse map configuration files defining zones and connections
- Find optimal paths for all drones using advanced pathfinding
- Simulate turn-by-turn movement with capacity constraints
- Visualize results through colored terminal output
- Respect zone types (normal, restricted, priority, blocked) and movement costs

## Instructions

### Setup & Virtual Environment

Create and activate the virtual environment:
```bash
make venv
source venv/bin/activate
```

### Installation

```bash
make install
```

### Running the Simulation with Default Map

```bash
make run
```

### Running a Specific Map

```bash
make run-map MAP=maps/medium/03_circular_loop.txt
```

### Debug Mode

```bash
make debug
```

### Code Quality

Run linters to ensure code quality:

```bash
make lint          # Run flake8 and mypy
make lint-strict   # Run mypy in strict mode
```

### Cleaning

Remove temporary files and caches:

```bash
make clean
```

## Project Structure

```
src/
├── main.py                   # Entry point
├── parser/
│     └── map_parser.py       # Parse map configuration files
├── model/
│     ├── zone.py             # Zone representation
│     ├── connection.py       # Connection between zones
│     ├── drone.py            # Drone representation
│     └── graph.py            # Complete network graph
├── simulator/
│     ├── simulator.py        # Simulation engine
├── pathfinder/
│     └── pathfinder.py       # Pathfinding algorithms
└── visualizer/
      └── visualizer.py       # Graphical map rendering & visualization
```

## Algorithm Overview

### Pathfinding Strategy

The pathfinding system uses:
- **Dijkstra**: For lowest-cost paths considering zone type costs
- **Constraint handling**: Respects zone capacity and connection limits

### Simulation Engine

Turn-by-turn simulation respects:
- Zone occupancy constraints (max_drones parameter)
- Connection capacity constraints (max_link_capacity parameter)
- Movement costs based on zone types
- Deadlock avoidance and intelligent waiting

### Performance Benchmarks

Target performance based on optimal turns:
- Easy maps: <4 turns
- Medium maps: 6 to 10 turns
- Hard maps: 13 to 26 turns
- Challenger map: 43 turns (The Impossible Dream)

## Visualization

The system provides:
- **Static 2D Map**: A graphical interface built with pure `matplotlib` that renders the network topology, node coordinates, and connections before the simulation begins.
- **Terminal Colors**: ANSI color codes applied to zone names during the simulation output to instantly identify zone types (e.g., restricted=red, start=green).
- **Turn-by-turn Display**: Shows concurrent drone movements precisely formatted per simulation turn.

## Example Input & Expected Output

### Input Map File (`map.txt`)
```text
nb_drones: 2
start_hub: start 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=normal]
hub: corridorA 4 3 [zone=normal]
connection: start-roof1
connection: start-corridorA
connection: roof1-goal
connection: corridorA-goal
```

```text
D1-roof1 D2-corridorA
D1-goal D2-goal
```

## Resources

### Graph Theory
- [Dijkstra's Algorithm](https://coddy.tech/visualize/graphs/dijkstras-algorithm)
- [Graph Theory Basics](https://www.khanacademy.org/computing/computer-science/algorithms/graph-representation/a/introduction-to-graphs)

### Python Best Practices
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Type Hints in Python](https://docs.python.org/3/library/typing.html)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [flake8 - Style Guide Enforcement](https://flake8.pycqa.org/)

### AI Usage in This Project

AI has been used to:
- Provide code structure recommendations
- Explain algorithm concepts (Dijkstra, constraint satisfaction)
- Review code quality and suggest improvements
- Generate docstring templates
- Optimize algorithm implementations

All AI-generated code was reviewed, tested, and modified to ensure it matches project requirements and personal understanding.

## Technical Choices

### Why Dijkstra's Algorithm?
- Evolved from a basic BFS approach to accurately evaluate movement costs based on zone types (restricted=2 turns, priority=1 turn).
- Ensures the drone fleet dynamically avoids traffic bottlenecks, prioritizing faster topological routes over simply minimizing the number of zone hops.

### Why Object-Oriented Design?
- Clear separation of concerns (Parser, Simulator, PathFinder)
- Easy to extend with new features (e.g., new zone types)
- Natural representation of domain concepts (Drone, Zone, Graph)

### Type Safety
- mypy ensures type correctness before runtime
- Reduces bugs and improves code maintainability
- Better IDE support and code documentation

## Performance Analysis

### Time Complexity
- Pathfinding (Dijkstra): O((V + E) log V) where V=zones, E=connections
- Simulation: O(D × T × V) where D=drones, T=turns
- Overall: O(((V + E) log V) + (D × T × V))

### Space Complexity
- Graph storage: O(V + E)
- Simulation state: O(D × V)
- Overall: O(V + E + D × V)

## Future Enhancements

- Multi-path routing for better load distribution
- Machine learning-based path optimization
- Real-time simulation speed control
- Advanced deadlock detection and resolution
