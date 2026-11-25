import tkinter as tk
from tkinter import ttk
import math
from theme import Theme
from custom_widgets import ModernButton, CanvasRoundedFrame, AnimatedToast

class PomodoroView(tk.Frame):
    """Integrated Pomodoro Focus Timer View linked with tasks and session history."""
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, bg=Theme.current['bg_root'], **kwargs)
        self.db = db_manager

        self.work_time_sec = 25 * 60
        self.short_break_sec = 5 * 60
        self.long_break_sec = 15 * 60

        self.current_time_sec = self.work_time_sec
        self.mode = "Work" # "Work", "Short Break", "Long Break"
        self.is_running = False
        self.timer_job = None
        self.completed_sessions = 0

        self._build_ui()
        self.refresh_task_list()

    def _build_ui(self):
        # Header
        f_header = tk.Frame(self, bg=Theme.current['bg_root'], padx=24, pady=16)
        f_header.pack(fill=tk.X)

        lbl_title = tk.Label(f_header, text="⏱️ Pomodoro Focus Timer", bg=Theme.current['bg_root'],
                             fg=Theme.current['text_primary'], font=Theme.get_font(18, "bold"))
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(f_header, text="Boost deep work productivity with timed focus sessions and short breaks",
                           bg=Theme.current['bg_root'], fg=Theme.current['text_secondary'], font=Theme.get_font(10))
        lbl_sub.pack(anchor="w")

        # Main Container
        f_main = tk.Frame(self, bg=Theme.current['bg_root'], padx=24, pady=10)
        f_main.pack(fill=tk.BOTH, expand=True)

        # Mode Selection Segment Buttons
        f_modes = tk.Frame(f_main, bg=Theme.current['bg_root'])
        f_modes.pack(pady=(0, 20))

        self.btn_mode_work = ModernButton(f_modes, text="Focus Work (25m)", command=lambda: self.switch_mode("Work"),
                                         bg_color=Theme.current['accent_primary'])
        self.btn_mode_work.pack(side=tk.LEFT, padx=6)

        self.btn_mode_short = ModernButton(f_modes, text="Short Break (5m)", command=lambda: self.switch_mode("Short Break"),
                                          bg_color=Theme.current['bg_card'], hover_color=Theme.current['bg_card_hover'],
                                          fg_color=Theme.current['text_primary'])
        self.btn_mode_short.pack(side=tk.LEFT, padx=6)

        self.btn_mode_long = ModernButton(f_modes, text="Long Break (15m)", command=lambda: self.switch_mode("Long Break"),
                                         bg_color=Theme.current['bg_card'], hover_color=Theme.current['bg_card_hover'],
                                         fg_color=Theme.current['text_primary'])
        self.btn_mode_long.pack(side=tk.LEFT, padx=6)

        # Timer Card Canvas
        self.timer_card = CanvasRoundedFrame(f_main, radius=20, width=340, height=320)
        self.timer_card.pack(pady=(0, 20))

        # Circular Timer Canvas
        self.timer_canvas = tk.Canvas(self.timer_card, width=240, height=240, highlightthickness=0,
                                      bg=Theme.current['bg_card'])
        self.timer_canvas.place(x=50, y=40)

        # Task Selection Dropdown Frame
        f_task_select = tk.Frame(f_main, bg=Theme.current['bg_root'])
        f_task_select.pack(pady=(0, 20))

        tk.Label(f_task_select, text="Link Session to Task:", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(side=tk.LEFT, padx=(0, 8))

        self.cmb_tasks = ttk.Combobox(f_task_select, width=35, state="readonly")
        self.cmb_tasks.pack(side=tk.LEFT)

        # Control Buttons (Play/Pause, Reset)
        f_controls = tk.Frame(f_main, bg=Theme.current['bg_root'])
        f_controls.pack()

        self.btn_toggle = ModernButton(f_controls, text="Start Focus", command=self.toggle_timer,
                                       icon="▶️", bg_color=Theme.current['success'], font_size=12)
        self.btn_toggle.pack(side=tk.LEFT, padx=10)

        self.btn_reset = ModernButton(f_controls, text="Reset", command=self.reset_timer,
                                      icon="🔄", bg_color=Theme.current['bg_card'],
                                      hover_color=Theme.current['bg_card_hover'],
                                      fg_color=Theme.current['text_primary'], font_size=12)
        self.btn_reset.pack(side=tk.LEFT, padx=10)

        # Sessions Counter Label
        self.lbl_sessions = tk.Label(f_main, text="Completed Sessions Today: 0 🍅",
                                     bg=Theme.current['bg_root'], fg=Theme.current['text_primary'],
                                     font=Theme.get_font(12, "bold"))
        self.lbl_sessions.pack(pady=(20, 0))

        self._draw_timer()

    def refresh_task_list(self):
        active_tasks = self.db.get_tasks(filter_status="Active")
        self.task_mapping = {}
        values = ["None (General Focus)"]
        for t in active_tasks:
            display = f"#{t['id']} - {t['title']}"
            values.append(display)
            self.task_mapping[display] = t['id']

        self.cmb_tasks['values'] = values
        if values:
            self.cmb_tasks.set(values[0])

    def switch_mode(self, mode: str):
        if self.is_running:
            self.pause_timer()

        self.mode = mode
        if mode == "Work":
            self.current_time_sec = self.work_time_sec
        elif mode == "Short Break":
            self.current_time_sec = self.short_break_sec
        else:
            self.current_time_sec = self.long_break_sec

        self._draw_timer()

    def toggle_timer(self):
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.is_running = True
        self.btn_toggle.label.config(text="⏸️  Pause")
        self.btn_toggle.normal_bg = Theme.current['warning']
        self.btn_toggle.config(bg=Theme.current['warning'])
        self._tick()

    def pause_timer(self):
        self.is_running = False
        if self.timer_job:
            self.after_cancel(self.timer_job)
            self.timer_job = None
        self.btn_toggle.label.config(text="▶️  Resume")
        self.btn_toggle.normal_bg = Theme.current['success']
        self.btn_toggle.config(bg=Theme.current['success'])

    def reset_timer(self):
        self.pause_timer()
        self.switch_mode(self.mode)
        self.btn_toggle.label.config(text="▶️  Start Focus")

    def _tick(self):
        if not self.is_running:
            return

        if self.current_time_sec > 0:
            self.current_time_sec -= 1
            self._draw_timer()
            self.timer_job = self.after(1000, self._tick)
        else:
            self._on_timer_complete()

    def _on_timer_complete(self):
        self.pause_timer()
        if self.mode == "Work":
            self.completed_sessions += 1
            self.lbl_sessions.config(text=f"Completed Sessions Today: {self.completed_sessions} 🍅")

            # Log pomodoro to DB if linked to task
            selected = self.cmb_tasks.get()
            task_id = self.task_mapping.get(selected) if selected in self.task_mapping else None
            self.db.log_pomodoro_session(task_id=task_id, duration=25)

            AnimatedToast(self.winfo_toplevel(), "Great job! Focus session completed! Take a break.", "success")
            self.switch_mode("Short Break")
        else:
            AnimatedToast(self.winfo_toplevel(), "Break over! Ready to focus again?", "info")
            self.switch_mode("Work")

    def _draw_timer(self):
        self.timer_canvas.delete("all")
        bg_card = Theme.current['bg_card']
        self.timer_canvas.config(bg=bg_card)

        mins = self.current_time_sec // 60
        secs = self.current_time_sec % 60
        time_str = f"{mins:02d}:{secs:02d}"

        total_sec = self.work_time_sec if self.mode == "Work" else (self.short_break_sec if self.mode == "Short Break" else self.long_break_sec)
        pct = self.current_time_sec / total_sec

        margin = 14
        x0, y0, x1, y1 = margin, margin, 240-margin, 240-margin

        # Background circle track
        self.timer_canvas.create_arc(x0, y0, x1, y1, start=0, extent=359.9,
                                     style="arc", width=12, outline=Theme.current['border'])

        # Progress Arc
        extent = pct * 360.0
        arc_color = Theme.current['accent_primary'] if self.mode == "Work" else Theme.current['success']
        if extent > 0:
            self.timer_canvas.create_arc(x0, y0, x1, y1, start=90, extent=extent,
                                         style="arc", width=12, outline=arc_color)

        # Center Time Text
        self.timer_canvas.create_text(120, 105, text=time_str, fill=Theme.current['text_primary'],
                                      font=Theme.get_font(28, "bold"))
        self.timer_canvas.create_text(120, 145, text=self.mode.upper(), fill=Theme.current['text_secondary'],
                                      font=Theme.get_font(10, "bold"))
