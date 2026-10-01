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


