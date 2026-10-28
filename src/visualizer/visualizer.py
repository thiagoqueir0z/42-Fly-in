"""Network visualizer for the Fly-in simulation."""

import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import os

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
        """Initialize the visualizer with the parsed graph."""
        self.graph = graph

    def _get_zone_color(self, zone: Zone) -> str:
        """Determine the rendering color for a specific zone."""
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

    def _apply_safe_margins(self, ax) -> None:
        """Ensures the plot has a minimum physical size to prevent clipping offsets."""
        xs = [z.x for z in self.graph.zones.values()]
        ys = [z.y for z in self.graph.zones.values()]

        x_pad = max(0.5, (max(xs) - min(xs)) * 0.1)
        y_pad = max(0.5, (max(ys) - min(ys)) * 0.1)

        ax.set_xlim(min(xs) - x_pad, max(xs) + x_pad)
        ax.set_ylim(min(ys) - y_pad, max(ys) + y_pad)

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

            cap = getattr(zone, 'max_drones', None)
            if cap is not None and cap != float('inf') and not zone.is_start and not zone.is_end:
                ax.text(
                    zone.x, zone.y + 0.12,
                    f"Max: {int(cap)}",
                    fontsize=7,
                    color="black",
                    fontweight="bold",
                    ha="center",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.8),
                    zorder=3.5
                )

        self._apply_safe_margins(ax)
        ax.axis("off")
        plt.subplots_adjust(left=0.05, right=0.95, top=0.95, bottom=0.05)
        plt.show()

    def animate_simulation(self, simulation_steps: list[dict]) -> None:
        """Animate drone movement smoothly with PNG icons, capacities, and keyboard controls."""
        total_turns = len(simulation_steps) - 1
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.set_title(f"Fly-in Simulation - Turn 0/{total_turns}", fontsize=16, fontweight="bold")

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

            capacity = getattr(connection, 'max_link_capacity', None)
            if capacity is not None and capacity != float('inf'):
                mid_x = (connection.zone_a.x + connection.zone_b.x) / 2
                mid_y = (connection.zone_a.y + connection.zone_b.y) / 2
                ax.text(
                    mid_x, mid_y + 0.004,
                    f"[{int(capacity)}]",
                    fontsize=8,
                    color="darkred",
                    fontweight="bold",
                    ha="center",
                    va="center",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.8),
                    zorder=1.5
                )

        for zone in self.graph.zones.values():
            color = self._get_zone_color(zone)
            ax.scatter(
                zone.x, zone.y,
                s=1200,
                c=color,
                edgecolor="black",
                linewidth=1.5,
                zorder=2
            )

            cap = getattr(zone, 'max_drones', None)
            if cap is not None and cap != float('inf') and not zone.is_start and not zone.is_end:
                ax.text(
                    zone.x, zone.y + 0.12,
                    f"Max: {int(cap)}",
                    fontsize=7,
                    color="black",
                    fontweight="bold",
                    ha="center",
                    va="bottom",
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="black", lw=0.5, alpha=0.8),
                    zorder=3.5
                )

        drone_artists = {}
        drone_labels = {}
        drone_img_path = "assets/drone.png"

        has_png = os.path.exists(drone_img_path)
        if has_png:
            arr_img = plt.imread(drone_img_path)

        for i in range(1, self.graph.num_drones + 1):
            drone_id_str = f"D{i}"
            if has_png:
                imagebox = OffsetImage(arr_img, zoom=0.05)
                ab = AnnotationBbox(imagebox, (0, 0), frameon=False, zorder=4)
                ax.add_artist(ab)
                drone_artists[drone_id_str] = ab

                badge = ax.text(
                    0, 0, str(i),
                    fontsize=8, fontweight="bold", color="white",
                    ha="center", va="center", zorder=4.5,
                    bbox=dict(boxstyle="circle,pad=0.15", fc="#E74C3C", ec="white", lw=0.8)
                )
                drone_labels[drone_id_str] = badge
            else:
                t = ax.text(
                    0, 0, drone_id_str,
                    fontsize=9, fontweight="bold", color="white",
                    bbox=dict(boxstyle="circle,pad=0.3", fc="darkblue", ec="black", lw=1),
                    ha="center", va="center", zorder=4
                )
                drone_artists[drone_id_str] = t

        self._apply_safe_margins(ax)
        ax.axis("off")

        fig.text(
            0.5, 0.05,
            "[Space]: Play/Pause  |  [R]: Reset  |  [ESC]: Close |  [+]: Faster  |  [-]: Slower",
            ha="center", va="bottom", fontsize=10, fontweight="bold",
            color="black", bbox=dict(boxstyle="round,pad=0.3", fc="lightgray", ec="gray", lw=1)
        )

        plt.subplots_adjust(bottom=0.1)

        special_coords = set()
        for z in self.graph.zones.values():
            if z.is_start or z.is_end:
                special_coords.add((round(z.x, 4), round(z.y, 4)))

        SUB_STEPS = 10
        smooth_frames = []

        def get_coords(z_name: str):
            if z_name in self.graph.zones:
                z = self.graph.zones[z_name]
                return z.x, z.y
            elif "-" in z_name:
                z1, z2 = z_name.split("-")
                if z1 in self.graph.zones and z2 in self.graph.zones:
                    zx1, zy1 = self.graph.zones[z1].x, self.graph.zones[z1].y
                    zx2, zy2 = self.graph.zones[z2].x, self.graph.zones[z2].y
                    return (zx1 + zx2) / 2, (zy1 + zy2) / 2
            return None

        for i in range(len(simulation_steps)):
            curr_state = simulation_steps[i]
            prev_state = simulation_steps[i - 1] if i > 0 else curr_state

            for step in range(SUB_STEPS):
                alpha = min(1.0, (step / (SUB_STEPS * 0.6)))
                raw_positions = {}

                for drone_id, curr_zone_name in curr_state.items():
                    prev_zone_name = prev_state.get(drone_id, curr_zone_name)

                    c_coords = get_coords(curr_zone_name)
                    p_coords = get_coords(prev_zone_name)

                    if c_coords and p_coords:
                        x = p_coords[0] + (c_coords[0] - p_coords[0]) * alpha
                        y = p_coords[1] + (c_coords[1] - p_coords[1]) * alpha
                        raw_positions[drone_id] = (round(x, 4), round(y, 4))

                interpolated_state = {}
                coord_counts = {}

                for pos in raw_positions.values():
                    coord_counts[pos] = coord_counts.get(pos, 0) + 1

                coord_seen = {}
                for drone_id, (x, y) in raw_positions.items():
                    total = coord_counts[(x, y)]
                    if total > 1 and (x, y) not in special_coords:
                        idx = coord_seen.get((x, y), 0)
                        coord_seen[(x, y)] = idx + 1

                        offset_x = (idx - (total - 1) / 2) * 0.04
                        offset_y = (idx - (total - 1) / 2) * 0.04
                        interpolated_state[drone_id] = (x + offset_x, y + offset_y)
                    else:
                        interpolated_state[drone_id] = (x, y)

                smooth_frames.append((i, interpolated_state))

        max_frames = len(smooth_frames)
        current_frame = [0]
        is_paused = [True]

        def update(frame_idx: int):
            current_frame[0] = frame_idx
            turn_num, drone_coords = smooth_frames[frame_idx]

            for artist in drone_artists.values():
                artist.set_visible(False)
            for badge in drone_labels.values():
                badge.set_visible(False)

            for drone_id, (x, y) in drone_coords.items():
                if drone_id in drone_artists:
                    artist = drone_artists[drone_id]
                    if has_png:
                        artist.xybox = (x, y)
                        artist.xy = (x, y)
                        artist.set_visible(True)
                        if drone_id in drone_labels:
                            badge = drone_labels[drone_id]
                            badge.set_position((x + 0.06, y - 0.06))
                            badge.set_visible(True)
                    else:
                        artist.set_position((x, y))
                        artist.set_visible(True)

            ax.set_title(
                f"Fly-in Simulation - Turn {turn_num}/{total_turns}", fontsize=16, fontweight="bold"
            )

            if frame_idx == max_frames - 1:
                anim.pause()
                is_paused[0] = True

            return list(drone_artists.values()) + list(drone_labels.values())

        anim = FuncAnimation(
            fig,
            update,
            frames=max_frames,
            interval=100,
            blit=False,
            repeat=True
        )

        anim.pause()
        update(0)
        fig.canvas.draw_idle()

        def on_key(event):
            if event.key == ' ':
                if is_paused[0]:
                    if current_frame[0] == max_frames - 1:
                        anim.frame_seq = anim.new_frame_seq()
                        update(0)
                    anim.resume()
                    is_paused[0] = False
                else:
                    anim.pause()
                    is_paused[0] = True
            elif event.key in ['r', 'R']:
                anim.pause()
                anim.frame_seq = anim.new_frame_seq()
                update(0)
                fig.canvas.draw_idle()
                is_paused[0] = True
            elif event.key == 'escape':
                plt.close(fig)
            elif event.key in ['+', '=']:
                if anim.event_source:
                    anim.event_source.interval = max(1, anim.event_source.interval / 3)
            elif event.key == '-':
                if anim.event_source:
                    anim.event_source.interval = min(2000, anim.event_source.interval * 2)

        fig.canvas.mpl_connect('key_press_event', on_key)
        plt.show()
