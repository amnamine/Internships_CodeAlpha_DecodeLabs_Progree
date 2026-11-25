"""
Real-time Search Engine Metrics HUD (Heads-Up Display).
Displays live search stats, runtime in ms, expanded node densities, step count, and path costs.
"""

import tkinter as tk
from typing import Dict, Any, Optional
import customtkinter as ctk
from ui.theme import Theme
from algorithms.base import SearchResult

class MetricsHUD(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(
            master,
            fg_color=Theme.BG_CARD,
            corner_radius=12,
            border_width=1,
            border_color=Theme.BORDER_COLOR,
            **kwargs
        )

        self._init_ui()

    def _init_ui(self):
        # Configure Grid
        self.grid_columnconfigure((0, 1, 2, 3, 4, 5), weight=1, uniform="metric_col")

        # Metric 1: Status
        self.status_card = self._create_card(0, "STATUS", "IDLE", Theme.TEXT_MUTED)

        # Metric 2: Step Count / Path Length
        self.steps_card = self._create_card(1, "STEPS / PATH", "0 / 0", Theme.ACCENT_CYAN)

        # Metric 3: Total Path Cost
        self.cost_card = self._create_card(2, "PATH COST", "0.00", Theme.ACCENT_EMERALD)

        # Metric 4: Nodes Expanded & Density
        self.expanded_card = self._create_card(3, "EXPANDED NODES", "0 (0.0%)", Theme.ACCENT_VIOLET)

        # Metric 5: High-Precision Runtime
        self.runtime_card = self._create_card(4, "EXECUTION TIME", "0.00 ms", Theme.ACCENT_AMBER)

        # Metric 6: Peak Frontier
        self.frontier_card = self._create_card(5, "PEAK FRONTIER", "0", Theme.ACCENT_SKY)

    def _create_card(self, col: int, label_text: str, default_val: str, val_color: str):
        card = ctk.CTkFrame(self, fg_color="transparent")
        card.grid(row=0, column=col, padx=8, pady=8, sticky="nsew")

        lbl = ctk.CTkLabel(
            card,
            text=label_text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10, weight="bold"),
            text_color=Theme.TEXT_SECONDARY
        )
        lbl.pack(anchor="center")

        val = ctk.CTkLabel(
            card,
            text=default_val,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=16, weight="bold"),
            text_color=val_color
        )
        val.pack(anchor="center", pady=(2, 0))

        return {"frame": card, "label": lbl, "value": val, "default_color": val_color}

    def update_live_progress(self, steps: int, open_count: int, closed_count: int, total_walkable: int):
        self.status_card["value"].configure(text="SEARCHING...", text_color=Theme.ACCENT_AMBER)
        self.steps_card["value"].configure(text=f"{steps} steps")
        density = (closed_count / total_walkable * 100) if total_walkable > 0 else 0.0
        self.expanded_card["value"].configure(text=f"{closed_count} ({density:.1f}%)")
        self.frontier_card["value"].configure(text=str(open_count))

    def update_completed_result(self, result: SearchResult, total_walkable: int):
        if result.success:
            self.status_card["value"].configure(text="PATH OPTIMIZED", text_color=Theme.ACCENT_EMERALD)
        else:
            self.status_card["value"].configure(text="NO PATH FOUND", text_color=Theme.ACCENT_ROSE)

        path_len = len(result.path)
        self.steps_card["value"].configure(text=f"{result.step_count} / {path_len}")
        self.cost_card["value"].configure(text=f"{result.path_cost:.2f}")

        density_pct = (result.expanded_nodes_count / total_walkable * 100) if total_walkable > 0 else 0.0
        self.expanded_card["value"].configure(text=f"{result.expanded_nodes_count} ({density_pct:.1f}%)")

        if result.runtime_ms < 1.0:
            time_str = f"{result.runtime_ms * 1000:.1f} µs"
        else:
            time_str = f"{result.runtime_ms:.2f} ms"
        self.runtime_card["value"].configure(text=time_str)

        self.frontier_card["value"].configure(text=str(result.peak_frontier))

    def reset_metrics(self):
        self.status_card["value"].configure(text="READY", text_color=Theme.TEXT_SECONDARY)
        self.steps_card["value"].configure(text="0 / 0")
        self.cost_card["value"].configure(text="0.00")
        self.expanded_card["value"].configure(text="0 (0.0%)")
        self.runtime_card["value"].configure(text="0.00 ms")
        self.frontier_card["value"].configure(text="0")
