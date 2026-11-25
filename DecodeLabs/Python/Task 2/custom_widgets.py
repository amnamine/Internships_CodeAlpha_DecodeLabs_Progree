"""
custom_widgets.py - Rich Animated GUI Components for ApexExpense
Contains custom visual widgets built on customtkinter and tkinter canvas:
- Modern KPI Stat Card with hover effects
- Canvas Donut / Ring Category Chart
- Canvas Spending Trend Bar Chart
- Rounded Canvas Progress Bar
- Toast Notification Banner
"""

import tkinter as tk
import customtkinter as ctk
import math
from theme import THEME, FONTS

class ModernStatCard(ctk.CTkFrame):
    """Sleek KPI Stat card with colored left border indicator and hover highlight."""
    def __init__(self, parent, title, amount, subtext="", icon="💰", accent_color="#6366F1", **kwargs):
        super().__init__(
            parent,
            fg_color=THEME["bg_card"],
            corner_radius=14,
            border_width=1,
            border_color=THEME["border"],
            **kwargs
        )
        self.accent_color = accent_color
        
        # Left color bar
        self.accent_bar = ctk.CTkFrame(self, width=6, fg_color=accent_color, corner_radius=3)
        self.accent_bar.pack(side="left", fill="y", padx=(0, 10), pady=8)
        
        # Content Container
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True, padx=(5, 12), pady=12)
        
        # Header Row (Title + Icon)
        self.header_row = ctk.CTkFrame(self.content, fg_color="transparent")
        self.header_row.pack(fill="x")
        
        self.lbl_title = ctk.CTkLabel(
            self.header_row,
            text=title.upper(),
            font=("Segoe UI", 10, "bold"),
            text_color=THEME["text_secondary"]
        )
        self.lbl_title.pack(side="left")
        
        self.lbl_icon = ctk.CTkLabel(
            self.header_row,
            text=icon,
            font=("Segoe UI Emoji", 16)
        )
        self.lbl_icon.pack(side="right")
        
        # Amount Display
        self.lbl_amount = ctk.CTkLabel(
            self.content,
            text=amount,
            font=FONTS["number_large"],
            text_color=THEME["text_primary"]
        )
        self.lbl_amount.pack(anchor="w", pady=(4, 0))
        
        # Subtext
        if subtext:
            self.lbl_subtext = ctk.CTkLabel(
                self.content,
                text=subtext,
                font=FONTS["caption"],
                text_color=THEME["text_secondary"]
            )
            self.lbl_subtext.pack(anchor="w")

        # Hover Bindings
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        self.configure(fg_color=THEME["bg_card_hover"])

    def _on_leave(self, event=None):
        self.configure(fg_color=THEME["bg_card"])

    def update_amount(self, new_amount, subtext=None):
        self.lbl_amount.configure(text=new_amount)
        if subtext and hasattr(self, 'lbl_subtext'):
            self.lbl_subtext.configure(text=subtext)


