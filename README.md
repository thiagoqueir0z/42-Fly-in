*This project has been created as part of the 42 curriculum by thiagoqueir0z.*

## Description

Fly-in is an autonomous drone routing system that efficiently navigates multiple drones through a network of connected zones while minimizing simulation turns and handling complex movement constraints.

The system must:
- Parse map configuration files defining zones and connections
- Find optimal paths for all drones using advanced pathfinding
- Simulate turn-by-turn movement with capacity constraints
- Visualize results through colored terminal output
- Respect zone types (normal, restricted, priority, blocked) and movement costs

## Instructions

### Installation

```bash
make install
```

### Running the Simulation

```bash
make run
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
├── main.py                 # Entry point
├── parser/
│   └── map_parser.py       # Parse map configuration files
├── model/
│   ├── zone.py             # Zone representation
│   ├── connection.py       # Connection between zones
│   ├── drone.py            # Drone representation
│   └── graph.py            # Complete network graph
├── simulator/
│   ├── simulator.py        # Simulation engine
│   └── movement_validator.py  # Validate drone movements
├── pathfinder/
│   └── pathfinder.py       # Pathfinding algorithms
└── visualization/
    └── visualizer.py       # Terminal visualization
```

## Algorithm Overview

### Pathfinding Strategy

The pathfinding system uses a combination of algorithms:
- **BFS**: For shortest path in terms of zone count
- **Dijkstra**: For lowest-cost paths considering zone type costs
- **Constraint handling**: Respects zone capacity and connection limits

### Simulation Engine

Turn-by-turn simulation respects:
- Zone occupancy constraints (max_drones parameter)
- Connection capacity constraints (max_link_capacity parameter)
- Movement costs based on zone types
- Deadlock avoidance and intelligent waiting

### Performance Benchmarks

Target performance:
- Easy maps: < 10 turns
- Medium maps: 10-30 turns
- Hard maps: < 60 turns
- Challenger map: < 45 turns (optional)

## Visualization

The system provides:
- **Terminal colors**: ANSI color codes for different zone types
- **Turn-by-turn display**: Shows each drone movement
- **Statistics**: Total turns, drones per turn, path efficiency

## Resources

### Graph Theory
- [BFS (Breadth-First Search)](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Dijkstra's Algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)
- [Graph Theory Basics](https://www.khanacademy.org/computing/computer-science/algorithms/graph-representation/a/introduction-to-graphs)

### Python Best Practices
- [PEP 257 - Docstring Conventions](https://www.python.org/dev/peps/pep-0257/)
- [Type Hints in Python](https://docs.python.org/3/library/typing.html)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [flake8 - Style Guide Enforcement](https://flake8.pycqa.org/)

### AI Usage in This Project

AI has been used to:
- Provide code structure recommendations
- Explain algorithm concepts (BFS, Dijkstra, constraint satisfaction)
- Review code quality and suggest improvements
- Generate docstring templates
- Optimize algorithm implementations

All AI-generated code was reviewed, tested, and modified to ensure it matches project requirements and personal understanding.

## Technical Choices

### Why BFS + Dijkstra?
- BFS provides fast shortest paths when cost doesn't matter
- Dijkstra handles zone type costs (restricted=2 turns, etc.)
- Combination allows flexible routing strategies

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
- Pathfinding (BFS): O(V + E) where V=zones, E=connections
- Simulation: O(D × T × V) where D=drones, T=turns
- Overall: O(D × T × (V + E))

### Space Complexity
- Graph storage: O(V + E)
- Simulation state: O(D × V)
- Overall: O(V + E + D × V)

## Future Enhancements

- Multi-path routing for better load distribution
- Machine learning-based path optimization
- Graphical UI with visualization
- Real-time simulation speed control
- Advanced deadlock detection and resolution
