*This project has been created as part of the 42 curriculum by thiferre.*

## Description

Fly-in is an autonomous drone routing system that efficiently navigates multiple drones through a network of connected zones while minimizing simulation turns and handling complex movement constraints.

The system must:
- Parse map configuration files defining zones and connections
- Find optimal, collision-free paths for all drones using advanced space-time pathfinding
- Simulate turn-by-turn movement with strict capacity constraints
- Visualize results through colored terminal output and an animated 2D graphical interface
- Respect zone types (normal, restricted, priority, blocked) and their movement costs

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
make run MAP=maps/medium/03_circular_loop.txt
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

Remove temporary files, caches, and the virtual environment:

```bash
make clean         # Removes __pycache__, .mypy_cache, etc.
make fclean        # Runs clean and removes the virtual environment
make re            # Fully rebuilds the environment and runs the project
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
│     └── pathfinder.py       # Cooperative A* Pathfinding algorithm
└── visualizer/
      └── visualizer.py       # 2D animated map rendering & visualization
```

## Algorithm Overview

### Pathfinding Strategy

The pathfinding system was engineered to solve complex deadlocks and throughput limits using:

- Time-Space A Search*: Drones book nodes (zones) and edges (connections) in a 4D reservation table mapping time and space. This ensures mathematically guaranteed collision-free routes.
- Permutation Engine: To overcome extreme bottlenecks without exponential time complexity, the system uses Prioritized Planning, shuffling drone calculation order and picking the configuration that yields the absolute minimal makespan.
- Dijkstra's Heuristic: Used in reverse from the goal hub to map precise topological costs considering priority/restricted zones, feeding the A* algorithm with perfect heuristic data.

### Simulation Engine

The turn-by-turn simulation strictly respects:

- Zone occupancy constraints (max_drones parameter)
- Connection capacity constraints (max_link_capacity parameter)
- Multi-turn transit mechanics (e.g., restricted zones requiring a 2-turn transit over a connection)
- Cascading dynamic movements within the same turn

### Performance Benchmarks

Target performance based on optimal turns:
- Easy maps: <4 turns
- Medium maps: 6 to 10 turns
- Hard maps: 13 to 26 turns
- Challenger map: 43 turns (The Impossible Dream)

## Visualization

The system provides a rich visual experience built from scratch:

- Animated 2D Visualization: A custom-built engine using pure matplotlib.animation. Drones move smoothly between zones using linear coordinate interpolation, realistically illustrating time delays on multi-turn routes.

- Interactive Keyboard Controls:
     - [Space]: Play/Pause the simulation

     - [R]: Reset animation to Turn 0
      
     - [ESC]: Close visualizer
     
     - [+] or [=]: Increase simulation speed
     
     - [-]: Decrease simulation speed

- Terminal Colors: ANSI color codes applied to zone names during the simulation output to instantly identify zone types (e.g., restricted=red, start=green).

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
- [Cooperative A*](https://davidstarsilver.wordpress.com/wp-content/uploads/2025/05/aiide-05.pdf)
- [Multi-Agent Path Finding (MAPF)](https://jiaoyangli.me/research/mapf/)
- [Dijkstra's Algorithm](https://coddy.tech/visualize/graphs/dijkstras-algorithm)

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

### Why Time-Space Cooperative A*?
- Evolved from a basic BFS/Dijkstra approach to accurately prevent drone collisions in narrow corridors. Standard pathfinding ignores other agents, while Cooperative A* considers the future position of all previously routed drones.

### Why Object-Oriented Design?
- Clear separation of concerns (Parser, Simulator, PathFinder)
- Natural representation of domain concepts (Drone, Zone, Graph)
- Highly scalable and testable architecture

### Type Safety
- mypy ensures type correctness before runtime
- Reduces bugs and improves code maintainability
- Better IDE support and code documentation

## Performance Analysis

### Time Complexity
- Pathfinding: $O(D \times (V + E) \log V)$ where $V$=zones, $E$=connections, $D$=drones
- Simulation: $O(D \times T)$ where $T$=turns

### Space Complexity
- Graph storage: $O(V + E)$
- Path Reservation Tables: $O(T \times (V + E))$
- Overall Space: $O(T \times (V + E))$

## Future Enhancements
- Multi-path routing for continuous load distribution (infinite drone streams)
- Machine learning-based path optimization to replace random permutations
- Advanced real-time deadlock resolution during simulation phase