class CanvasDonutChart(tk.Canvas):
    """Custom Tkinter Canvas ring chart for category spending breakdown."""
    def __init__(self, parent, width=280, height=240, bg_color=THEME["bg_card"], **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        self.width = width
        self.height = height
        self.bg_color = bg_color

    def render_chart(self, data, currency_symbol="$"):
        """
        data format: list of dicts [{'name': 'Food', 'amount': 150.0, 'color': '#EF4444'}]
        """
        self.delete("all")
        
        total = sum(item["amount"] for item in data)
        cx, cy = self.width / 2, self.height / 2
        r_outer = min(self.width, self.height) * 0.38
        r_inner = r_outer * 0.65
        
        if total <= 0 or not data:
            # Draw placeholder empty circle
            self.create_oval(
                cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                fill="", outline=THEME["border"], width=12
            )
            self.create_text(
                cx, cy,
                text="No Expenses\nRecorded",
                fill=THEME["text_secondary"],
                font=FONTS["caption"],
                justify="center"
            )
            return

        start_angle = 90
        for item in data:
            amount = item["amount"]
            if amount <= 0:
                continue
            extent = (amount / total) * 360
            
            # Arc slice
            self.create_arc(
                cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer,
                start=start_angle, extent=-extent,
                fill=item["color"], outline=self.bg_color, width=2, style=tk.PIESLICE
            )
            start_angle -= extent

        # Center cutout circle for donut effect
        self.create_oval(
            cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner,
            fill=self.bg_color, outline=""
        )
        
        # Center Summary text
        self.create_text(
            cx, cy - 8,
            text="TOTAL SPENT",
            fill=THEME["text_secondary"],
            font=("Segoe UI", 8, "bold")
        )
        self.create_text(
            cx, cy + 10,
            text=f"{currency_symbol}{total:,.2f}",
            fill=THEME["text_primary"],
            font=("Segoe UI", 12, "bold")
        )


class CanvasBarChart(tk.Canvas):
    """Custom vector bar chart for daily or weekly spending trends."""
    def __init__(self, parent, width=420, height=220, bg_color=THEME["bg_card"], **kwargs):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_color,
            highlightthickness=0,
            **kwargs
        )
        self.width = width
        self.height = height
        self.bg_color = bg_color

    def render_chart(self, trend_data, currency_symbol="$"):
        """
        trend_data: list of dicts [{'date': '2026-08-01', 'amount': 45.0}]
        """
        self.delete("all")
        if not trend_data:
            return

        padding_x = 40
        padding_y = 30
        graph_w = self.width - (2 * padding_x)
        graph_h = self.height - (2 * padding_y)
        
        max_amount = max([item["amount"] for item in trend_data] + [1.0])
        n_bars = len(trend_data)
        bar_width = min(24, max(8, (graph_w / n_bars) - 6))

        # Baseline horizontal grid line
        y_base = self.height - padding_y
        self.create_line(
            padding_x, y_base, self.width - padding_x, y_base,
            fill=THEME["border"], width=1
        )
        
        # Render Bars
        for i, item in enumerate(trend_data):
            amt = item["amount"]
            ratio = amt / max_amount if max_amount > 0 else 0
            h = ratio * (graph_h - 10)
            
            cx = padding_x + (i + 0.5) * (graph_w / n_bars)
            x0 = cx - (bar_width / 2)
            x1 = cx + (bar_width / 2)
            y0 = y_base - h
            y1 = y_base
            
            # Color gradient simulation
            color = THEME["accent_primary"] if amt > 0 else THEME["border"]
            if amt > 0:
                self.create_rectangle(
                    x0, y0, x1, y1,
                    fill=color, outline="", width=0
                )
            
            # Date label (short day name or day number)
            day_str = item["date"].split("-")[-1]
            self.create_text(
                cx, y_base + 14,
                text=day_str,
                fill=THEME["text_secondary"],
                font=("Segoe UI", 8)
            )


class RoundedProgressBar(ctk.CTkProgressBar):
    """Enhanced progress bar with dynamic color transitions based on percentage."""
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            height=10,
            corner_radius=5,
            progress_color=THEME["accent_success"],
            fg_color=THEME["border"],
            **kwargs
        )
        
    def set_progress(self, current, max_val):
        if max_val <= 0:
            pct = 0.0
        else:
            pct = min(1.0, current / max_val)
            
        # Color coding
        if pct > 0.90:
            color = THEME["accent_danger"]
        elif pct > 0.70:
            color = THEME["accent_warning"]
        else:
            color = THEME["accent_success"]
            
        self.configure(progress_color=color)
        self.set(pct)


class ToastNotification(ctk.CTkFrame):
    """Floating notification toast pop-up."""
    def __init__(self, parent, message, icon="✅", is_error=False):
        accent = THEME["accent_danger"] if is_error else THEME["accent_success"]
        super().__init__(
            parent,
            fg_color=THEME["bg_card"],
            border_width=2,
            border_color=accent,
            corner_radius=10
        )
        
        lbl_icon = ctk.CTkLabel(self, text=icon, font=("Segoe UI Emoji", 14))
        lbl_icon.pack(side="left", padx=(12, 6), pady=8)
        
        lbl_msg = ctk.CTkLabel(
            self,
            text=message,
            font=FONTS["body_bold"],
            text_color=THEME["text_primary"]
        )
        lbl_msg.pack(side="left", padx=(0, 16), pady=8)
        
        # Place floating banner top right
        self.place(relx=0.98, rely=0.04, anchor="ne")
        self.after(3000, self.destroy)
