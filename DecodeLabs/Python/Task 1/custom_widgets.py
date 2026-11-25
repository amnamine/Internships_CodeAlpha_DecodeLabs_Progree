import tkinter as tk
from tkinter import ttk
import math
from theme import Theme

class CanvasRoundedFrame(tk.Canvas):
    """Custom Canvas widget that draws smooth rounded rectangle cards with hover elevation."""
    def __init__(self, parent, radius=16, bg_color=None, border_color=None,
                 hover_bg=None, command=None, **kwargs):
        super().__init__(parent, highlightthickness=0, bd=0, **kwargs)
        self.radius = radius
        self.bg_color = bg_color or Theme.current['bg_card']
        self.border_color = border_color or Theme.current['border']
        self.hover_bg = hover_bg or Theme.current['bg_card_hover']
        self.command = command
        self.is_hovered = False

        self.bind("<Configure>", self._draw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        if self.command:
            self.bind("<Button-1>", lambda e: self.command())
            self.config(cursor="hand2")

    def set_colors(self, bg_color, border_color=None, hover_bg=None):
        self.bg_color = bg_color
        if border_color:
            self.border_color = border_color
        if hover_bg:
            self.hover_bg = hover_bg
        self._draw()

    def _on_enter(self, event):
        self.is_hovered = True
        self._draw()

    def _on_leave(self, event):
        self.is_hovered = False
        self._draw()

    def _draw(self, event=None):
        self.delete("card_bg")
        w = self.winfo_width()
        h = self.winfo_height()

        if w <= 1 or h <= 1:
            return

        r = min(self.radius, w // 2, h // 2)
        fill = self.hover_bg if self.is_hovered and self.command else self.bg_color

        # Draw rounded rectangle using arcs and polygons
        self.create_arc(0, 0, 2*r, 2*r, start=90, extent=90, fill=fill, outline=fill, tags="card_bg")
        self.create_arc(w-2*r, 0, w, 2*r, start=0, extent=90, fill=fill, outline=fill, tags="card_bg")
        self.create_arc(w-2*r, h-2*r, w, h, start=270, extent=90, fill=fill, outline=fill, tags="card_bg")
        self.create_arc(0, h-2*r, 2*r, h, start=180, extent=90, fill=fill, outline=fill, tags="card_bg")

        self.create_rectangle(r, 0, w-r, h, fill=fill, outline=fill, tags="card_bg")
        self.create_rectangle(0, r, w, h-r, fill=fill, outline=fill, tags="card_bg")

        # Smooth border line
        if self.border_color:
            self.create_line(r, 0, w-r, 0, fill=self.border_color, tags="card_bg")
            self.create_line(r, h, w-r, h, fill=self.border_color, tags="card_bg")
            self.create_line(0, r, 0, h-r, fill=self.border_color, tags="card_bg")
            self.create_line(w, r, w, h-r, fill=self.border_color, tags="card_bg")


class CircularProgress(tk.Canvas):
    """Canvas widget for displaying animated circular progress percentage."""
    def __init__(self, parent, size=120, thickness=12, progress_color=None, bg_color=None, **kwargs):
        super().__init__(parent, width=size, height=size, highlightthickness=0, bg=parent.cget('bg'), **kwargs)
        self.size = size
        self.thickness = thickness
        self.progress_color = progress_color or Theme.current['accent_primary']
        self.track_color = bg_color or Theme.current['border']
        self.percentage = 0
        self._draw()

    def set_progress(self, percentage: float, text: str = None):
        self.percentage = max(0, min(100, percentage))
        self._draw(text)

    def _draw(self, display_text=None):
        self.delete("all")
        bg_parent = self.master.cget('bg')
        self.config(bg=bg_parent)

        margin = self.thickness / 2 + 2
        x0 = margin
        y0 = margin
        x1 = self.size - margin
        y1 = self.size - margin

        # Track Circle
        self.create_arc(x0, y0, x1, y1, start=0, extent=359.9,
                         style="arc", width=self.thickness, outline=self.track_color)

        # Active Arc
        extent = -(self.percentage / 100.0) * 360.0
        if self.percentage > 0:
            self.create_arc(x0, y0, x1, y1, start=90, extent=extent,
                             style="arc", width=self.thickness, outline=self.progress_color)

        # Center Text
        txt = display_text if display_text is not None else f"{int(self.percentage)}%"
        self.create_text(self.size/2, self.size/2, text=txt,
                         fill=Theme.current['text_primary'],
                         font=Theme.get_font(13, "bold"))


class BarChartWidget(tk.Canvas):
    """Canvas widget for drawing interactive weekly activity bar charts."""
    def __init__(self, parent, height=160, **kwargs):
        super().__init__(parent, height=height, highlightthickness=0, bd=0, **kwargs)
        self.data = []
        self.bind("<Configure>", lambda e: self._draw())

    def set_data(self, data):
        """Data format: [{'day_name': 'Mon', 'count': 4}, ...]"""
        self.data = data
        self._draw()

    def _draw(self):
        self.delete("all")
        w = self.winfo_width()
        h = self.winfo_height()
        if w <= 10 or h <= 10 or not self.data:
            return

        self.config(bg=Theme.current['bg_card'])

        max_val = max([item['count'] for item in self.data] + [5])
        padding_x = 40
        padding_y = 30
        chart_w = w - (2 * padding_x)
        chart_h = h - (2 * padding_y)

        num_bars = len(self.data)
        bar_width = min(36, (chart_w / num_bars) - 12)

        for i, item in enumerate(self.data):
            x_center = padding_x + (i + 0.5) * (chart_w / num_bars)
            x0 = x_center - (bar_width / 2)
            x1 = x_center + (bar_width / 2)

            bar_h = (item['count'] / max_val) * chart_h
            y1 = h - padding_y
            y0 = y1 - bar_h

            color = Theme.current['accent_primary'] if item['count'] > 0 else Theme.current['border']

            # Draw bar
            self.create_rectangle(x0, y0, x1, y1, fill=color, outline="", tags="bar")
            
            # Value label above bar
            if item['count'] > 0:
                self.create_text(x_center, y0 - 10, text=str(item['count']),
                                 fill=Theme.current['text_primary'],
                                 font=Theme.get_font(9, "bold"))

            # Day label below bar
            self.create_text(x_center, y1 + 14, text=item['day_name'],
                             fill=Theme.current['text_secondary'],
                             font=Theme.get_font(9))


class AnimatedToast(tk.Frame):
    """Floating notification toast banner with visual timing."""
    def __init__(self, root, message: str, toast_type: str = "info", duration_ms: int = 3000):
        color_map = {
            'info': Theme.current['info'],
            'success': Theme.current['success'],
            'warning': Theme.current['warning'],
            'danger': Theme.current['danger']
        }
        bg = color_map.get(toast_type, Theme.current['info'])

        super().__init__(root, bg=bg, padx=16, pady=10)
        self.root = root

        icon_map = {'info': 'ℹ️', 'success': '✅', 'warning': '⚠️', 'danger': '❌'}
        icon = icon_map.get(toast_type, '🔔')

        lbl = tk.Label(self, text=f"{icon}  {message}", bg=bg, fg="#FFFFFF",
                       font=Theme.get_font(10, "bold"))
        lbl.pack()

        # Place toast at bottom right
        self.place(relx=0.98, rely=0.95, anchor="se")
        self.lift()

        self.after(duration_ms, self.destroy)


class BadgeLabel(tk.Frame):
    """Modern pill badge with custom rounded background color."""
    def __init__(self, parent, text: str, bg_color: str, fg_color: str = "#FFFFFF", **kwargs):
        super().__init__(parent, bg=bg_color, padx=8, pady=2, **kwargs)
        self.lbl = tk.Label(self, text=text, bg=bg_color, fg=fg_color,
                            font=Theme.get_font(8, "bold"))
        self.lbl.pack()


class ModernButton(tk.Frame):
    """Custom styled button frame with hover and active states."""
    def __init__(self, parent, text: str, command=None, icon: str = "",
                 bg_color=None, hover_color=None, fg_color="#FFFFFF", font_size=10, **kwargs):
        bg = bg_color or Theme.current['accent_primary']
        super().__init__(parent, bg=bg, cursor="hand2", padx=14, pady=8, **kwargs)

        self.normal_bg = bg
        self.hover_bg = hover_color or Theme.current['accent_hover']
        self.command = command

        display_text = f"{icon}  {text}" if icon else text
        self.label = tk.Label(self, text=display_text, bg=bg, fg=fg_color,
                              font=Theme.get_font(font_size, "bold"))
        self.label.pack()

        for widget in (self, self.label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            if command:
                widget.bind("<Button-1>", lambda e: self.command())

    def _on_enter(self, event):
        self.config(bg=self.hover_bg)
        self.label.config(bg=self.hover_bg)

    def _on_leave(self, event):
        self.config(bg=self.normal_bg)
        self.label.config(bg=self.normal_bg)
