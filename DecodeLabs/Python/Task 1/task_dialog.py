import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime
from typing import Optional, Dict, Any, List
from theme import Theme
from custom_widgets import ModernButton

class TaskDialog(tk.Toplevel):
    """Modal dialog for creating and editing tasks with full attribute controls."""
    def __init__(self, parent, db_manager, task_data: Optional[Dict[str, Any]] = None, on_save_callback=None):
        super().__init__(parent)
        self.db = db_manager
        self.task_data = task_data
        self.on_save_callback = on_save_callback

        self.title("Edit Task" if task_data else "Create New Task")
        self.geometry("560x680")
        self.resizable(False, False)
        self.configure(bg=Theme.current['bg_root'])

        # Make modal
        self.transient(parent)
        self.grab_set()

        self.categories = self.db.get_all_categories()
        self.all_tags = self.db.get_all_tags()
        self.subtasks_temp = []

        if self.task_data and 'subtask_list' in self.task_data:
            self.subtasks_temp = [st['title'] for st in self.task_data['subtask_list']]

        self._build_ui()
        if self.task_data:
            self._load_task_data()

    def _build_ui(self):
        main_frame = tk.Frame(self, bg=Theme.current['bg_root'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Title
        title_txt = "✏️ Edit Task Details" if self.task_data else "✨ Add New Task"
        lbl_header = tk.Label(main_frame, text=title_txt, bg=Theme.current['bg_root'],
                              fg=Theme.current['text_primary'], font=Theme.get_font(16, "bold"))
        lbl_header.pack(anchor="w", pady=(0, 16))

        # Canvas Scrollable Body Container
        canvas = tk.Canvas(main_frame, bg=Theme.current['bg_root'], highlightthickness=0, bd=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=Theme.current['bg_root'])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw", width=500)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 1. Task Title Input
        tk.Label(scrollable_frame, text="Task Title *", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(4, 2))
        self.ent_title = tk.Entry(scrollable_frame, bg=Theme.current['bg_card'],
                                  fg=Theme.current['text_primary'], insertbackground=Theme.current['text_primary'],
                                  font=Theme.get_font(11), bd=1, relief="solid")
        self.ent_title.pack(fill=tk.X, ipady=6, pady=(0, 12))

        # 2. Priority & Category (Row)
        row_pc = tk.Frame(scrollable_frame, bg=Theme.current['bg_root'])
        row_pc.pack(fill=tk.X, pady=(0, 12))

        # Priority
        f_prio = tk.Frame(row_pc, bg=Theme.current['bg_root'])
        f_prio.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(f_prio, text="Priority", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(0, 2))
        self.cmb_priority = ttk.Combobox(f_prio, values=["Urgent", "High", "Medium", "Low"], state="readonly")
        self.cmb_priority.set("Medium")
        self.cmb_priority.pack(fill=tk.X, ipady=4)

        # Category
        f_cat = tk.Frame(row_pc, bg=Theme.current['bg_root'])
        f_cat.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(f_cat, text="Category", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(0, 2))
        cat_names = [f"{c['icon']} {c['name']}" for c in self.categories]
        self.cmb_category = ttk.Combobox(f_cat, values=cat_names, state="readonly")
        if cat_names:
            self.cmb_category.set(cat_names[0])
        self.cmb_category.pack(fill=tk.X, ipady=4)

        # 3. Due Date & Due Time (Row)
        row_dt = tk.Frame(scrollable_frame, bg=Theme.current['bg_root'])
        row_dt.pack(fill=tk.X, pady=(0, 12))

        f_date = tk.Frame(row_dt, bg=Theme.current['bg_root'])
        f_date.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(f_date, text="Due Date (YYYY-MM-DD)", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(0, 2))
        self.ent_due_date = tk.Entry(f_date, bg=Theme.current['bg_card'], fg=Theme.current['text_primary'],
                                     insertbackground=Theme.current['text_primary'], font=Theme.get_font(10), bd=1, relief="solid")
        self.ent_due_date.insert(0, date.today().strftime("%Y-%m-%d"))
        self.ent_due_date.pack(fill=tk.X, ipady=4)

        f_time = tk.Frame(row_dt, bg=Theme.current['bg_root'])
        f_time.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(f_time, text="Due Time (HH:MM)", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(0, 2))
        self.ent_due_time = tk.Entry(f_time, bg=Theme.current['bg_card'], fg=Theme.current['text_primary'],
                                     insertbackground=Theme.current['text_primary'], font=Theme.get_font(10), bd=1, relief="solid")
        self.ent_due_time.insert(0, "18:00")
        self.ent_due_time.pack(fill=tk.X, ipady=4)

        # 4. Notes Input
        tk.Label(scrollable_frame, text="Notes & Description", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(4, 2))
        self.txt_notes = tk.Text(scrollable_frame, height=4, bg=Theme.current['bg_card'],
                                 fg=Theme.current['text_primary'], insertbackground=Theme.current['text_primary'],
                                 font=Theme.get_font(10), bd=1, relief="solid")
        self.txt_notes.pack(fill=tk.X, pady=(0, 12))

        # 5. Subtasks Builder Frame
        tk.Label(scrollable_frame, text="Subtasks Checklist", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(4, 2))

        f_sub_input = tk.Frame(scrollable_frame, bg=Theme.current['bg_root'])
        f_sub_input.pack(fill=tk.X, pady=(0, 6))

        self.ent_subtask = tk.Entry(f_sub_input, bg=Theme.current['bg_card'], fg=Theme.current['text_primary'],
                                    insertbackground=Theme.current['text_primary'], font=Theme.get_font(10), bd=1, relief="solid")
        self.ent_subtask.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=4, padx=(0, 6))
        self.ent_subtask.bind("<Return>", lambda e: self._add_subtask())

        btn_add_sub = ModernButton(f_sub_input, text="Add", command=self._add_subtask, font_size=9)
        btn_add_sub.pack(side=tk.RIGHT)

        self.subtasks_container = tk.Frame(scrollable_frame, bg=Theme.current['bg_root'])
        self.subtasks_container.pack(fill=tk.X, pady=(0, 12))
        self._render_subtasks_list()

        # 6. Tags Selector
        tk.Label(scrollable_frame, text="Tags", bg=Theme.current['bg_root'],
                 fg=Theme.current['text_secondary'], font=Theme.get_font(10, "bold")).pack(anchor="w", pady=(4, 2))
        
        self.tag_vars = {}
        f_tags = tk.Frame(scrollable_frame, bg=Theme.current['bg_root'])
        f_tags.pack(fill=tk.X, pady=(0, 16))

        for tag in self.all_tags:
            var = tk.BooleanVar(value=False)
            self.tag_vars[tag['id']] = var
            cb = tk.Checkbutton(f_tags, text=tag['name'], variable=var, bg=Theme.current['bg_root'],
                                fg=Theme.current['text_primary'], selectcolor=Theme.current['bg_card'],
                                activebackground=Theme.current['bg_root'], font=Theme.get_font(9))
            cb.pack(side=tk.LEFT, padx=(0, 8))

        # Bottom Actions Frame
        f_actions = tk.Frame(scrollable_frame, bg=Theme.current['bg_root'])
        f_actions.pack(fill=tk.X, pady=(16, 0))

        btn_cancel = ModernButton(f_actions, text="Cancel", command=self.destroy,
                                  bg_color=Theme.current['bg_card'], hover_color=Theme.current['bg_card_hover'],
                                  fg_color=Theme.current['text_primary'])
        btn_cancel.pack(side=tk.LEFT)

        btn_save = ModernButton(f_actions, text="Save Task", command=self._save,
                                bg_color=Theme.current['accent_primary'], hover_color=Theme.current['accent_hover'])
        btn_save.pack(side=tk.RIGHT)

    def _add_subtask(self):
        val = self.ent_subtask.get().strip()
        if val:
            self.subtasks_temp.append(val)
            self.ent_subtask.delete(0, tk.END)
            self._render_subtasks_list()

    def _remove_subtask(self, idx):
        if 0 <= idx < len(self.subtasks_temp):
            self.subtasks_temp.pop(idx)
            self.subtasks_temp = list(self.subtasks_temp)
            self._render_subtasks_list()

    def _render_subtasks_list(self):
        for widget in self.subtasks_container.winfo_children():
            widget.destroy()

        for idx, st_title in enumerate(self.subtasks_temp):
            row = tk.Frame(self.subtasks_container, bg=Theme.current['bg_card'], padx=8, pady=4)
            row.pack(fill=tk.X, pady=2)

            lbl = tk.Label(row, text=f"• {st_title}", bg=Theme.current['bg_card'],
                           fg=Theme.current['text_primary'], font=Theme.get_font(9))
            lbl.pack(side=tk.LEFT)

            btn_del = tk.Label(row, text="❌", bg=Theme.current['bg_card'], fg=Theme.current['danger'],
                               cursor="hand2", font=Theme.get_font(8))
            btn_del.pack(side=tk.RIGHT)
            btn_del.bind("<Button-1>", lambda e, i=idx: self._remove_subtask(i))

    def _load_task_data(self):
        if not self.task_data:
            return
        self.ent_title.insert(0, self.task_data.get('title', ''))
        self.cmb_priority.set(self.task_data.get('priority', 'Medium'))
        
        if self.task_data.get('category_name'):
            cat_str = f"{self.task_data.get('category_icon', '📁')} {self.task_data.get('category_name')}"
            self.cmb_category.set(cat_str)

        if self.task_data.get('due_date'):
            self.ent_due_date.delete(0, tk.END)
            self.ent_due_date.insert(0, self.task_data.get('due_date'))

        if self.task_data.get('due_time'):
            self.ent_due_time.delete(0, tk.END)
            self.ent_due_time.insert(0, self.task_data.get('due_time'))

        if self.task_data.get('notes'):
            self.txt_notes.insert("1.0", self.task_data.get('notes'))

        # Tags
        selected_tag_ids = [t['id'] for t in self.task_data.get('tags', [])]
        for tid, var in self.tag_vars.items():
            if tid in selected_tag_ids:
                var.set(True)

    def _save(self):
        title = self.ent_title.get().strip()
        if not title:
            messagebox.showwarning("Validation Error", "Task Title is required!", parent=self)
            return

        priority = self.cmb_priority.get()
        cat_str = self.cmb_category.get()
        category_id = None
        for cat in self.categories:
            if f"{cat['icon']} {cat['name']}" == cat_str:
                category_id = cat['id']
                break

        due_date = self.ent_due_date.get().strip()
        due_time = self.ent_due_time.get().strip()
        notes = self.txt_notes.get("1.0", tk.END).strip()

        tag_ids = [tid for tid, var in self.tag_vars.items() if var.get()]

        if self.task_data:
            # Update existing
            self.db.update_task(
                task_id=self.task_data['id'],
                title=title,
                notes=notes,
                category_id=category_id,
                priority=priority,
                status=self.task_data.get('status', 'Pending'),
                due_date=due_date,
                due_time=due_time,
                estimated_pomodoros=self.task_data.get('estimated_pomodoros', 1),
                tag_ids=tag_ids
            )
            # Update subtasks
            # For simplicity, add new subtasks if any
            existing_st_titles = [st['title'] for st in self.task_data.get('subtask_list', [])]
            for stt in self.subtasks_temp:
                if stt not in existing_st_titles:
                    self.db.add_subtask(self.task_data['id'], stt)
        else:
            # Add new
            self.db.add_task(
                title=title,
                notes=notes,
                category_id=category_id,
                priority=priority,
                status="Pending",
                due_date=due_date,
                due_time=due_time,
                tag_ids=tag_ids,
                subtasks=self.subtasks_temp
            )

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()
