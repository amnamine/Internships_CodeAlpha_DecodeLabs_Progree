"""
Custom High-Performance Tkinter Widgets Built on Canvas with Hover Effects & Smooth Animations
"""

import tkinter as tk
import math
from theme import GLOBAL_THEME

class CustomButton(tk.Canvas):
    """Modern rounded corner button with smooth hover and press animation."""
    def __init__(self, parent, text="", command=None, width=140, height=38, radius=8,
                 bg_color=None, hover_color=None, fg_color=None, font=("Segoe UI", 10, "bold"), icon=None):
        self.theme = GLOBAL_THEME.theme
        self.bg_color = bg_color or self.theme["accent_primary"]
        self.hover_color = hover_color or self.theme["accent_primary_hover"]
        self.fg_color = fg_color or "#FFFFFF"
        self.current_bg = self.bg_color
        
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.text = text
        self.command = command
        self.radius = radius
        self.w = width
        self.h = height
        self.font = font
        self.icon = icon

        GLOBAL_THEME.register_listener(self.on_theme_change)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_click)

        self.draw()

    def on_theme_change(self, theme):
        self.theme = theme
        self.configure(bg=self.master["bg"])
        self.draw()

    def draw(self):
        self.delete("all")
        # Draw rounded rectangle
        r = self.radius
        self.create_arc((0, 0, r*2, r*2), start=90, extent=90, fill=self.current_bg, outline="")
        self.create_arc((self.w-r*2, 0, self.w, r*2), start=0, extent=90, fill=self.current_bg, outline="")
        self.create_arc((0, self.h-r*2, r*2, self.h), start=180, extent=90, fill=self.current_bg, outline="")
        self.create_arc((self.w-r*2, self.h-r*2, self.w, self.h), start=270, extent=90, fill=self.current_bg, outline="")
        self.create_rectangle((r, 0, self.w-r, self.h), fill=self.current_bg, outline="")
        self.create_rectangle((0, r, self.w, self.h-r), fill=self.current_bg, outline="")

        full_text = f"{self.icon} {self.text}" if self.icon else self.text
        self.create_text(self.w/2, self.h/2, text=full_text, fill=self.fg_color, font=self.font)

    def _on_enter(self, event):
        self.current_bg = self.hover_color
        self.draw()

    def _on_leave(self, event):
        self.current_bg = self.bg_color
        self.draw()

    def _on_click(self, event):
        if self.command:
            self.command()


class CustomSlider(tk.Canvas):
    """Modern smooth draggable slider widget."""
    def __init__(self, parent, from_=4, to=64, initial=16, command=None, width=300, height=36):
        self.theme = GLOBAL_THEME.theme
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.from_ = from_
        self.to = to
        self.value = initial
        self.command = command
        self.w = width
        self.h = height
        self.padding = 15
        self.dragging = False

        GLOBAL_THEME.register_listener(self.on_theme_change)
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", self._on_release)

        self.draw()

    def on_theme_change(self, theme):
        self.theme = theme
        self.configure(bg=self.master["bg"])
        self.draw()

    def set_value(self, val):
        self.value = max(self.from_, min(self.to, int(val)))
        self.draw()
        if self.command:
            self.command(self.value)

    def _val_to_x(self):
        ratio = (self.value - self.from_) / (self.to - self.from_)
        return self.padding + ratio * (self.w - 2 * self.padding)

    def _x_to_val(self, x):
        x = max(self.padding, min(self.w - self.padding, x))
        ratio = (x - self.padding) / (self.w - 2 * self.padding)
        return int(round(self.from_ + ratio * (self.to - self.from_)))

    def draw(self):
        self.delete("all")
        cy = self.h / 2
        kx = self._val_to_x()

        # Track background
        self.create_line(self.padding, cy, self.w - self.padding, cy, fill=self.theme["border_color"], width=6, capstyle="round")
        # Filled track
        self.create_line(self.padding, cy, kx, cy, fill=self.theme["accent_primary"], width=6, capstyle="round")
        # Knob outer glow & knob
        self.create_oval(kx - 10, cy - 10, kx + 10, cy + 10, fill=self.theme["accent_primary"], outline=self.theme["fg_primary"], width=2)

    def _on_press(self, event):
        self.dragging = True
        self.set_value(self._x_to_val(event.x))

    def _on_drag(self, event):
        if self.dragging:
            self.set_value(self._x_to_val(event.x))

    def _on_release(self, event):
        self.dragging = False


