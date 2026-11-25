"""
Heuristic Graph Pathfinding Agent Search Engine.
Main Entry Point and GUI Application Orchestrator.
"""

import tkinter as tk
from typing import Optional, Dict, Any, Generator, List
import customtkinter as ctk
import time

from ui.theme import Theme
from ui.canvas_grid import CanvasGrid
from ui.metrics_hud import MetricsHUD
from ui.control_panel import ControlPanel
from ui.benchmark_view import BenchmarkWindow
from ui.export_dialog import ExportDialog

from environment.grid import Grid, CellType
from environment.maze_generators import (
    generate_recursive_backtracker,
    generate_prims,
    generate_recursive_division,
    generate_random_obstacles,
    generate_cellular_automata,
    generate_weighted_terrain_map
)

from algorithms.base import HeuristicType, SearchResult, BaseSearchAlgorithm
from algorithms.astar import AStar
from algorithms.dijkstra import Dijkstra
from algorithms.greedy_best_first import GreedyBestFirstSearch
from algorithms.bfs_dfs import BreadthFirstSearch, DepthFirstSearch
from algorithms.bidirectional_astar import BidirectionalAStar
from algorithms.jump_point_search import JumpPointSearch
from algorithms.q_learning import QLearningAgent

# Configure CustomTkinter
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class PathfindingApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("⚡ Heuristic Graph Pathfinding & RL Agent Search Engine")
        self.geometry("1400x900")
        self.minsize(1050, 700)
        self.configure(fg_color=Theme.BG_DARK)

        # Core State
        self.grid_model = Grid(rows=22, cols=38)
        self.current_algorithm_name = "A* Search"
        self.current_heuristic = HeuristicType.MANHATTAN
        self.heuristic_weight = 1.0
        self.allow_diagonal = False
        self.animation_delay_ms = 25

        # Execution & Animation State
        self.search_generator: Optional[Generator] = None
        self.is_animating = False
        self.is_paused = False
        self.last_result: Optional[SearchResult] = None
        self.agent_walk_step = 0
        self.agent_walk_path: List = []

        self._init_layout()
        self._init_default_maze()

    def _init_layout(self):
        # 1. Top Navbar Header
        self.header_frame = ctk.CTkFrame(self, fg_color=Theme.BG_PANEL, corner_radius=0, height=52)
        self.header_frame.pack(fill="x", side="top")

        brand_lbl = ctk.CTkLabel(
            self.header_frame,
            text="⚡ PATHFINDING AGENT SEARCH ENGINE",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_ACCENT
        )
        brand_lbl.pack(side="left", padx=20, pady=12)

        author_lbl = ctk.CTkLabel(
            self.header_frame,
            text="Heuristic Graph Optimization • Tabular Q-Learning RL • Interactive Visualizer",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11),
            text_color=Theme.TEXT_MUTED
        )
        author_lbl.pack(side="left", padx=10, pady=12)

        # 2. Real-Time Metrics HUD
        self.hud = MetricsHUD(self)
        self.hud.pack(fill="x", padx=16, pady=(12, 8))

        # 3. Main Body Split: Left Sidebar, Right Canvas
        self.body_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.body_frame.pack(fill="both", expand=True, padx=16, pady=(0, 8))

        # Left Control Panel
        self.controls = ControlPanel(
            self.body_frame,
            width=320,
            on_start_search=self.start_visualization,
            on_instant_solve=self.run_instant_solve,
            on_pause_resume=self.toggle_pause,
            on_step_forward=self.step_forward_manual,
            on_clear_search=self.clear_search_visuals,
            on_clear_grid=self.reset_entire_grid,
            on_generate_maze=self.generate_maze_by_name,
            on_brush_change=self.handle_brush_change,
            on_algorithm_change=self.handle_algorithm_change,
            on_heuristic_change=self.handle_heuristic_change,
            on_diagonal_toggle=self.handle_diagonal_toggle,
            on_weight_change=self.handle_weight_change,
            on_speed_change=self.handle_speed_change,
            on_grid_resize=self.handle_grid_resize,
            on_open_benchmark=self.open_benchmark_window,
            on_open_export=self.open_export_dialog
        )
        self.controls.pack(side="left", fill="y", padx=(0, 10))

        # Right Grid Container
        self.canvas_container = ctk.CTkFrame(
            self.body_frame,
            fg_color=Theme.BG_PANEL,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR
        )
        self.canvas_container.pack(side="right", fill="both", expand=True)

        self.canvas_grid = CanvasGrid(
            self.canvas_container,
            grid=self.grid_model,
            on_grid_modified=self.handle_grid_modified
        )
        self.canvas_grid.pack(fill="both", expand=True, padx=8, pady=8)

        # 4. Bottom Visual Legend Bar
        self._init_legend()

    def _init_legend(self):
        legend_frame = ctk.CTkFrame(self, fg_color=Theme.BG_PANEL, corner_radius=0, height=36)
        legend_frame.pack(fill="x", side="bottom", pady=0)

        items = [
            ("Start Pin", Theme.NODE_START),
            ("Goal Pin", Theme.NODE_GOAL),
            ("Wall", Theme.CELL_WALL),
            ("Mud (3x)", Theme.CELL_MUD),
            ("Water (5x)", Theme.CELL_WATER),
            ("Forest (2x)", Theme.CELL_FOREST),
            ("Frontier Open", Theme.NODE_OPEN),
            ("Explored Closed", Theme.NODE_CLOSED),
            ("Optimal Path", Theme.NODE_PATH),
            ("Agent Token", Theme.AGENT_TOKEN)
        ]

        for text, color in items:
            chip = ctk.CTkFrame(legend_frame, fg_color="transparent")
            chip.pack(side="left", padx=8, pady=6)

            dot = ctk.CTkFrame(chip, width=12, height=12, corner_radius=6, fg_color=color)
            dot.pack(side="left", padx=(0, 4))

            lbl = ctk.CTkLabel(
                chip,
                text=text,
                font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
                text_color=Theme.TEXT_SECONDARY
            )
            lbl.pack(side="left")

    def _init_default_maze(self):
        generate_recursive_backtracker(self.grid_model)
        self.canvas_grid.redraw_full()
        self.hud.reset_metrics()

    def _instantiate_current_algorithm(self) -> BaseSearchAlgorithm:
        name = self.current_algorithm_name
        if name == "A* Search":
            return AStar(heuristic_type=self.current_heuristic, weight=self.heuristic_weight)
        elif name == "Dijkstra's Algorithm":
            return Dijkstra()
        elif name == "Greedy Best-First":
            return GreedyBestFirstSearch(heuristic_type=self.current_heuristic)
        elif name == "Breadth-First Search (BFS)":
            return BreadthFirstSearch()
        elif name == "Depth-First Search (DFS)":
            return DepthFirstSearch()
        elif name == "Bi-directional A*":
            return BidirectionalAStar(heuristic_type=self.current_heuristic)
        elif name == "Jump Point Search (JPS)":
            return JumpPointSearch(heuristic_type=self.current_heuristic)
        elif name == "Q-Learning Agent (RL)":
            return QLearningAgent(episodes=250, max_steps_per_episode=200)
        else:
            return AStar(heuristic_type=self.current_heuristic, weight=self.heuristic_weight)

    def start_visualization(self):
        self.stop_any_animation()
        self.canvas_grid.reset_visual_search()
        self.hud.reset_metrics()

        algo = self._instantiate_current_algorithm()
        self.search_generator = algo.step_generator(self.grid_model, allow_diagonal=self.allow_diagonal)
        self.is_animating = True
        self.is_paused = False
        self._animation_loop()

    def _animation_loop(self):
        if not self.is_animating or self.is_paused:
            return

        try:
            step_data = next(self.search_generator)
            step_type = step_data.get("type")

            if step_type in ("init", "step"):
                self.canvas_grid.set_search_state(
                    current=step_data.get("current"),
                    open_set=step_data.get("open"),
                    closed_set=step_data.get("closed")
                )
                steps = step_data.get("steps", 0)
                open_cnt = len(step_data.get("open", []))
                closed_cnt = len(step_data.get("closed", []))
                self.hud.update_live_progress(steps, open_cnt, closed_cnt, self.grid_model.total_walkable_cells)

                self.after(self.animation_delay_ms, self._animation_loop)

            elif step_type == "complete":
                result: SearchResult = step_data["result"]
                self.last_result = result
                self.canvas_grid.set_search_state(
                    path=result.path,
                    closed_set=list(result.explored_nodes)
                )
                self.hud.update_completed_result(result, self.grid_model.total_walkable_cells)
                self.is_animating = False

                # Trigger virtual agent walking animation along solved path
                if result.path:
                    self._start_agent_walk_animation(result.path)

        except StopIteration as e:
            if e.value and isinstance(e.value, SearchResult):
                self.last_result = e.value
                self.hud.update_completed_result(e.value, self.grid_model.total_walkable_cells)
            self.is_animating = False
        except Exception as err:
            print("Animation error:", err)
            self.is_animating = False

    def _start_agent_walk_animation(self, path: List):
        self.agent_walk_path = path
        self.agent_walk_step = 0
        self._agent_walk_loop()

    def _agent_walk_loop(self):
        if self.agent_walk_step < len(self.agent_walk_path):
            pos = self.agent_walk_path[self.agent_walk_step]
            self.canvas_grid.set_search_state(agent_pos=pos)
            self.agent_walk_step += 1
            self.after(max(20, self.animation_delay_ms), self._agent_walk_loop)

    def run_instant_solve(self):
        self.stop_any_animation()
        self.canvas_grid.reset_visual_search()

        algo = self._instantiate_current_algorithm()
        result = algo.search(self.grid_model, allow_diagonal=self.allow_diagonal)
        self.last_result = result

        self.canvas_grid.set_search_state(
            closed_set=list(result.explored_nodes),
            path=result.path
        )
        self.hud.update_completed_result(result, self.grid_model.total_walkable_cells)

        if result.path:
            self._start_agent_walk_animation(result.path)

    def toggle_pause(self):
        if not self.is_animating:
            return
        self.is_paused = not self.is_paused
        self.controls.btn_pause.configure(
            text="▶ Resume" if self.is_paused else "⏸ Pause",
            fg_color=Theme.ACCENT_CYAN if self.is_paused else Theme.BG_CARD_HOVER,
            text_color="#090d16" if self.is_paused else "#ffffff"
        )
        if not self.is_paused:
            self._animation_loop()

    def step_forward_manual(self):
        if not self.search_generator:
            algo = self._instantiate_current_algorithm()
            self.search_generator = algo.step_generator(self.grid_model, allow_diagonal=self.allow_diagonal)
            self.is_animating = True
            self.is_paused = True

        try:
            step_data = next(self.search_generator)
            step_type = step_data.get("type")

            if step_type in ("init", "step"):
                self.canvas_grid.set_search_state(
                    current=step_data.get("current"),
                    open_set=step_data.get("open"),
                    closed_set=step_data.get("closed")
                )
                steps = step_data.get("steps", 0)
                open_cnt = len(step_data.get("open", []))
                closed_cnt = len(step_data.get("closed", []))
                self.hud.update_live_progress(steps, open_cnt, closed_cnt, self.grid_model.total_walkable_cells)
            elif step_type == "complete":
                result = step_data["result"]
                self.last_result = result
                self.canvas_grid.set_search_state(path=result.path, closed_set=list(result.explored_nodes))
                self.hud.update_completed_result(result, self.grid_model.total_walkable_cells)
                self.search_generator = None
        except StopIteration:
            self.search_generator = None

    def stop_any_animation(self):
        self.is_animating = False
        self.is_paused = False
        self.search_generator = None
        self.agent_walk_path = []
        self.controls.btn_pause.configure(text="⏸ Pause", fg_color=Theme.BG_CARD_HOVER, text_color="#ffffff")

    def clear_search_visuals(self):
        self.stop_any_animation()
        self.canvas_grid.reset_visual_search()
        self.hud.reset_metrics()

    def reset_entire_grid(self):
        self.stop_any_animation()
        self.grid_model.clear_all()
        self.canvas_grid.redraw_full()
        self.hud.reset_metrics()

    def generate_maze_by_name(self, name: str):
        self.stop_any_animation()
        if name == "Recursive Backtracker":
            generate_recursive_backtracker(self.grid_model)
        elif name == "Randomized Prim's":
            generate_prims(self.grid_model)
        elif name == "Recursive Division":
            generate_recursive_division(self.grid_model)
        elif name == "Random Obstacles (20%)":
            generate_random_obstacles(self.grid_model, density=0.20)
        elif name == "Random Obstacles (35%)":
            generate_random_obstacles(self.grid_model, density=0.35)
        elif name == "Random Obstacles (50%)":
            generate_random_obstacles(self.grid_model, density=0.50)
        elif name == "Cellular Automata Caves":
            generate_cellular_automata(self.grid_model)
        elif name == "Weighted Terrain Map":
            generate_weighted_terrain_map(self.grid_model)

        self.canvas_grid.redraw_full()
        self.hud.reset_metrics()

    def handle_brush_change(self, brush_type: CellType):
        self.canvas_grid.set_brush(brush_type)

    def handle_algorithm_change(self, algo_name: str):
        self.current_algorithm_name = algo_name

    def handle_heuristic_change(self, heuristic: HeuristicType):
        self.current_heuristic = heuristic

    def handle_diagonal_toggle(self, enabled: bool):
        self.allow_diagonal = enabled

    def handle_weight_change(self, weight: float):
        self.heuristic_weight = weight

    def handle_speed_change(self, delay_ms: int):
        self.animation_delay_ms = delay_ms

    def handle_grid_resize(self, rows: int, cols: int):
        self.stop_any_animation()
        self.grid_model.reset_dimensions(rows, cols)
        self.canvas_grid.redraw_full()
        self.hud.reset_metrics()

    def handle_grid_modified(self):
        # Clears search path on drawing to keep visualization coherent
        if not self.is_animating:
            self.canvas_grid.path_nodes.clear()
            self.canvas_grid.delete("path_line")

    def open_benchmark_window(self):
        BenchmarkWindow(
            self,
            grid_model=self.grid_model,
            allow_diagonal=self.allow_diagonal,
            heuristic=self.current_heuristic
        )

    def open_export_dialog(self):
        ExportDialog(
            self,
            grid_model=self.grid_model,
            last_result=self.last_result
        )

    def on_grid_loaded(self):
        self.canvas_grid.redraw_full()
        self.hud.reset_metrics()

if __name__ == "__main__":
    app = PathfindingApp()
    app.mainloop()
