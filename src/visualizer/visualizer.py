"""Matplotlib visualization for the Fly-in simulation."""

from pathlib import Path
from typing import Any

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnnotationBbox, OffsetImage

from src.model.graph import Graph
from src.model.zone import Zone, ZoneType

SimulationStep = dict[str, str]
Position = tuple[float, float]


class NetworkVisualizer:
    """Render the network and the existing simulation history."""

    def __init__(self, graph: Graph) -> None:
        """Initialize the visualizer with a graph."""
        self.graph = graph
        self.animation: FuncAnimation | None = None

    def _get_zone_color(self, zone: Zone) -> str:
        """Return the Matplotlib color for a zone."""
        if zone.color and mcolors.is_color_like(zone.color):
            return zone.color

        if zone.is_start:
            return "green"
        if zone.is_end:
            return "lightgreen"
        if zone.zone_type == ZoneType.BLOCKED:
            return "gray"
        if zone.zone_type == ZoneType.RESTRICTED:
            return "red"
        if zone.zone_type == ZoneType.PRIORITY:
            return "orange"

        return "blue"

    def _validate_graph(self) -> None:
        """Ensure the graph contains data that can be displayed."""
        if not self.graph.zones:
            raise ValueError("Cannot visualize a graph without zones.")

    @staticmethod
    def _asset_path() -> Path:
        """Return the path to the optional drone image."""
        return Path(__file__).resolve().parents[2] / "assets" / "drone.png"

    def _apply_safe_margins(self, ax: Any) -> None:
        """Apply margins around all zone coordinates."""
        self._validate_graph()
        xs = [zone.x for zone in self.graph.zones.values()]
        ys = [zone.y for zone in self.graph.zones.values()]

        x_padding = max(0.5, (max(xs) - min(xs)) * 0.1)
        y_padding = max(0.5, (max(ys) - min(ys)) * 0.1)
        ax.set_xlim(min(xs) - x_padding, max(xs) + x_padding)
        ax.set_ylim(min(ys) - y_padding, max(ys) + y_padding)

    def _draw_connections(self, ax: Any, show_capacity: bool = False) -> None:
        """Draw graph connections and, optionally, their capacities."""
        for connection in self.graph.connections:
            x_values = [connection.zone_a.x, connection.zone_b.x]
            y_values = [connection.zone_a.y, connection.zone_b.y]
            ax.plot(
                x_values,
                y_values,
                color="black",
                linewidth=2,
                alpha=0.5,
                zorder=1,
            )

            if show_capacity:
                middle_x = sum(x_values) / 2
                middle_y = sum(y_values) / 2
                self._draw_label(
                    ax,
                    middle_x,
                    middle_y + 0.004,
                    f"[{connection.max_link_capacity}]",
                    color="darkred",
                    fontsize=8,
                    zorder=1.5,
                )

    def _draw_zones(self, ax: Any, point_size: int) -> None:
        """Draw all zones and their capacities."""
        for zone in self.graph.zones.values():
            ax.scatter(
                zone.x,
                zone.y,
                s=point_size,
                c=self._get_zone_color(zone),
                edgecolor="black",
                linewidth=1.5,
                zorder=2,
            )

            if not zone.is_start and not zone.is_end:
                self._draw_label(
                    ax,
                    zone.x,
                    zone.y + 0.12,
                    f"Max: {zone.max_drones}",
                    color="black",
                    fontsize=7,
                    zorder=3.5,
                )

    @staticmethod
    def _draw_label(
        ax: Any,
        x: float,
        y: float,
        text: str,
        color: str,
        fontsize: int,
        zorder: float,
    ) -> None:
        """Draw a readable label with a white background."""
        ax.text(
            x,
            y,
            text,
            fontsize=fontsize,
            color=color,
            fontweight="bold",
            ha="center",
            va="center",
            bbox={
                "boxstyle": "round,pad=0.2",
                "fc": "white",
                "ec": "black",
                "lw": 0.5,
                "alpha": 0.8,
            },
            zorder=zorder,
        )

    def _prepare_axes(self, title: str, show_capacity: bool = False) -> Any:
        """Create and configure axes for a visualization."""
        self._validate_graph()
        _, ax = plt.subplots(figsize=(10, 8))
        ax.set_title(title, fontsize=16, fontweight="bold")
        self._draw_connections(ax, show_capacity)
        self._draw_zones(ax, 1200 if show_capacity else 900)
        self._apply_safe_margins(ax)
        ax.axis("off")
        return ax

    def show_static_map(self) -> None:
        """Display the static network topology."""
        figure = plt.figure(figsize=(10, 8))
        try:
            ax = figure.add_subplot(1, 1, 1)
            self._validate_graph()
            ax.set_title(
                "Fly-in Drone Network Topology",
                fontsize=16,
                fontweight="bold",
            )
            self._draw_connections(ax)
            self._draw_zones(ax, 900)
            self._apply_safe_margins(ax)
            ax.axis("off")
            figure.subplots_adjust(
                left=0.05,
                right=0.95,
                top=0.95,
                bottom=0.05,
            )
            plt.show()
        finally:
            plt.close(figure)

    def _create_drone_artists(
        self,
        ax: Any,
    ) -> tuple[dict[str, Any], dict[str, Any], bool]:
        """Create artists for every drone, using an image when available."""
        artists: dict[str, Any] = {}
        labels: dict[str, Any] = {}
        image_path = self._asset_path()
        has_image = image_path.is_file()
        image = plt.imread(image_path) if has_image else None

        for drone_id in range(1, self.graph.num_drones + 1):
            name = f"D{drone_id}"
            if has_image and image is not None:
                image_box = OffsetImage(image, zoom=0.05)
                artist = AnnotationBbox(
                    image_box,
                    (0, 0),
                    frameon=False,
                    zorder=4,
                )
                ax.add_artist(artist)
                artists[name] = artist
                labels[name] = ax.text(
                    0,
                    0,
                    str(drone_id),
                    fontsize=8,
                    fontweight="bold",
                    color="white",
                    ha="center",
                    va="center",
                    zorder=4.5,
                    bbox={
                        "boxstyle": "circle,pad=0.15",
                        "fc": "#E74C3C",
                        "ec": "white",
                        "lw": 0.8,
                    },
                )
            else:
                artists[name] = ax.text(
                    0,
                    0,
                    name,
                    fontsize=9,
                    fontweight="bold",
                    color="white",
                    bbox={
                        "boxstyle": "circle,pad=0.3",
                        "fc": "darkblue",
                        "ec": "black",
                        "lw": 1,
                    },
                    ha="center",
                    va="center",
                    zorder=4,
                )

        return artists, labels, has_image

    def _build_frames(
        self,
        simulation_steps: list[SimulationStep],
    ) -> list[tuple[int, dict[str, Position]]]:
        """Build interpolated frames from the existing zone history."""
        frames: list[tuple[int, dict[str, Position]]] = []
        special_positions = {
            (zone.x, zone.y)
            for zone in self.graph.zones.values()
            if zone.is_start or zone.is_end
        }
        sub_steps = 10

        for index, current_state in enumerate(simulation_steps):
            previous_state = (
                simulation_steps[index - 1] if index > 0 else current_state
            )
            for step in range(sub_steps):
                alpha = min(1.0, step / (sub_steps * 0.6))
                positions = self._interpolate_positions(
                    previous_state,
                    current_state,
                    alpha,
                )
                frames.append(
                    (index, self._separate_overlapping_positions(
                        positions,
                        special_positions,
                    ))
                )

        return frames

    def _interpolate_positions(
        self,
        previous: SimulationStep,
        current: SimulationStep,
        alpha: float,
    ) -> dict[str, Position]:
        """Interpolate drone positions between two simulation states."""
        positions: dict[str, Position] = {}
        for drone_id, current_name in current.items():
            previous_name = previous.get(drone_id, current_name)
            if current_name not in self.graph.zones:
                continue
            if previous_name not in self.graph.zones:
                continue

            current_zone = self.graph.zones[current_name]
            previous_zone = self.graph.zones[previous_name]
            x = previous_zone.x + (current_zone.x - previous_zone.x) * alpha
            y = previous_zone.y + (current_zone.y - previous_zone.y) * alpha
            positions[drone_id] = (round(x, 4), round(y, 4))

        return positions

    @staticmethod
    def _separate_overlapping_positions(
        positions: dict[str, Position],
        special_positions: set[Position],
    ) -> dict[str, Position]:
        """Offset overlapping drones except at start and end zones."""
        counts: dict[Position, int] = {}
        for position in positions.values():
            counts[position] = counts.get(position, 0) + 1

        seen: dict[Position, int] = {}
        separated: dict[str, Position] = {}
        for drone_id, (x, y) in positions.items():
            position = (x, y)
            total = counts[position]
            if total <= 1 or position in special_positions:
                separated[drone_id] = position
                continue

            index = seen.get(position, 0)
            seen[position] = index + 1
            offset = (index - (total - 1) / 2) * 0.04
            separated[drone_id] = (x + offset, y + offset)

        return separated

    def animate_simulation(
        self,
        simulation_steps: list[SimulationStep],
    ) -> None:
        """Animate the simulation history with keyboard controls."""
        if not simulation_steps:
            raise ValueError("Simulation history cannot be empty.")

        total_turns = len(simulation_steps) - 1
        figure, ax = plt.subplots(figsize=(10, 8))
        ax.set_title(
            f"Fly-in Simulation - Turn 0/{total_turns}",
            fontsize=16,
            fontweight="bold",
        )
        self._draw_connections(ax, show_capacity=True)
        self._draw_zones(ax, 1200)
        artists, labels, has_image = self._create_drone_artists(ax)
        self._apply_safe_margins(ax)
        ax.axis("off")
        figure.text(
            0.5,
            0.02,
            "[Space]: Play/Pause  |  [R]: Reset  |  [ESC]: Close",
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
            color="black",
            bbox={
                "boxstyle": "round,pad=0.4",
                "fc": "lightgray",
                "ec": "gray",
                "lw": 1,
            },
        )
        figure.subplots_adjust(bottom=0.1)

        frames = self._build_frames(simulation_steps)
        if not frames:
            plt.close(figure)
            raise ValueError("Simulation history produced no animation frames.")

        current_frame = 0
        paused = True

        def update(frame_index: int) -> list[Any]:
            """Update artists for one animation frame."""
            nonlocal current_frame, paused
            current_frame = frame_index
            turn_number, positions = frames[frame_index]

            for artist in [*artists.values(), *labels.values()]:
                artist.set_visible(False)

            for drone_id, (x, y) in positions.items():
                artist = artists.get(drone_id)
                if artist is None:
                    continue

                if has_image:
                    artist.xybox = (x, y)
                    artist.xy = (x, y)
                else:
                    artist.set_position((x, y))
                artist.set_visible(True)

                label = labels.get(drone_id)
                if label is not None:
                    label.set_position((x + 0.04, y + 0.04))
                    label.set_visible(True)

            ax.set_title(
                f"Fly-in Simulation - Turn {turn_number}/{total_turns}",
                fontsize=16,
                fontweight="bold",
            )
            if frame_index == len(frames) - 1:
                self.animation.pause() if self.animation else None
                paused = True

            return [*artists.values(), *labels.values()]

        self.animation = FuncAnimation(
            figure,
            update,
            frames=len(frames),
            interval=100,
            blit=False,
            repeat=True,
        )
        self.animation.pause()
        update(0)
        figure.canvas.draw_idle()

        def on_key(event: Any) -> None:
            """Handle playback keyboard shortcuts."""
            nonlocal paused
            if event.key == " ":
                if paused:
                    if current_frame == len(frames) - 1:
                        self.animation.frame_seq = self.animation.new_frame_seq()
                        update(0)
                    self.animation.resume()
                    paused = False
                else:
                    self.animation.pause()
                    paused = True
            elif event.key in {"r", "R"}:
                self.animation.pause()
                self.animation.frame_seq = self.animation.new_frame_seq()
                update(0)
                figure.canvas.draw_idle()
                paused = True
            elif event.key == "escape":
                plt.close(figure)

        figure.canvas.mpl_connect("key_press_event", on_key)
        plt.show()
        plt.close(figure)
