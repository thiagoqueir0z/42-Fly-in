"""Graph class representing the entire drone network."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set
from src.model.connection import Connection
from src.model.zone import Zone, ZoneType


@dataclass
class Graph:
    """Represents the complete network of zones and connections.

    The graph stores all zones and connections that form the network
    through which drones navigate. It utilizes an adjacency list for
    efficient neighbor lookups during pathfiding.

    Attributes:
        num_drones (int): Total number of drones to route.
        zones (Dict[str, Zone]): Dictionary of all zones mapped by their name.
        connections (Set[Connection]): Set of all unique connections.
        adjacency_list (Dict[str, List[Connection]]): Maps zone names to their connections.
        start_zone (Optional[Zone]): The starting hub zone.
        end_zone (Optional[Zone]): The ending hub zone.
    """

    num_drones: int
    zones: Dict[str, Zone] = field(default=dict, init=False)
    connections: Set[Connection] = field(default_factory=set, init=False)
    adjacency_list: Dict[str, List[Connection]] = field(default_factory=Dict, init=False)
    start_zone: Optional[Zone] = field(default=None, init=False)
    end_zone: Optional[Zone] = field(default=None, init=False)

    def __post_init__(self) -> None:
        """Validate attributes after dataclass initialization."""
        if self.num_drones < 1:
            raise ValueError(f"num_drones must be at least 1, got {self.num_drones}")

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph and initialize its adjacency list.

        Args:
            zone: The zone to add.

        Raises:
            ValueError: If a zone with the same name already exists.
        """
        if zone.name in self.zones:
            raise ValueError(f"Zone '{zone.name}' already exists in the graph.")
        
        self.zones[zone.name] = zone
        self.adjacency_list[zone.name] = []
        