class CustomToggleSwitch(tk.Canvas):
    """Animated iOS style modern toggle switch."""
    def __init__(self, parent, text="", initial=True, command=None, width=220, height=30):
        self.theme = GLOBAL_THEME.theme
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.text = text
        self.state = initial
        self.command = command
        self.w = width
        self.h = height
        self.sw_w = 46
        self.sw_h = 24

        GLOBAL_THEME.register_listener(self.on_theme_change)
        self.bind("<Button-1>", self._toggle)
        self.draw()

    def on_theme_change(self, theme):
        self.theme = theme
        self.configure(bg=self.master["bg"])
        self.draw()

    def _toggle(self, event):
        self.state = not self.state
        self.draw()
        if self.command:
            self.command(self.state)

    def set_state(self, state):
        self.state = state
        self.draw()

    def draw(self):
        self.delete("all")
        cy = self.h / 2
        bg_col = self.theme["accent_success"] if self.state else self.theme["border_color"]
        
        # Switch background rounded pill
        r = self.sw_h / 2
        sx0 = 0
        sy0 = cy - r
        sx1 = self.sw_w
        sy1 = cy + r

        self.create_arc((sx0, sy0, sx0 + self.sw_h, sy1), start=90, extent=180, fill=bg_col, outline="")
        self.create_arc((sx1 - self.sw_h, sy0, sx1, sy1), start=270, extent=180, fill=bg_col, outline="")
        self.create_rectangle((sx0 + r, sy0, sx1 - r, sy1), fill=bg_col, outline="")

        # Knob
        kx = sx1 - r - 2 if self.state else sx0 + r + 2
        self.create_oval(kx - (r - 3), cy - (r - 3), kx + (r - 3), cy + (r - 3), fill="#FFFFFF", outline="")

        # Text Label
        self.create_text(self.sw_w + 12, cy, text=self.text, anchor="w", fill=self.theme["fg_primary"], font=("Segoe UI", 10))


class StrengthMeterGauge(tk.Canvas):
    """Visual password strength gauge progress bar with animated transitions."""
    def __init__(self, parent, width=320, height=20):
        self.theme = GLOBAL_THEME.theme
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0)
        self.w = width
        self.h = height
        self.score = 0
        self.color_key = "strength_weak"

        GLOBAL_THEME.register_listener(self.on_theme_change)
        self.draw()

    def on_theme_change(self, theme):
        self.theme = theme
        self.configure(bg=self.master["bg"])
        self.draw()

    def update_gauge(self, score, color_key):
        self.score = max(0, min(100, score))
        self.color_key = color_key
        self.draw()

    def draw(self):
        self.delete("all")
        # Track
        r = self.h / 2
        self.create_rectangle(0, 0, self.w, self.h, fill=self.theme["bg_input"], outline=self.theme["border_color"], width=1)
        
        # Fill
        fill_w = (self.score / 100.0) * self.w
        if fill_w > 0:
            color = self.theme.get(self.color_key, self.theme["accent_primary"])
            self.create_rectangle(0, 0, fill_w, self.h, fill=color, outline="")


class ToastNotification(tk.Canvas):
    """Floating notification toast overlay."""
    def __init__(self, parent, text="Copied to clipboard!", width=220, height=36):
        self.theme = GLOBAL_THEME.theme
        super().__init__(parent, width=width, height=height, bg=self.theme["accent_success"], highlightthickness=0)
        self.w = width
        self.h = height
        self.create_text(width/2, height/2, text=f"✓ {text}", fill="#FFFFFF", font=("Segoe UI", 10, "bold"))
        self.place(relx=0.5, rely=0.08, anchor="n")
        self.after(2000, self.destroy)
