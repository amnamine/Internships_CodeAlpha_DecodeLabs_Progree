"""
Control Panel Sidebar Component.
Provides controls for algorithm selection, heuristic tuning, maze generation, drawing tools, and playback.
"""

import tkinter as tk
from typing import Callable, Dict, Any, Optional
import customtkinter as ctk
from environment.grid import CellType
from algorithms.base import HeuristicType
from ui.theme import Theme

class ControlPanel(ctk.CTkScrollableFrame):
    def __init__(
        self,
        master,
        on_start_search: Callable[[], None],
        on_instant_solve: Callable[[], None],
        on_pause_resume: Callable[[], None],
        on_step_forward: Callable[[], None],
        on_clear_search: Callable[[], None],
        on_clear_grid: Callable[[], None],
        on_generate_maze: Callable[[str], None],
        on_brush_change: Callable[[CellType], None],
        on_algorithm_change: Callable[[str], None],
        on_heuristic_change: Callable[[HeuristicType], None],
        on_diagonal_toggle: Callable[[bool], None],
        on_weight_change: Callable[[float], None],
        on_speed_change: Callable[[int], None],
        on_grid_resize: Callable[[int, int], None],
        on_open_benchmark: Callable[[], None],
        on_open_export: Callable[[], None],
        **kwargs
    ):
        super().__init__(
            master,
            fg_color=Theme.BG_PANEL,
            scrollbar_button_color=Theme.BG_CARD_HOVER,
            **kwargs
        )

        self.on_start_search = on_start_search
        self.on_instant_solve = on_instant_solve
        self.on_pause_resume = on_pause_resume
        self.on_step_forward = on_step_forward
        self.on_clear_search = on_clear_search
        self.on_clear_grid = on_clear_grid
        self.on_generate_maze = on_generate_maze
        self.on_brush_change = on_brush_change
        self.on_algorithm_change = on_algorithm_change
        self.on_heuristic_change = on_heuristic_change
        self.on_diagonal_toggle = on_diagonal_toggle
        self.on_weight_change = on_weight_change
        self.on_speed_change = on_speed_change
        self.on_grid_resize = on_grid_resize
        self.on_open_benchmark = on_open_benchmark
        self.on_open_export = on_open_export

        self._init_ui()

    def _init_ui(self):
        # Header / Title
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(fill="x", padx=12, pady=(12, 16))

        title_lbl = ctk.CTkLabel(
            title_frame,
            text="⚡ SEARCH ENGINE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=Theme.TEXT_ACCENT
        )
        title_lbl.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            title_frame,
            text="Heuristic & RL Graph Pathfinding",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        )
        subtitle.pack(anchor="w")

        # ---------------- Section: Search Algorithm ----------------
        self._create_section_label("ALGORITHM & HEURISTICS")

        algo_card = self._create_card()
        algo_card.pack(fill="x", padx=12, pady=6)

        # Algorithm Dropdown
        self.algo_dropdown = ctk.CTkOptionMenu(
            algo_card,
            values=[
                "A* Search",
                "Dijkstra's Algorithm",
                "Bi-directional A*",
                "Greedy Best-First",
                "Breadth-First Search (BFS)",
                "Depth-First Search (DFS)",
                "Jump Point Search (JPS)",
                "Q-Learning Agent (RL)"
            ],
            command=self._handle_algo_selected,
            fg_color=Theme.BG_CARD,
            button_color=Theme.ACCENT_INDIGO,
            dropdown_fg_color=Theme.BG_CARD,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold")
        )
        self.algo_dropdown.set("A* Search")
        self.algo_dropdown.pack(fill="x", padx=10, pady=(10, 6))

        # Heuristic Dropdown
        self.heuristic_label = ctk.CTkLabel(
            algo_card,
            text="Heuristic Metric:",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_SECONDARY
        )
        self.heuristic_label.pack(anchor="w", padx=10, pady=(4, 0))

        self.heuristic_dropdown = ctk.CTkOptionMenu(
            algo_card,
            values=[
                "Manhattan (L1)",
                "Euclidean (L2)",
                "Chebyshev (Linf)",
                "Octile (Diagonal)"
            ],
            command=self._handle_heuristic_selected,
            fg_color=Theme.BG_DARK,
            button_color=Theme.BG_CARD_HOVER,
            dropdown_fg_color=Theme.BG_CARD,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11)
        )
        self.heuristic_dropdown.set("Manhattan (L1)")
        self.heuristic_dropdown.pack(fill="x", padx=10, pady=(2, 8))

        # Heuristic Weight Slider (for Weighted A*)
        self.weight_label = ctk.CTkLabel(
            algo_card,
            text="Heuristic Weight (w): 1.0x",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_SECONDARY
        )
        self.weight_label.pack(anchor="w", padx=10, pady=(4, 0))

        self.weight_slider = ctk.CTkSlider(
            algo_card,
            from_=1.0,
            to=3.0,
            number_of_steps=20,
            command=self._handle_weight_changed,
            progress_color=Theme.ACCENT_CYAN,
            button_color=Theme.ACCENT_CYAN
        )
        self.weight_slider.set(1.0)
        self.weight_slider.pack(fill="x", padx=10, pady=(2, 8))

        # Diagonal Movement Switch
        self.diag_switch = ctk.CTkSwitch(
            algo_card,
            text="8-Way Diagonal Movement",
            command=self._handle_diagonal_toggle,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            progress_color=Theme.ACCENT_EMERALD
        )
        self.diag_switch.pack(anchor="w", padx=10, pady=(4, 10))

        # ---------------- Section: Execution & Playback ----------------
        self._create_section_label("SEARCH CONTROLS")
        play_card = self._create_card()
        play_card.pack(fill="x", padx=12, pady=6)

        # Primary Action: Visualize Search
        self.btn_search = ctk.CTkButton(
            play_card,
            text="▶  START VISUALIZATION",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=12, weight="bold"),
            fg_color=Theme.ACCENT_CYAN,
            hover_color="#0891b2",
            text_color="#090d16",
            height=36,
            command=self.on_start_search
        )
        self.btn_search.pack(fill="x", padx=10, pady=(10, 6))

        # Instant Solve Button
        self.btn_instant = ctk.CTkButton(
            play_card,
            text="⚡  INSTANT SOLVE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.ACCENT_INDIGO,
            hover_color="#4f46e5",
            height=32,
            command=self.on_instant_solve
        )
        self.btn_instant.pack(fill="x", padx=10, pady=(0, 6))

        # Step & Pause Controls Row
        step_row = ctk.CTkFrame(play_card, fg_color="transparent")
        step_row.pack(fill="x", padx=10, pady=(0, 6))

        self.btn_pause = ctk.CTkButton(
            step_row,
            text="⏸ Pause",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            fg_color=Theme.BG_CARD_HOVER,
            hover_color="#475569",
            width=80,
            command=self.on_pause_resume
        )
        self.btn_pause.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_step = ctk.CTkButton(
            step_row,
            text="⏭ Step",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            fg_color=Theme.BG_CARD_HOVER,
            hover_color="#475569",
            width=80,
            command=self.on_step_forward
        )
        self.btn_step.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # Animation Speed Slider
        self.speed_label = ctk.CTkLabel(
            play_card,
            text="Animation Speed: Fast (30ms)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_SECONDARY
        )
        self.speed_label.pack(anchor="w", padx=10, pady=(4, 0))

        self.speed_slider = ctk.CTkSlider(
            play_card,
            from_=1,
            to=100,
            number_of_steps=100,
            command=self._handle_speed_changed,
            progress_color=Theme.ACCENT_AMBER,
            button_color=Theme.ACCENT_AMBER
        )
        self.speed_slider.set(70)
        self.speed_slider.pack(fill="x", padx=10, pady=(2, 6))

        # Clear Controls Row
        clear_row = ctk.CTkFrame(play_card, fg_color="transparent")
        clear_row.pack(fill="x", padx=10, pady=(4, 10))

        self.btn_clear_path = ctk.CTkButton(
            clear_row,
            text="🧹 Clear Path",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            fg_color=Theme.BG_DARK,
            hover_color=Theme.BG_CARD_HOVER,
            command=self.on_clear_search
        )
        self.btn_clear_path.pack(side="left", expand=True, fill="x", padx=(0, 4))

        self.btn_clear_all = ctk.CTkButton(
            clear_row,
            text="❌ Reset Grid",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            fg_color="#7f1d1d",
            hover_color="#991b1b",
            command=self.on_clear_grid
        )
        self.btn_clear_all.pack(side="right", expand=True, fill="x", padx=(4, 0))

        # ---------------- Section: Procedural Maze & Obstacle Generation ----------------
        self._create_section_label("MAZE & TERRAIN GENERATORS")
        maze_card = self._create_card()
        maze_card.pack(fill="x", padx=12, pady=6)

        self.maze_dropdown = ctk.CTkOptionMenu(
            maze_card,
            values=[
                "Recursive Backtracker",
                "Randomized Prim's",
                "Recursive Division",
                "Random Obstacles (20%)",
                "Random Obstacles (35%)",
                "Random Obstacles (50%)",
                "Cellular Automata Caves",
                "Weighted Terrain Map"
            ],
            fg_color=Theme.BG_DARK,
            button_color=Theme.BG_CARD_HOVER,
            dropdown_fg_color=Theme.BG_CARD,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11)
        )
        self.maze_dropdown.set("Recursive Backtracker")
        self.maze_dropdown.pack(fill="x", padx=10, pady=(10, 6))

        self.btn_gen_maze = ctk.CTkButton(
            maze_card,
            text="🎲  GENERATE MAZE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.ACCENT_VIOLET,
            hover_color="#7c3aed",
            command=self._handle_generate_maze
        )
        self.btn_gen_maze.pack(fill="x", padx=10, pady=(0, 10))

        # ---------------- Section: Interactive Drawing Tools ----------------
        self._create_section_label("DRAWING BRUSHES")
        brush_card = self._create_card()
        brush_card.pack(fill="x", padx=12, pady=6)

        self.brush_seg = ctk.CTkSegmentedButton(
            brush_card,
            values=["Wall", "Mud (3x)", "Water (5x)", "Forest (2x)", "Erase"],
            command=self._handle_brush_selected,
            selected_color=Theme.ACCENT_CYAN,
            selected_hover_color="#0891b2",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=9, weight="bold")
        )
        self.brush_seg.set("Wall")
        self.brush_seg.pack(fill="x", padx=8, pady=8)

        # ---------------- Section: Grid Dimensions ----------------
        self._create_section_label("GRID RESOLUTION")
        grid_card = self._create_card()
        grid_card.pack(fill="x", padx=12, pady=6)

        self.grid_size_menu = ctk.CTkOptionMenu(
            grid_card,
            values=["Compact: 15 x 25", "Standard: 22 x 38", "Large: 28 x 50", "Ultra: 35 x 65"],
            command=self._handle_grid_size_selected,
            fg_color=Theme.BG_DARK,
            button_color=Theme.BG_CARD_HOVER,
            dropdown_fg_color=Theme.BG_CARD,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11)
        )
        self.grid_size_menu.set("Standard: 22 x 38")
        self.grid_size_menu.pack(fill="x", padx=10, pady=10)

        # ---------------- Section: Analysis & Export ----------------
        self._create_section_label("BENCHMARK & LOGS")
        tools_card = self._create_card()
        tools_card.pack(fill="x", padx=12, pady=(6, 20))

        self.btn_benchmark = ctk.CTkButton(
            tools_card,
            text="📊  MULTI-AGENT BENCHMARK",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.ACCENT_EMERALD,
            hover_color="#059669",
            text_color="#090d16",
            command=self.on_open_benchmark
        )
        self.btn_benchmark.pack(fill="x", padx=10, pady=(10, 6))

        self.btn_export = ctk.CTkButton(
            tools_card,
            text="💾  EXPORT LOGS & TELEMETRY",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.BG_CARD_HOVER,
            hover_color="#475569",
            command=self.on_open_export
        )
        self.btn_export.pack(fill="x", padx=10, pady=(0, 10))

    def _create_section_label(self, text: str):
        lbl = ctk.CTkLabel(
            self,
            text=text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_MUTED
        )
        lbl.pack(anchor="w", padx=14, pady=(12, 2))

    def _create_card(self):
        return ctk.CTkFrame(
            self,
            fg_color=Theme.BG_CARD,
            corner_radius=10,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )

    def _handle_algo_selected(self, algo_name: str):
        # Hide heuristic settings for Dijkstra / BFS / DFS / Q-Learning if irrelevant
        is_heuristic = "A*" in algo_name or "Greedy" in algo_name or "JPS" in algo_name
        self.heuristic_dropdown.configure(state="normal" if is_heuristic else "disabled")
        self.weight_slider.configure(state="normal" if "A*" in algo_name else "disabled")
        self.on_algorithm_change(algo_name)

    def _handle_heuristic_selected(self, h_str: str):
        for h_type in HeuristicType:
            if h_type.value == h_str:
                self.on_heuristic_change(h_type)
                break

    def _handle_weight_changed(self, val: float):
        self.weight_label.configure(text=f"Heuristic Weight (w): {val:.2f}x")
        self.on_weight_change(val)

    def _handle_diagonal_toggle(self):
        self.on_diagonal_toggle(self.diag_switch.get() == 1)

    def _handle_speed_changed(self, val: float):
        # Map slider 1..100 to delay in ms: 100 -> 1ms, 1 -> 250ms
        delay = int(max(1, (100 - val) * 2.5 + 1))
        label_text = "Instant" if val >= 95 else ("Fast" if val >= 60 else ("Medium" if val >= 30 else "Slow"))
        self.speed_label.configure(text=f"Animation Speed: {label_text} ({delay}ms)")
        self.on_speed_change(delay)

    def _handle_generate_maze(self):
        maze_type = self.maze_dropdown.get()
        self.on_generate_maze(maze_type)

    def _handle_brush_selected(self, val: str):
        mapping = {
            "Wall": CellType.WALL,
            "Mud (3x)": CellType.MUD,
            "Water (5x)": CellType.WATER,
            "Forest (2x)": CellType.FOREST,
            "Erase": CellType.EMPTY
        }
        self.on_brush_change(mapping.get(val, CellType.WALL))

    def _handle_grid_size_selected(self, val: str):
        if "15 x 25" in val:
            self.on_grid_resize(15, 25)
        elif "22 x 38" in val:
            self.on_grid_resize(22, 38)
        elif "28 x 50" in val:
            self.on_grid_resize(28, 50)
        elif "35 x 65" in val:
            self.on_grid_resize(35, 65)
