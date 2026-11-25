import tkinter as tk
from tkinter import ttk
from theme import Theme
from custom_widgets import CircularProgress, BarChartWidget, CanvasRoundedFrame

class DashboardView(tk.Frame):
    """Analytics & Productivity Dashboard Frame with visual metrics and charts."""
    def __init__(self, parent, db_manager, **kwargs):
        super().__init__(parent, bg=Theme.current['bg_root'], **kwargs)
        self.db = db_manager
        self.bind("<Visibility>", lambda e: self.refresh())
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # Header
        f_header = tk.Frame(self, bg=Theme.current['bg_root'], padx=24, pady=16)
        f_header.pack(fill=tk.X)

        lbl_title = tk.Label(f_header, text="📊 Productivity Dashboard", bg=Theme.current['bg_root'],
                             fg=Theme.current['text_primary'], font=Theme.get_font(18, "bold"))
        lbl_title.pack(anchor="w")

        lbl_sub = tk.Label(f_header, text="Track your completion rates, weekly activity, and category distribution",
                           bg=Theme.current['bg_root'], fg=Theme.current['text_secondary'], font=Theme.get_font(10))
        lbl_sub.pack(anchor="w")

        # Scrollable Main Body
        canvas = tk.Canvas(self, bg=Theme.current['bg_root'], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=Theme.current['bg_root'], padx=24, pady=8)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Top Metric Cards Row (4 Stat Cards)
        self.f_cards_row = tk.Frame(self.scrollable_frame, bg=Theme.current['bg_root'])
        self.f_cards_row.pack(fill=tk.X, pady=(0, 20))

        # Charts Row (Progress Ring + Weekly Bar Chart)
        self.f_charts_row = tk.Frame(self.scrollable_frame, bg=Theme.current['bg_root'])
        self.f_charts_row.pack(fill=tk.X, pady=(0, 20))

        # Left Chart Container: Completion Ring Card
        self.card_ring = CanvasRoundedFrame(self.f_charts_row, radius=16, width=280, height=260)
        self.card_ring.pack(side=tk.LEFT, padx=(0, 16), fill=tk.BOTH)
        
        lbl_ring_title = tk.Label(self.card_ring, text="Overall Completion", bg=Theme.current['bg_card'],
                                  fg=Theme.current['text_primary'], font=Theme.get_font(12, "bold"))
        lbl_ring_title.place(x=20, y=16)

        self.progress_ring = CircularProgress(self.card_ring, size=150, thickness=14)
        self.progress_ring.place(x=65, y=60)

        # Right Chart Container: Weekly Activity Bar Chart
        self.card_chart = CanvasRoundedFrame(self.f_charts_row, radius=16, width=540, height=260)
        self.card_chart.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        lbl_chart_title = tk.Label(self.card_chart, text="Weekly Activity (Completed Tasks)",
                                   bg=Theme.current['bg_card'], fg=Theme.current['text_primary'],
                                   font=Theme.get_font(12, "bold"))
        lbl_chart_title.place(x=20, y=16)

        self.bar_chart = BarChartWidget(self.card_chart, height=180)
        self.bar_chart.place(x=20, y=55, width=500, height=180)

        # Categories Breakdown Section
        self.f_cat_section = tk.Frame(self.scrollable_frame, bg=Theme.current['bg_root'])
        self.f_cat_section.pack(fill=tk.X, pady=(0, 20))

    def refresh(self):
        stats = self.db.get_dashboard_stats()

        # Refresh Metric Cards
        for widget in self.f_cards_row.winfo_children():
            widget.destroy()

        card_metrics = [
            ("Total Tasks", str(stats['total_tasks']), "📝", Theme.current['info']),
            ("Completed", str(stats['completed_tasks']), "✅", Theme.current['success']),
            ("Pending", str(stats['pending_tasks']), "⏳", Theme.current['warning']),
            ("Overdue", str(stats['overdue_tasks']), "⚠️", Theme.current['danger']),
        ]

        for title, val, icon, color in card_metrics:
            card = CanvasRoundedFrame(self.f_cards_row, radius=12, width=190, height=90)
            card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

            lbl_ic = tk.Label(card, text=icon, bg=Theme.current['bg_card'], font=Theme.get_font(18))
            lbl_ic.place(x=16, y=16)

            lbl_v = tk.Label(card, text=val, bg=Theme.current['bg_card'], fg=color,
                             font=Theme.get_font(18, "bold"))
            lbl_v.place(x=60, y=14)

            lbl_t = tk.Label(card, text=title, bg=Theme.current['bg_card'], fg=Theme.current['text_secondary'],
                             font=Theme.get_font(9))
            lbl_t.place(x=60, y=48)

        # Refresh Circular Progress
        self.progress_ring.set_progress(stats['completion_rate'])

        # Refresh Bar Chart
        self.bar_chart.set_data(stats['weekly_activity'])

        # Refresh Categories Section
        for widget in self.f_cat_section.winfo_children():
            widget.destroy()

        lbl_cat_head = tk.Label(self.f_cat_section, text="Category Breakdown", bg=Theme.current['bg_root'],
                                fg=Theme.current['text_primary'], font=Theme.get_font(14, "bold"))
        lbl_cat_head.pack(anchor="w", pady=(0, 10))

        cat_card = CanvasRoundedFrame(self.f_cat_section, radius=16, width=820, height=120)
        cat_card.pack(fill=tk.X)

        if not stats['category_stats']:
            lbl_empty = tk.Label(cat_card, text="No categorized tasks available yet.",
                                 bg=Theme.current['bg_card'], fg=Theme.current['text_muted'],
                                 font=Theme.get_font(10, "italic"))
            lbl_empty.place(x=20, y=40)
        else:
            x_pos = 20
            for cs in stats['category_stats']:
                pill = tk.Frame(cat_card, bg=cs['color'], padx=12, pady=6)
                pill.place(x=x_pos, y=35)

                txt = f"{cs['name']}: {cs['count']} tasks"
                lbl_c = tk.Label(pill, text=txt, bg=cs['color'], fg="#FFFFFF", font=Theme.get_font(10, "bold"))
                lbl_c.pack()

                x_pos += 180
