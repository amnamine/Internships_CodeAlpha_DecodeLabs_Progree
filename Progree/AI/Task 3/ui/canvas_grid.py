"""
High-Performance Interactive Tkinter Canvas Grid.
Renders grid cells, terrain, walls, real-time search animation, final path glow, and agent walking.
"""

import tkinter as tk
from typing import Tuple, List, Set, Optional, Callable, Dict, Any
from environment.grid import Grid, CellType
from ui.theme import Theme

class CanvasGrid(tk.Canvas):
    def __init__(self, master, grid: Grid, on_grid_modified: Optional[Callable[[], None]] = None, **kwargs):
        super().__init__(
            master,
            bg=Theme.BG_DARK,
            highlightthickness=0,
            bd=0,
            **kwargs
        )
        self.grid_model = grid
        self.on_grid_modified = on_grid_modified

        # Interaction state
        self.current_brush: CellType = CellType.WALL
        self.is_mouse_down = False
        self.dragging_start = False
        self.dragging_goal = False

        # Visual overlays state
        self.open_nodes: Set[Tuple[int, int]] = set()
        self.closed_nodes: Set[Tuple[int, int]] = set()
        self.path_nodes: List[Tuple[int, int]] = []
        self.current_inspect_node: Optional[Tuple[int, int]] = None
        self.agent_position: Optional[Tuple[int, int]] = None

        # Cell size caching
        self.cell_size = 20
        self.offset_x = 0
        self.offset_y = 0

        # Bind events
        self.bind("<Configure>", self._on_resize)
        self.bind("<Button-1>", self._on_left_down)
        self.bind("<B1-Motion>", self._on_left_drag)
        self.bind("<ButtonRelease-1>", self._on_mouse_up)
        self.bind("<Button-3>", self._on_right_down)
        self.bind("<B3-Motion>", self._on_right_drag)
        self.bind("<ButtonRelease-3>", self._on_mouse_up)

    def set_brush(self, brush_type: CellType):
        self.current_brush = brush_type

    def _on_resize(self, event):
        self.redraw_full()

    def calculate_cell_metrics(self):
        w = max(100, self.winfo_width())
        h = max(100, self.winfo_height())
        padding = 16

        avail_w = w - 2 * padding
        avail_h = h - 2 * padding

        cell_w = avail_w / max(1, self.grid_model.cols)
        cell_h = avail_h / max(1, self.grid_model.rows)
        self.cell_size = max(6.0, min(cell_w, cell_h))

        total_grid_w = self.cell_size * self.grid_model.cols
        total_grid_h = self.cell_size * self.grid_model.rows

        self.offset_x = max(padding, (w - total_grid_w) / 2)
        self.offset_y = max(padding, (h - total_grid_h) / 2)

    def get_cell_coords(self, r: int, c: int) -> Tuple[float, float, float, float]:
        x1 = self.offset_x + c * self.cell_size
        y1 = self.offset_y + r * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        return x1, y1, x2, y2

    def get_grid_pos(self, x: float, y: float) -> Optional[Tuple[int, int]]:
        if self.cell_size <= 0:
            return None
        c = int((x - self.offset_x) // self.cell_size)
        r = int((y - self.offset_y) // self.cell_size)
        if 0 <= r < self.grid_model.rows and 0 <= c < self.grid_model.cols:
            return (r, c)
        return None

    def _on_left_down(self, event):
        self.is_mouse_down = True
        pos = self.get_grid_pos(event.x, event.y)
        if not pos:
            return

        if pos == self.grid_model.start:
            self.dragging_start = True
        elif pos == self.grid_model.goal:
            self.dragging_goal = True
        else:
            self._apply_brush(pos[0], pos[1], self.current_brush)

    def _on_left_drag(self, event):
        if not self.is_mouse_down:
            return
        pos = self.get_grid_pos(event.x, event.y)
        if not pos:
            return

        if self.dragging_start:
            if pos != self.grid_model.goal and pos != self.grid_model.start:
                self.grid_model.set_start(pos[0], pos[1])
                self.redraw_full()
                if self.on_grid_modified:
                    self.on_grid_modified()
        elif self.dragging_goal:
            if pos != self.grid_model.start and pos != self.grid_model.goal:
                self.grid_model.set_goal(pos[0], pos[1])
                self.redraw_full()
                if self.on_grid_modified:
                    self.on_grid_modified()
        else:
            self._apply_brush(pos[0], pos[1], self.current_brush)

    def _on_right_down(self, event):
        self.is_mouse_down = True
        pos = self.get_grid_pos(event.x, event.y)
        if pos:
            self._apply_brush(pos[0], pos[1], CellType.EMPTY)

    def _on_right_drag(self, event):
        if not self.is_mouse_down:
            return
        pos = self.get_grid_pos(event.x, event.y)
        if pos:
            self._apply_brush(pos[0], pos[1], CellType.EMPTY)

    def _on_mouse_up(self, event):
        self.is_mouse_down = False
        self.dragging_start = False
        self.dragging_goal = False

    def _apply_brush(self, r: int, c: int, brush_type: CellType):
        if (r, c) == self.grid_model.start or (r, c) == self.grid_model.goal:
            return
        changed = self.grid_model.set_cell(r, c, brush_type)
        if changed:
            self.draw_cell(r, c)
            if self.on_grid_modified:
                self.on_grid_modified()

    def reset_visual_search(self):
        """Clears path, open, closed, and agent overlays without touching walls or terrain."""
        self.open_nodes.clear()
        self.closed_nodes.clear()
        self.path_nodes.clear()
        self.current_inspect_node = None
        self.agent_position = None
        self.redraw_full()

    def set_search_state(
        self,
        current: Optional[Tuple[int, int]] = None,
        open_set: Optional[List[Tuple[int, int]]] = None,
        closed_set: Optional[List[Tuple[int, int]]] = None,
        path: Optional[List[Tuple[int, int]]] = None,
        agent_pos: Optional[Tuple[int, int]] = None
    ):
        """Updates animation state incrementally."""
        old_current = self.current_inspect_node
        self.current_inspect_node = current

        new_open = set(open_set) if open_set is not None else self.open_nodes
        new_closed = set(closed_set) if closed_set is not None else self.closed_nodes

        nodes_to_update = set()
        if old_current:
            nodes_to_update.add(old_current)
        if current:
            nodes_to_update.add(current)

        # Difference updates
        nodes_to_update.update(new_open.symmetric_difference(self.open_nodes))
        nodes_to_update.update(new_closed.symmetric_difference(self.closed_nodes))

        self.open_nodes = new_open
        self.closed_nodes = new_closed

        if path is not None:
            self.path_nodes = path
            nodes_to_update.update(path)

        if agent_pos is not None or self.agent_position is not None:
            if self.agent_position:
                nodes_to_update.add(self.agent_position)
            self.agent_position = agent_pos
            if agent_pos:
                nodes_to_update.add(agent_pos)

        for r, c in nodes_to_update:
            if self.grid_model.in_bounds(r, c):
                self.draw_cell(r, c)

        # Draw path connection overlay if path exists
        if self.path_nodes:
            self._draw_path_overlay()

    def draw_cell(self, r: int, c: int):
        tag = f"cell_{r}_{c}"
        self.delete(tag)

        x1, y1, x2, y2 = self.get_cell_coords(r, c)
        inset = 1.0 if self.cell_size > 14 else 0.5
        rx1, ry1, rx2, ry2 = x1 + inset, y1 + inset, x2 - inset, y2 - inset

        cell_type = self.grid_model.get_cell(r, c)
        pos = (r, c)

        # Determine cell fill color
        if pos == self.grid_model.start:
            fill_color = Theme.NODE_START
            outline = "#34d399"
        elif pos == self.grid_model.goal:
            fill_color = Theme.NODE_GOAL
            outline = "#fb7185"
        elif pos == self.current_inspect_node:
            fill_color = Theme.NODE_CURRENT
            outline = "#fde047"
        elif pos in self.path_nodes:
            fill_color = Theme.NODE_PATH
            outline = Theme.NODE_PATH_GLOW
        elif pos in self.open_nodes:
            fill_color = Theme.NODE_OPEN
            outline = Theme.NODE_OPEN_PULSE
        elif pos in self.closed_nodes:
            fill_color = Theme.NODE_CLOSED
            outline = Theme.NODE_CLOSED_PALE
        elif cell_type == CellType.WALL:
            fill_color = Theme.CELL_WALL
            outline = Theme.CELL_WALL_BORDER
        elif cell_type == CellType.MUD:
            fill_color = Theme.CELL_MUD
            outline = "#92400e"
        elif cell_type == CellType.WATER:
            fill_color = Theme.CELL_WATER
            outline = "#0284c7"
        elif cell_type == CellType.FOREST:
            fill_color = Theme.CELL_FOREST
            outline = "#047857"
        else:
            fill_color = Theme.CELL_BG_EMPTY
            outline = Theme.CELL_BORDER

        # Draw base rectangle
        self.create_rectangle(
            rx1, ry1, rx2, ry2,
            fill=fill_color,
            outline=outline,
            width=1,
            tags=(tag, "cell")
        )

        # Draw icon or glyph indicators for special nodes
        center_x = (rx1 + rx2) / 2
        center_y = (ry1 + ry2) / 2

        if pos == self.grid_model.start:
            # Draw Start Star / S
            if self.cell_size >= 14:
                font_sz = max(7, int(self.cell_size * 0.45))
                self.create_text(
                    center_x, center_y,
                    text="S",
                    fill="#ffffff",
                    font=(Theme.FONT_FAMILY, font_sz, "bold"),
                    tags=(tag, "cell")
                )
        elif pos == self.grid_model.goal:
            # Draw Goal Target / G
            if self.cell_size >= 14:
                font_sz = max(7, int(self.cell_size * 0.45))
                self.create_text(
                    center_x, center_y,
                    text="G",
                    fill="#ffffff",
                    font=(Theme.FONT_FAMILY, font_sz, "bold"),
                    tags=(tag, "cell")
                )
        elif cell_type == CellType.MUD and self.cell_size >= 18:
            self.create_text(
                center_x, center_y,
                text="3x",
                fill="#fde68a",
                font=(Theme.FONT_FAMILY, max(6, int(self.cell_size * 0.35)), "bold"),
                tags=(tag, "cell")
            )
        elif cell_type == CellType.WATER and self.cell_size >= 18:
            self.create_text(
                center_x, center_y,
                text="5x",
                fill="#bae6fd",
                font=(Theme.FONT_FAMILY, max(6, int(self.cell_size * 0.35)), "bold"),
                tags=(tag, "cell")
            )
        elif cell_type == CellType.FOREST and self.cell_size >= 18:
            self.create_text(
                center_x, center_y,
                text="2x",
                fill="#a7f3d0",
                font=(Theme.FONT_FAMILY, max(6, int(self.cell_size * 0.35)), "bold"),
                tags=(tag, "cell")
            )

        # If agent is currently on this cell, draw glowing agent marker
        if pos == self.agent_position:
            radius = max(3.0, (self.cell_size - 4) / 2)
            self.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                fill=Theme.AGENT_TOKEN,
                outline="#ffffff",
                width=2,
                tags=(tag, "agent_token")
            )

    def _draw_path_overlay(self):
        self.delete("path_line")
        if len(self.path_nodes) < 2:
            return

        points = []
        for r, c in self.path_nodes:
            x1, y1, x2, y2 = self.get_cell_coords(r, c)
            points.extend([(x1 + x2) / 2, (y1 + y2) / 2])

        if len(points) >= 4:
            self.create_line(
                *points,
                fill=Theme.NODE_PATH_GLOW,
                width=max(2.0, self.cell_size * 0.25),
                capstyle=tk.ROUND,
                joinstyle=tk.ROUND,
                smooth=True,
                tags="path_line"
            )

    def redraw_full(self):
        self.delete("all")
        self.calculate_cell_metrics()

        # Background grid border
        bx1 = self.offset_x
        by1 = self.offset_y
        bx2 = bx1 + self.cell_size * self.grid_model.cols
        by2 = by1 + self.cell_size * self.grid_model.rows

        self.create_rectangle(
            bx1 - 2, by1 - 2, bx2 + 2, by2 + 2,
            outline=Theme.BORDER_COLOR,
            width=2,
            fill=Theme.BG_DARK
        )

        for r in range(self.grid_model.rows):
            for c in range(self.grid_model.cols):
                self.draw_cell(r, c)

        if self.path_nodes:
            self._draw_path_overlay()
