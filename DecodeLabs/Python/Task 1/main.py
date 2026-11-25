import tkinter as tk
from tkinter import ttk, messagebox
import sys
import os
from datetime import date, datetime
from typing import Dict, Any, List, Optional

from database import DatabaseManager
from theme import Theme
from custom_widgets import CanvasRoundedFrame, BadgeLabel, ModernButton, AnimatedToast
from task_dialog import TaskDialog
from dashboard_view import DashboardView
from pomodoro_view import PomodoroView
from data_manager import DataManager

class TaskMasterApp(tk.Tk):
    """Main Application Window for Apex TaskMaster Pro."""
    def __init__(self):
        super().__init__()
        self.title("Apex TaskMaster Pro - Worldwide Ultimate To-Do List")
        self.geometry("1180x760")
        self.minsize(980, 640)

        # Database Engine
        self.db = DatabaseManager()
        self.data_mgr = DataManager(self.db)

        # Check if database is empty; if so, seed sample tasks
        if len(self.db.get_tasks(filter_status="All")) == 0:
            self.data_mgr.seed_sample_data()

        # State Variables
        self.current_filter_status = "Active"
        self.current_category_filter = None
        self.current_priority_filter = "All"
        self.current_sort_by = "due_date"
        self.search_query = ""

        # Configure root colors
        self.configure(bg=Theme.current['bg_root'])

        self._build_layout()
        self._bind_shortcuts()
        self.show_view("tasks")

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self.open_add_task_dialog())
        self.bind("<Control-f>", lambda e: self.ent_search.focus_set())
        self.bind("<Control-t>", lambda e: self.toggle_theme())

    def _build_layout(self):
        # Master Layout: Left Sidebar + Main Content Workspace
        self.main_container = tk.Frame(self, bg=Theme.current['bg_root'])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # ---------------- 1. LEFT NAVIGATION SIDEBAR ----------------
        self.f_sidebar = tk.Frame(self.main_container, bg=Theme.current['bg_sidebar'], width=240)
        self.f_sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.f_sidebar.pack_propagate(False)

        # App Logo & Branding
        f_brand = tk.Frame(self.f_sidebar, bg=Theme.current['bg_sidebar'], padx=18, pady=20)
        f_brand.pack(fill=tk.X)

        lbl_logo = tk.Label(f_brand, text="⚡ TaskMaster", bg=Theme.current['bg_sidebar'],
                             fg=Theme.current['accent_primary'], font=Theme.get_font(16, "bold"))
        lbl_logo.pack(anchor="w")

        lbl_edition = tk.Label(f_brand, text="PRO EDITION • SQLITE", bg=Theme.current['bg_sidebar'],
                               fg=Theme.current['text_muted'], font=Theme.get_font(8, "bold"))
        lbl_edition.pack(anchor="w")

        # Sidebar Nav Buttons
        self.f_nav = tk.Frame(self.f_sidebar, bg=Theme.current['bg_sidebar'], padx=12, pady=10)
        self.f_nav.pack(fill=tk.X)

        self.nav_buttons = {}
        nav_items = [
            ("tasks", "📋", "Tasks Workspace"),
            ("dashboard", "📊", "Analytics & Stats"),
            ("pomodoro", "⏱️", "Pomodoro Focus"),
        ]

        for key, icon, label in nav_items:
            btn = ModernButton(
                self.f_nav, text=label, icon=icon,
                command=lambda k=key: self.show_view(k),
                bg_color=Theme.current['bg_sidebar'],
                hover_color=Theme.current['bg_card_hover'],
                fg_color=Theme.current['text_primary'],
                font_size=10
            )
            btn.pack(fill=tk.X, pady=4)
            self.nav_buttons[key] = btn

        # Quick Add Button in Sidebar
        btn_quick_add = ModernButton(
            self.f_sidebar, text="Quick New Task", icon="➕",
            command=self.open_add_task_dialog,
            bg_color=Theme.current['accent_primary'],
            hover_color=Theme.current['accent_hover'],
            font_size=11
        )
        btn_quick_add.pack(fill=tk.X, padx=16, pady=16)

        # Sidebar Bottom Utility Tools (Theme Toggle, Export)
        f_bottom_tools = tk.Frame(self.f_sidebar, bg=Theme.current['bg_sidebar'], padx=16, pady=16)
        f_bottom_tools.pack(side=tk.BOTTOM, fill=tk.X)

        btn_export = ModernButton(
            f_bottom_tools, text="Export JSON/CSV", icon="📥",
            command=self._show_export_menu,
            bg_color=Theme.current['bg_card'],
            hover_color=Theme.current['bg_card_hover'],
            fg_color=Theme.current['text_primary'],
            font_size=9
        )
        btn_export.pack(fill=tk.X, pady=(0, 8))

        self.btn_theme = ModernButton(
            f_bottom_tools, text="Toggle Theme", icon="🌙" if Theme.is_dark else "☀️",
            command=self.toggle_theme,
            bg_color=Theme.current['bg_card'],
            hover_color=Theme.current['bg_card_hover'],
            fg_color=Theme.current['text_primary'],
            font_size=9
        )
        self.btn_theme.pack(fill=tk.X)

        # ---------------- 2. RIGHT WORKSPACE AREA ----------------
        self.f_workspace = tk.Frame(self.main_container, bg=Theme.current['bg_root'])
        self.f_workspace.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Top Header Search & Filter Bar
        self.f_topbar = tk.Frame(self.f_workspace, bg=Theme.current['bg_root'], padx=24, pady=16)
        self.f_topbar.pack(fill=tk.X)

        # Real-Time Search Box
        f_search = tk.Frame(self.f_topbar, bg=Theme.current['bg_card'], padx=10, pady=4)
        f_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 16))

        lbl_s_icon = tk.Label(f_search, text="🔍", bg=Theme.current['bg_card'], font=Theme.get_font(10))
        lbl_s_icon.pack(side=tk.LEFT)

        self.ent_search = tk.Entry(f_search, bg=Theme.current['bg_card'], fg=Theme.current['text_primary'],
                                   insertbackground=Theme.current['text_primary'], font=Theme.get_font(11), bd=0)
        self.ent_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)
        self.ent_search.bind("<KeyRelease>", self._on_search_changed)

        # View Frame Stack
        self.f_content = tk.Frame(self.f_workspace, bg=Theme.current['bg_root'])
        self.f_content.pack(fill=tk.BOTH, expand=True)

        # Views
        self.view_tasks = tk.Frame(self.f_content, bg=Theme.current['bg_root'])
        self.view_dashboard = DashboardView(self.f_content, self.db)
        self.view_pomodoro = PomodoroView(self.f_content, self.db)

        self._build_tasks_workspace()

    def _build_tasks_workspace(self):
        """Build the main Tasks List Workspace with status filters, sorting, and scrollable card stack."""
        # Filter Tabs Row
        f_filter_bar = tk.Frame(self.view_tasks, bg=Theme.current['bg_root'], padx=24, pady=4)
        f_filter_bar.pack(fill=tk.X)

        status_options = ["Active", "All", "Today", "Upcoming", "Overdue", "Completed", "Archived"]
        self.filter_buttons = {}

        for st in status_options:
            btn = tk.Button(
                f_filter_bar, text=st, command=lambda s=st: self.set_status_filter(s),
                bg=Theme.current['accent_primary'] if st == self.current_filter_status else Theme.current['bg_card'],
                fg="#FFFFFF" if st == self.current_filter_status else Theme.current['text_secondary'],
                font=Theme.get_font(9, "bold"), bd=0, padx=12, pady=5, cursor="hand2", activebackground=Theme.current['accent_hover']
            )
            btn.pack(side=tk.LEFT, padx=3)
            self.filter_buttons[st] = btn

        # Priority & Sort Control Frame
        f_controls = tk.Frame(self.view_tasks, bg=Theme.current['bg_root'], padx=24, pady=8)
        f_controls.pack(fill=tk.X)

        tk.Label(f_controls, text="Priority:", bg=Theme.current['bg_root'], fg=Theme.current['text_secondary'],
                 font=Theme.get_font(9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.cmb_priority_filter = ttk.Combobox(f_controls, values=["All", "Urgent", "High", "Medium", "Low"], width=10, state="readonly")
        self.cmb_priority_filter.set("All")
        self.cmb_priority_filter.pack(side=tk.LEFT, padx=(0, 16))
        self.cmb_priority_filter.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        tk.Label(f_controls, text="Sort By:", bg=Theme.current['bg_root'], fg=Theme.current['text_secondary'],
                 font=Theme.get_font(9, "bold")).pack(side=tk.LEFT, padx=(0, 4))
        self.cmb_sort = ttk.Combobox(f_controls, values=["Due Date", "Priority", "Title", "Created Date"], width=12, state="readonly")
        self.cmb_sort.set("Due Date")
        self.cmb_sort.pack(side=tk.LEFT)
        self.cmb_sort.bind("<<ComboboxSelected>>", lambda e: self._on_filter_changed())

        # Scrollable Task Cards Stack
        canvas = tk.Canvas(self.view_tasks, bg=Theme.current['bg_root'], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(self.view_tasks, orient="vertical", command=canvas.yview)
        self.f_task_list = tk.Frame(canvas, bg=Theme.current['bg_root'], padx=24, pady=8)

        self.f_task_list.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=self.f_task_list, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    def show_view(self, view_name: str):
        self.view_tasks.pack_forget()
        self.view_dashboard.pack_forget()
        self.view_pomodoro.pack_forget()

        # Update sidebar nav button highlights
        for key, btn in self.nav_buttons.items():
            if key == view_name:
                btn.config(bg=Theme.current['accent_primary'])
                btn.label.config(bg=Theme.current['accent_primary'])
            else:
                btn.config(bg=Theme.current['bg_sidebar'])
                btn.label.config(bg=Theme.current['bg_sidebar'])

        if view_name == "tasks":
            self.view_tasks.pack(fill=tk.BOTH, expand=True)
            self.refresh_tasks()
        elif view_name == "dashboard":
            self.view_dashboard.pack(fill=tk.BOTH, expand=True)
            self.view_dashboard.refresh()
        elif view_name == "pomodoro":
            self.view_pomodoro.pack(fill=tk.BOTH, expand=True)
            self.view_pomodoro.refresh_task_list()

    def set_status_filter(self, status: str):
        self.current_filter_status = status
        for st, btn in self.filter_buttons.items():
            if st == status:
                btn.config(bg=Theme.current['accent_primary'], fg="#FFFFFF")
            else:
                btn.config(bg=Theme.current['bg_card'], fg=Theme.current['text_secondary'])
        self.refresh_tasks()

    def _on_search_changed(self, event=None):
        self.search_query = self.ent_search.get().strip()
        self.refresh_tasks()

    def _on_filter_changed(self):
        self.current_priority_filter = self.cmb_priority_filter.get()
        sort_val = self.cmb_sort.get()
        sort_map = {"Due Date": "due_date", "Priority": "priority", "Title": "title", "Created Date": "created"}
        self.current_sort_by = sort_map.get(sort_val, "due_date")
        self.refresh_tasks()

    def refresh_tasks(self):
        # Clear existing cards
        for widget in self.f_task_list.winfo_children():
            widget.destroy()

        tasks = self.db.get_tasks(
            search_query=self.search_query,
            filter_status=self.current_filter_status,
            priority_filter=self.current_priority_filter,
            sort_by=self.current_sort_by
        )

        if not tasks:
            f_empty = tk.Frame(self.f_task_list, bg=Theme.current['bg_root'], pady=60)
            f_empty.pack(fill=tk.BOTH, expand=True)

            lbl_e_icon = tk.Label(f_empty, text="🎉", bg=Theme.current['bg_root'], font=Theme.get_font(36))
            lbl_e_icon.pack()

            lbl_e_txt = tk.Label(f_empty, text="No tasks found matching your filter criteria!",
                                 bg=Theme.current['bg_root'], fg=Theme.current['text_secondary'],
                                 font=Theme.get_font(12, "bold"))
            lbl_e_txt.pack(pady=8)
            return

        for task in tasks:
            self._render_task_card(task)

    def _render_task_card(self, task: Dict[str, Any]):
        card = CanvasRoundedFrame(self.f_task_list, radius=14, width=820, height=110)
        card.pack(fill=tk.X, pady=6)

        is_completed = (task['status'] == 'Completed')

        # Checkbox for Completion
        chk_state = tk.BooleanVar(value=is_completed)
        chk = tk.Checkbutton(
            card, variable=chk_state, bg=Theme.current['bg_card'],
            activebackground=Theme.current['bg_card'], selectcolor=Theme.current['bg_root'],
            command=lambda t=task, v=chk_state: self._toggle_task_completion(t, v.get())
        )
        chk.place(x=16, y=20)

        # Title Label (Strikethrough if completed)
        font_style = Theme.get_font(11, "bold")
        fg_title = Theme.current['text_muted'] if is_completed else Theme.current['text_primary']
        lbl_title = tk.Label(card, text=task['title'], bg=Theme.current['bg_card'], fg=fg_title, font=font_style)
        lbl_title.place(x=48, y=18)

        # Badges Row (Priority + Category)
        x_badge = 48
        # Priority Badge
        prio_color = Theme.get_priority_color(task['priority'])
        prio_badge = BadgeLabel(card, text=task['priority'].upper(), bg_color=prio_color)
        prio_badge.place(x=x_badge, y=48)
        x_badge += 85

        # Category Badge
        if task.get('category_name'):
            cat_bg = task.get('category_color', Theme.current['accent_primary'])
            cat_txt = f"{task.get('category_icon', '')} {task.get('category_name')}"
            cat_badge = BadgeLabel(card, text=cat_txt, bg_color=cat_bg)
            cat_badge.place(x=x_badge, y=48)
            x_badge += 130

        # Subtask Progress Text
        if task.get('total_subtasks', 0) > 0:
            st_text = f"Subtasks: {task['completed_subtasks']}/{task['total_subtasks']}"
            lbl_st = tk.Label(card, text=st_text, bg=Theme.current['bg_card'], fg=Theme.current['text_secondary'],
                              font=Theme.get_font(9, "bold"))
            lbl_st.place(x=x_badge, y=50)

        # Due Date Display
        if task.get('due_date'):
            due_str = f"📅 {task['due_date']} {task.get('due_time', '')}".strip()
            # Highlight if overdue
            today_str = date.today().strftime("%Y-%m-%d")
            fg_due = Theme.current['danger'] if (task['due_date'] < today_str and not is_completed) else Theme.current['text_secondary']

            lbl_due = tk.Label(card, text=due_str, bg=Theme.current['bg_card'], fg=fg_due, font=Theme.get_font(9))
            lbl_due.place(x=520, y=20)

        # Action Buttons (Edit, Delete)
        btn_edit = tk.Label(card, text="✏️", bg=Theme.current['bg_card'], cursor="hand2", font=Theme.get_font(12))
        btn_edit.place(x=740, y=18)
        btn_edit.bind("<Button-1>", lambda e, t=task: self.open_edit_task_dialog(t))

        btn_del = tk.Label(card, text="🗑️", bg=Theme.current['bg_card'], cursor="hand2", font=Theme.get_font(12))
        btn_del.place(x=770, y=18)
        btn_del.bind("<Button-1>", lambda e, tid=task['id']: self._delete_task(tid))

        # Subtasks Dropdown Toggle button if subtasks exist
        if task.get('subtask_list'):
            lbl_expand = tk.Label(card, text="▼ Subtasks Checklist", bg=Theme.current['bg_card'],
                                  fg=Theme.current['accent_primary'], cursor="hand2", font=Theme.get_font(9, "bold"))
            lbl_expand.place(x=48, y=78)
            lbl_expand.bind("<Button-1>", lambda e, t=task: self._open_subtasks_popup(t))

    def _toggle_task_completion(self, task: Dict[str, Any], is_completed: bool):
        new_status = 'Completed' if is_completed else 'Pending'
        self.db.set_task_status(task['id'], new_status)
        msg = f"Task '{task['title']}' marked as Completed!" if is_completed else f"Task '{task['title']}' reopened."
        AnimatedToast(self, msg, "success" if is_completed else "info")
        self.refresh_tasks()

    def _delete_task(self, task_id: int):
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this task?", parent=self):
            self.db.delete_task(task_id)
            AnimatedToast(self, "Task deleted successfully.", "warning")
            self.refresh_tasks()

    def _open_subtasks_popup(self, task: Dict[str, Any]):
        popup = tk.Toplevel(self)
        popup.title(f"Subtasks - {task['title']}")
        popup.geometry("420x350")
        popup.configure(bg=Theme.current['bg_root'])

        tk.Label(popup, text=f"Subtasks for: {task['title']}", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_primary'], font=Theme.get_font(11, "bold"), wraplength=380).pack(pady=12)

        for st in task.get('subtask_list', []):
            f_row = tk.Frame(popup, bg=Theme.current['bg_card'], padx=10, pady=6)
            f_row.pack(fill=tk.X, padx=16, pady=3)

            var = tk.BooleanVar(value=bool(st['is_completed']))
            cb = tk.Checkbutton(
                f_row, text=st['title'], variable=var, bg=Theme.current['bg_card'],
                fg=Theme.current['text_primary'], selectcolor=Theme.current['bg_root'],
                font=Theme.get_font(10),
                command=lambda st_id=st['id'], v=var: self.db.toggle_subtask(st_id, v.get())
            )
            cb.pack(side=tk.LEFT)

    def open_add_task_dialog(self):
        TaskDialog(self, self.db, on_save_callback=self.refresh_tasks)

    def open_edit_task_dialog(self, task: Dict[str, Any]):
        TaskDialog(self, self.db, task_data=task, on_save_callback=self.refresh_tasks)

    def _show_export_menu(self):
        top = tk.Toplevel(self)
        top.title("Export & Data Backup")
        top.geometry("320x180")
        top.configure(bg=Theme.current['bg_root'])

        tk.Label(top, text="Select Export Format", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_primary'], font=Theme.get_font(12, "bold")).pack(pady=16)

        ModernButton(top, text="Export as JSON", icon="📄", command=lambda: [top.destroy(), self.data_mgr.export_to_json()]).pack(fill=tk.X, padx=24, pady=4)
        ModernButton(top, text="Export as CSV", icon="📊", command=lambda: [top.destroy(), self.data_mgr.export_to_csv()]).pack(fill=tk.X, padx=24, pady=4)

    def toggle_theme(self):
        Theme.toggle_theme()
        self.configure(bg=Theme.current['bg_root'])
        self.btn_theme.label.config(text="🌙 Toggle Theme" if not Theme.is_dark else "☀️ Toggle Theme")

        # Re-build layout to apply new theme colors across all components
        for widget in self.winfo_children():
            widget.destroy()
        self._build_layout()
        self.show_view("tasks")
        AnimatedToast(self, "Theme switched successfully!", "info")

if __name__ == "__main__":
    app = TaskMasterApp()
    app.mainloop()
