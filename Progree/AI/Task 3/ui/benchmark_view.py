"""
Benchmark Suite and Comparative Analysis Window.
Executes multiple graph search agents on identical grid environments,
renders comparative tables and embedded Matplotlib visual plots.
"""

import tkinter as tk
from tkinter import ttk
from typing import List, Dict, Any, Optional
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import copy

from ui.theme import Theme
from environment.grid import Grid
from algorithms.base import HeuristicType, SearchResult
from algorithms.astar import AStar
from algorithms.dijkstra import Dijkstra
from algorithms.greedy_best_first import GreedyBestFirstSearch
from algorithms.bfs_dfs import BreadthFirstSearch, DepthFirstSearch
from algorithms.bidirectional_astar import BidirectionalAStar
from algorithms.jump_point_search import JumpPointSearch
from algorithms.q_learning import QLearningAgent

class BenchmarkWindow(ctk.CTkToplevel):
    def __init__(self, master, grid_model: Grid, allow_diagonal: bool = False, heuristic: HeuristicType = HeuristicType.MANHATTAN):
        super().__init__(master)
        self.title("⚡ Multi-Agent Graph Pathfinding Benchmark Suite")
        self.geometry("1100x750")
        self.configure(fg_color=Theme.BG_DARK)
        self.grid_model = grid_model
        self.allow_diagonal = allow_diagonal
        self.heuristic = heuristic
        self.results: List[SearchResult] = []

        self._init_ui()
        self.run_benchmarks()

    def _init_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=Theme.BG_PANEL, corner_radius=0, height=50)
        header.pack(fill="x", padx=0, pady=0)

        title = ctk.CTkLabel(
            header,
            text="📊 Comprehensive Algorithm Optimization & Performance Benchmark",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=15, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left", padx=20, pady=12)

        btn_rerun = ctk.CTkButton(
            header,
            text="🔄 Re-run Benchmark",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=Theme.ACCENT_CYAN,
            text_color="#090d16",
            hover_color="#0891b2",
            command=self.run_benchmarks
        )
        btn_rerun.pack(side="right", padx=20, pady=10)

        # Main Split Container: Top Table, Bottom Plots
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=16, pady=16)

        # ---------------- Table Section ----------------
        table_card = ctk.CTkFrame(main_frame, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        table_card.pack(fill="x", pady=(0, 12))

        table_title = ctk.CTkLabel(
            table_card,
            text="EXPERIMENTAL RUNTIME & NODE EXPANSION METRICS",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        table_title.pack(anchor="w", padx=12, pady=(10, 4))

        columns = ("algo", "status", "cost", "steps", "expanded", "density", "runtime", "frontier")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", height=8)

        # Style Treeview
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "Treeview",
            background=Theme.BG_DARK,
            foreground=Theme.TEXT_PRIMARY,
            fieldbackground=Theme.BG_DARK,
            rowheight=24,
            font=(Theme.FONT_FAMILY, 9)
        )
        style.configure(
            "Treeview.Heading",
            background=Theme.BG_CARD_HOVER,
            foreground=Theme.TEXT_PRIMARY,
            font=(Theme.FONT_FAMILY, 9, "bold")
        )
        style.map("Treeview", background=[("selected", Theme.ACCENT_INDIGO)])

        self.tree.heading("algo", text="Algorithm")
        self.tree.heading("status", text="Success")
        self.tree.heading("cost", text="Path Cost")
        self.tree.heading("steps", text="Step Count")
        self.tree.heading("expanded", text="Expanded Nodes")
        self.tree.heading("density", text="Exp. Density (%)")
        self.tree.heading("runtime", text="Runtime (ms)")
        self.tree.heading("frontier", text="Peak Frontier")

        self.tree.column("algo", width=180, anchor="w")
        self.tree.column("status", width=80, anchor="center")
        self.tree.column("cost", width=90, anchor="e")
        self.tree.column("steps", width=90, anchor="e")
        self.tree.column("expanded", width=110, anchor="e")
        self.tree.column("density", width=110, anchor="e")
        self.tree.column("runtime", width=100, anchor="e")
        self.tree.column("frontier", width=90, anchor="e")

        self.tree.pack(fill="x", padx=12, pady=(0, 12))

        # ---------------- Matplotlib Visual Charts Section ----------------
        chart_card = ctk.CTkFrame(main_frame, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        chart_card.pack(fill="both", expand=True)

        self.fig = Figure(figsize=(10, 4.2), dpi=100, facecolor=Theme.BG_CARD)
        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=chart_card)
        self.canvas_chart.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    def run_benchmarks(self):
        # Clear table
        for row in self.tree.get_children():
            self.tree.delete(row)

        test_suite = [
            AStar(heuristic_type=self.heuristic, weight=1.0),
            AStar(heuristic_type=self.heuristic, weight=1.5),
            Dijkstra(),
            BidirectionalAStar(heuristic_type=self.heuristic),
            GreedyBestFirstSearch(heuristic_type=self.heuristic),
            BreadthFirstSearch(),
            DepthFirstSearch(),
            JumpPointSearch(heuristic_type=self.heuristic),
            QLearningAgent(episodes=200, max_steps_per_episode=200)
        ]

        self.results = []
        for algo in test_suite:
            # Deep copy grid to ensure no side effects
            grid_copy = copy.deepcopy(self.grid_model)
            res = algo.search(grid_copy, allow_diagonal=self.allow_diagonal)
            self.results.append(res)

            status_str = "✔ Optimal" if res.success else "✖ Failed"
            density_str = f"{res.expanded_density * 100:.1f}%"
            time_str = f"{res.runtime_ms:.3f}"

            self.tree.insert("", "end", values=(
                res.algorithm_name,
                status_str,
                f"{res.path_cost:.2f}",
                res.step_count,
                res.expanded_nodes_count,
                density_str,
                time_str,
                res.peak_frontier
            ))

        self._render_charts()

    def _render_charts(self):
        self.fig.clear()

        # 3 Subplots: 1. Runtime, 2. Expanded Nodes, 3. Path Cost
        ax1 = self.fig.add_subplot(131)
        ax2 = self.fig.add_subplot(132)
        ax3 = self.fig.add_subplot(133)

        for ax in (ax1, ax2, ax3):
            ax.set_facecolor(Theme.BG_DARK)
            ax.tick_params(colors=Theme.TEXT_SECONDARY, labelsize=7)
            for spine in ax.spines.values():
                spine.set_color(Theme.BORDER_COLOR)

        names = [r.algorithm_name.replace("Search", "").replace("Algorithm", "").strip() for r in self.results]
        # Truncate names for clear chart labels
        short_names = [n[:12] + ".." if len(n) > 12 else n for n in names]
        y_pos = list(range(len(names)))

        runtimes = [r.runtime_ms for r in self.results]
        expanded = [r.expanded_nodes_count for r in self.results]
        costs = [r.path_cost if r.success else 0.0 for r in self.results]

        # Colors
        colors_runtime = ["#38bdf8", "#0284c7", "#6366f1", "#8b5cf6", "#f59e0b", "#ec4899", "#ef4444", "#10b981", "#14b8a6"]
        
        # Plot 1: Runtime
        bars1 = ax1.barh(y_pos, runtimes, color=colors_runtime[:len(names)], height=0.6)
        ax1.set_yticks(y_pos)
        ax1.set_yticklabels(short_names, fontsize=7)
        ax1.invert_yaxis()
        ax1.set_title("Runtime (ms) - Lower is Better", color=Theme.TEXT_PRIMARY, fontsize=9, fontweight="bold")
        ax1.grid(axis="x", color="#1e293b", linestyle="--", alpha=0.6)

        # Plot 2: Expanded Nodes
        ax2.barh(y_pos, expanded, color="#818cf8", height=0.6)
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels([])
        ax2.invert_yaxis()
        ax2.set_title("Expanded Nodes (Exploration)", color=Theme.TEXT_PRIMARY, fontsize=9, fontweight="bold")
        ax2.grid(axis="x", color="#1e293b", linestyle="--", alpha=0.6)

        # Plot 3: Path Cost
        ax3.barh(y_pos, costs, color="#10b981", height=0.6)
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels([])
        ax3.invert_yaxis()
        ax3.set_title("Final Path Cost (Optimality)", color=Theme.TEXT_PRIMARY, fontsize=9, fontweight="bold")
        ax3.grid(axis="x", color="#1e293b", linestyle="--", alpha=0.6)

        self.fig.tight_layout()
        self.canvas_chart.draw()
