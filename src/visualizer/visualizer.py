"""Network visualizer for the Fly-in simulation."""

import matplotlib.pyplot as plt

from src.model.graph import Graph
from src.model.zone import Zone, ZoneType


class NetworkVisualizer:
    """Renders a 2D visualization of the drone network without graph libraries.

    Uses pure matplotlib to plot coordinates and draw lines for connections,
    respecting the strict rule against using graph logic libraries.

    Attributes:
        graph (Graph): The Fly-in network graph to be rendered.
    """

    def __init__(self, graph: Graph) -> None:
        """Initialize the visualizer with the parsed graph.

        Args:
            graph: The network topology to draw.
        """
        self.graph = graph

    def _get_zone_color(self, zone: Zone) -> str:
        """Determine the rendering color for a specific zone.

        Prioritizes the color defined in the map metadata. If none exists,
        defaults to standard colors based on the zone type.

        Args:
            zone: The Zone instance to evaluate.

        Returns:
            A string representing a matplotlib-compatible color.
        """
        if zone.color:
            return zone.color

        if zone.is_start:
            return "green"
        if zone.is_end:
            return "yellow"
        if zone.zone_type == ZoneType.BLOCKED:
            return "gray"
        if zone.zone_type == ZoneType.RESTRICTED:
            return "red"
        if zone.zone_type == ZoneType.PRIORITY:
            return "orange"

        return "lightblue"

    def show_static_map(self) -> None:
        """Render and display the static network topology."""
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_title("Fly-in Drone Network Topology", fontsize=16, fontweight="bold")

        for connection in self.graph.connections:
            x_coords = [connection.zone_a.x, connection.zone_b.x]
            y_coords = [connection.zone_a.y, connection.zone_b.y]
            ax.plot(
                x_coords, y_coords,
                color="black",
                linewidth=2,
                alpha=0.5,
                zorder=1
            )

        for zone in self.graph.zones.values():
            color = self._get_zone_color(zone)

            ax.scatter(
               zone.x, zone.y,
               s=900,
               c=color,
               edgecolor="black",
               linewidth=1.5,
               zorder=2
            )

            ax.text(
                zone.x, zone.y,
                zone.name,
                fontsize=9,
                fontweight="bold",
                ha="center",
                va="center",
                zorder=3
            )

        ax.axis("off")
        plt.tight_layout()
        plt.show()
