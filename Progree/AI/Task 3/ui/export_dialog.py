"""
Export and Serialization Engine.
Handles saving/loading mazes, exporting JSON telemetry logs, CSV summaries, and PNG snapshots.
"""

import json
import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Optional, Dict, Any, List
import customtkinter as ctk
from PIL import Image, ImageDraw

from ui.theme import Theme
from environment.grid import Grid, CellType, CELL_COSTS
from algorithms.base import SearchResult

class ExportDialog(ctk.CTkToplevel):
    def __init__(self, master, grid_model: Grid, last_result: Optional[SearchResult] = None):
        super().__init__(master)
        self.title("💾 Export Pathfinding Logs & Map Telemetry")
        self.geometry("620x520")
        self.configure(fg_color=Theme.BG_DARK)
        self.grid_model = grid_model
        self.last_result = last_result

        self._init_ui()

    def _init_ui(self):
        header = ctk.CTkFrame(self, fg_color=Theme.BG_PANEL, corner_radius=0, height=50)
        header.pack(fill="x", padx=0, pady=0)

        title = ctk.CTkLabel(
            header,
            text="📁 Export Data & Visualization Logs",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=14, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        title.pack(side="left", padx=16, pady=12)

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=16, pady=16)

        # 1. JSON Detailed Step Logs
        self._create_export_card(
            content,
            title="1. Detailed Telemetry Log (JSON)",
            desc="Exports complete step-by-step exploration trace with f, g, h values, frontier states, and path coords.",
            btn_text="Export Step Logs JSON",
            btn_color=Theme.ACCENT_CYAN,
            action=self.export_json_logs
        )

        # 2. CSV Summary
        self._create_export_card(
            content,
            title="2. Performance Metrics (CSV)",
            desc="Exports tabular summary with runtime, nodes expanded, density %, path length, and total costs.",
            btn_text="Export Metrics CSV",
            btn_color=Theme.ACCENT_EMERALD,
            action=self.export_csv_metrics
        )

        # 3. High-Res PNG Map Snapshot
        self._create_export_card(
            content,
            title="3. High-Resolution Snapshot (PNG)",
            desc="Renders and exports a raster image of current maze layout, terrain, and solution path.",
            btn_text="Export Snapshot PNG",
            btn_color=Theme.ACCENT_VIOLET,
            action=self.export_png_snapshot
        )

        # 4. Save/Load Grid Setup
        save_load_card = ctk.CTkFrame(content, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        save_load_card.pack(fill="x", pady=6)

        lbl = ctk.CTkLabel(
            save_load_card,
            text="4. Grid Map Blueprint (Save / Load)",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        lbl.pack(anchor="w", padx=12, pady=(10, 2))

        desc = ctk.CTkLabel(
            save_load_card,
            text="Save current maze walls and weighted terrain to reuse later, or load an existing layout file.",
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_SECONDARY
        )
        desc.pack(anchor="w", padx=12, pady=(0, 8))

        btn_row = ctk.CTkFrame(save_load_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=12, pady=(0, 10))

        btn_save = ctk.CTkButton(
            btn_row,
            text="💾 Save Grid File",
            fg_color=Theme.BG_CARD_HOVER,
            hover_color="#475569",
            command=self.save_grid_file
        )
        btn_save.pack(side="left", expand=True, fill="x", padx=(0, 6))

        btn_load = ctk.CTkButton(
            btn_row,
            text="📂 Load Grid File",
            fg_color=Theme.BG_CARD_HOVER,
            hover_color="#475569",
            command=self.load_grid_file
        )
        btn_load.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _create_export_card(self, parent, title: str, desc: str, btn_text: str, btn_color: str, action):
        card = ctk.CTkFrame(parent, fg_color=Theme.BG_CARD, corner_radius=10, border_width=1, border_color=Theme.BORDER_COLOR)
        card.pack(fill="x", pady=6)

        t = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            text_color=Theme.TEXT_PRIMARY
        )
        t.pack(anchor="w", padx=12, pady=(10, 2))

        d = ctk.CTkLabel(
            card,
            text=desc,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=10),
            text_color=Theme.TEXT_SECONDARY
        )
        d.pack(anchor="w", padx=12, pady=(0, 8))

        btn = ctk.CTkButton(
            card,
            text=btn_text,
            font=ctk.CTkFont(family=Theme.FONT_FAMILY, size=11, weight="bold"),
            fg_color=btn_color,
            hover_color="#334155",
            text_color="#090d16" if btn_color in (Theme.ACCENT_CYAN, Theme.ACCENT_EMERALD) else "#ffffff",
            command=action
        )
        btn.pack(anchor="e", padx=12, pady=(0, 10))

    def export_json_logs(self):
        if not self.last_result:
            messagebox.showwarning("No Data", "Please execute a search first before exporting logs.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON Files", "*.json")],
            initialfile="pathfinding_telemetry_log.json"
        )
        if not filepath:
            return

        data = {
            "grid_metadata": self.grid_model.to_dict(),
            "search_summary": self.last_result.to_dict(),
            "step_by_step_logs": [log.to_dict() for log in self.last_result.step_logs]
        }

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Export Successful", f"Telemetry log saved successfully to:\n{filepath}")

    def export_csv_metrics(self):
        if not self.last_result:
            messagebox.showwarning("No Data", "Please execute a search first before exporting metrics.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv")],
            initialfile="pathfinding_metrics.csv"
        )
        if not filepath:
            return

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Algorithm", "Success", "Path Length", "Path Cost", "Step Count",
                "Expanded Nodes", "Expanded Density (%)", "Runtime (ms)", "Peak Frontier", "Obstacle Density (%)"
            ])
            res = self.last_result
            writer.writerow([
                res.algorithm_name,
                res.success,
                len(res.path),
                f"{res.path_cost:.4f}",
                res.step_count,
                res.expanded_nodes_count,
                f"{res.expanded_density * 100:.2f}",
                f"{res.runtime_ms:.4f}",
                res.peak_frontier,
                f"{self.grid_model.obstacle_density * 100:.2f}"
            ])

        messagebox.showinfo("Export Successful", f"Metrics CSV saved successfully to:\n{filepath}")

    def export_png_snapshot(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG Images", "*.png")],
            initialfile="pathfinding_maze_snapshot.png"
        )
        if not filepath:
            return

        cell_px = 24
        img_w = self.grid_model.cols * cell_px
        img_h = self.grid_model.rows * cell_px

        img = Image.new("RGB", (img_w, img_h), color="#090d16")
        draw = ImageDraw.Draw(img)

        # Color mapping
        colors = {
            CellType.EMPTY: "#131b2e",
            CellType.WALL: "#334155",
            CellType.MUD: "#78350f",
            CellType.WATER: "#0369a1",
            CellType.FOREST: "#065f46",
        }

        path_set = set(self.last_result.path) if self.last_result else set()
        explored_set = self.last_result.explored_nodes if self.last_result else set()

        for r in range(self.grid_model.rows):
            for c in range(self.grid_model.cols):
                x1 = c * cell_px
                y1 = r * cell_px
                x2 = x1 + cell_px - 1
                y2 = y1 + cell_px - 1

                pos = (r, c)
                if pos == self.grid_model.start:
                    fill = "#10b981"
                elif pos == self.grid_model.goal:
                    fill = "#f43f5e"
                elif pos in path_set:
                    fill = "#22c55e"
                elif pos in explored_set:
                    fill = "#4f46e5"
                else:
                    cell_t = self.grid_model.get_cell(r, c)
                    fill = colors.get(CellType(cell_t), "#131b2e")

                draw.rectangle([x1, y1, x2, y2], fill=fill, outline="#1e293b")

        img.save(filepath)
        messagebox.showinfo("Export Successful", f"High-res PNG snapshot saved to:\n{filepath}")

    def save_grid_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Maze Grid Blueprint", "*.json")],
            initialfile="custom_maze.json"
        )
        if not filepath:
            return

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.grid_model.to_dict(), f, indent=2)

        messagebox.showinfo("Saved", f"Maze Blueprint saved successfully to:\n{filepath}")

    def load_grid_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Maze Grid Blueprint", "*.json")]
        )
        if not filepath:
            return

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded_grid = Grid.from_dict(data)
            self.grid_model.rows = loaded_grid.rows
            self.grid_model.cols = loaded_grid.cols
            self.grid_model.grid = loaded_grid.grid
            self.grid_model.start = loaded_grid.start
            self.grid_model.goal = loaded_grid.goal

            if hasattr(self.master, "on_grid_loaded"):
                self.master.on_grid_loaded()

            messagebox.showinfo("Loaded", "Maze Blueprint loaded successfully!")
            self.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load grid file:\n{str(e)}")
