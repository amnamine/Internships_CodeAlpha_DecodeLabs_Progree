import os
import shutil
import re
import urllib.parse
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests

# Modern Theme Colors
BG_DARK = "#0F172A"       # Deep slate blue/black
BG_PANEL = "#1E293B"      # Sleek panel gray-blue
BG_CARD = "#334155"       # Card color
ACCENT_PRIMARY = "#6366F1" # Indigo purple
ACCENT_SECONDARY = "#8B5CF6" # Violet purple
TEXT_PRIMARY = "#F8FAFC"   # White / Off-white
TEXT_SECONDARY = "#94A3B8" # Slate gray
TEXT_MUTED = "#64748B"     # Muted gray
COLOR_SUCCESS = "#10B981"  # Emerald green
COLOR_WARNING = "#F59E0B"  # Amber orange
COLOR_DANGER = "#EF4444"   # Coral red

class ModernButton(tk.Canvas):
    """A beautiful, animated, rounded button using Tkinter Canvas."""
    def __init__(self, parent, text, command, bg_color=ACCENT_PRIMARY, fg_color=TEXT_PRIMARY, hover_color=ACCENT_SECONDARY, width=160, height=40, corner_radius=10, font=("Segoe UI", 10, "bold"), **kwargs):
        super().__init__(parent, width=width, height=height, bg=parent["bg"], highlightthickness=0, **kwargs)
        self.command = command
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.width = width
        self.height = height
        self.corner_radius = corner_radius
        self.text = text
        self.font = font
        
        self.rect_id = None
        self.text_id = None
        self.draw_button(self.bg_color)
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_click)
        self.bind("<ButtonRelease-1>", self.on_release)

    def draw_button(self, color):
        self.delete("all")
        r = self.corner_radius
        w = self.width
        h = self.height
        
        points = [
            r, 0,
            w - r, 0,
            w, r,
            w, h - r,
            w - r, h,
            r, h,
            0, h - r,
            0, r
        ]
        self.rect_id = self.create_polygon(points, fill=color, smooth=True, splinesteps=36)
        self.text_id = self.create_text(w/2, h/2, text=self.text, fill=self.fg_color, font=self.font, justify="center")

    def on_enter(self, event):
        self.draw_button(self.hover_color)

    def on_leave(self, event):
        self.draw_button(self.bg_color)

    def on_click(self, event):
        self.draw_button(self.adjust_color_brightness(self.hover_color, 0.8))

    def on_release(self, event):
        self.draw_button(self.hover_color)
        if self.command:
            self.command()

    def adjust_color_brightness(self, hex_color, factor):
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(min(255, max(0, int(c * factor))) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)


class AutomationSuiteApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NovaAutomate - Task Automation Suite")
        self.geometry("1020x680")
        self.configure(bg=BG_DARK)
        self.resizable(False, False)
        
        self.setup_styles()
        self.active_tab = "dashboard"
        self.create_layout()
        self.log_message("Welcome to NovaAutomate! Choose an automation utility to begin.", "info")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        
        style.configure("Treeview",
                        background=BG_PANEL,
                        foreground=TEXT_PRIMARY,
                        fieldbackground=BG_PANEL,
                        bordercolor=BG_PANEL,
                        rowheight=28,
                        font=("Segoe UI", 9))
        style.map("Treeview", background=[("selected", ACCENT_PRIMARY)])
        style.configure("Treeview.Heading",
                        background=BG_CARD,
                        foreground=TEXT_PRIMARY,
                        font=("Segoe UI", 9, "bold"))
        
        style.configure("TProgressbar",
                        thickness=8,
                        troughcolor=BG_CARD,
                        background=ACCENT_PRIMARY)

    def create_layout(self):
        self.header_frame = tk.Frame(self, bg=BG_PANEL, height=70)
        self.header_frame.pack(fill="x", side="top")
        self.header_frame.pack_propagate(False)
        
        header_title = tk.Label(
            self.header_frame,
            text="⚡ NOVA AUTOMATE",
            font=("Segoe UI", 16, "bold"),
            fg=TEXT_PRIMARY,
            bg=BG_PANEL
        )
        header_title.pack(side="left", padx=25, pady=15)
        
        header_subtitle = tk.Label(
            self.header_frame,
            text="A Sleek Multi-Task Automation Suite",
            font=("Segoe UI", 10, "italic"),
            fg=TEXT_SECONDARY,
            bg=BG_PANEL
        )
        header_subtitle.pack(side="left", padx=5, pady=20)

        # Sandbox Tester Button
        self.btn_sandbox = ModernButton(
            self.header_frame,
            text="🛠️ Setup Sandbox",
            command=self.setup_demo_sandbox,
            bg_color=ACCENT_SECONDARY,
            hover_color=ACCENT_PRIMARY,
            width=140,
            height=30,
            corner_radius=8
        )
        self.btn_sandbox.pack(side="right", padx=25, pady=20)

        self.sidebar = tk.Frame(self, bg=BG_PANEL, width=220)
        self.sidebar.pack(fill="y", side="left", padx=(0, 2))
        self.sidebar.pack_propagate(False)
        
        self.nav_buttons = {}
        navs = [
            ("dashboard", "🏠 Dashboard"),
            ("organizer", "📁 File Organizer"),
            ("extractor", "📧 Text & Emails"),
            ("scraper", "🌐 Web Scraper")
        ]
        
        for tab_id, text in navs:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 10, "bold"),
                fg=TEXT_SECONDARY,
                bg=BG_PANEL,
                activebackground=BG_CARD,
                activeforeground=TEXT_PRIMARY,
                bd=0,
                cursor="hand2",
                anchor="w",
                padx=20,
                pady=12,
                command=lambda tid=tab_id: self.switch_tab(tid)
            )
            btn.pack(fill="x", pady=2)
            self.nav_buttons[tab_id] = btn
        
        self.update_sidebar_highlight()

        self.content_container = tk.Frame(self, bg=BG_DARK)
        self.content_container.pack(fill="both", expand=True, side="left", padx=15, pady=15)
        
        self.pages = {}
        self.init_dashboard_page()
        self.init_organizer_page()
        self.init_extractor_page()
        self.init_scraper_page()
        
        self.show_page("dashboard")
        
        self.console_frame = tk.Frame(self, bg=BG_PANEL, height=160)
        self.console_frame.pack(fill="x", side="bottom")
        self.console_frame.pack_propagate(False)
        
        console_title_bar = tk.Frame(self.console_frame, bg=BG_CARD, height=25)
        console_title_bar.pack(fill="x", side="top")
        
        console_title = tk.Label(
            console_title_bar,
            text="SYSTEM TERMINAL LOG",
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY,
            bg=BG_CARD
        )
        console_title.pack(side="left", padx=15)
        
        btn_clear_log = tk.Button(
            console_title_bar,
            text="Clear",
            font=("Segoe UI", 8, "bold"),
            fg=TEXT_SECONDARY,
            bg=BG_CARD,
            bd=0,
            cursor="hand2",
            command=self.clear_logs
        )
        btn_clear_log.pack(side="right", padx=15)
        
        self.console_text = tk.Text(
            self.console_frame,
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Consolas", 9),
            bd=0,
            padx=15,
            pady=8,
            insertbackground=TEXT_PRIMARY
        )
        self.console_text.pack(fill="both", expand=True, side="left")
        
        scrollbar = tk.Scrollbar(self.console_frame, command=self.console_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.console_text.config(yscrollcommand=scrollbar.set)
        
        self.console_text.tag_config("info", foreground=TEXT_PRIMARY)
        self.console_text.tag_config("success", foreground=COLOR_SUCCESS)
        self.console_text.tag_config("warning", foreground=COLOR_WARNING)
        self.console_text.tag_config("danger", foreground=COLOR_DANGER)

    def log_message(self, message, msg_type="info"):
        self.console_text.config(state="normal")
        prefix = "[INFO] "
        if msg_type == "success":
            prefix = "[SUCCESS] "
        elif msg_type == "warning":
            prefix = "[WARNING] "
        elif msg_type == "danger":
            prefix = "[ERROR] "
            
        self.console_text.insert("end", f"{prefix}{message}\n", msg_type)
        self.console_text.see("end")
        self.console_text.config(state="disabled")

    def clear_logs(self):
        self.console_text.config(state="normal")
        self.console_text.delete("1.0", "end")
        self.console_text.config(state="disabled")

    def switch_tab(self, tab_id):
        self.active_tab = tab_id
        self.update_sidebar_highlight()
        self.show_page(tab_id)

    def update_sidebar_highlight(self):
        for tab_id, btn in self.nav_buttons.items():
            if tab_id == self.active_tab:
                btn.config(bg=BG_CARD, fg=TEXT_PRIMARY)
            else:
                btn.config(bg=BG_PANEL, fg=TEXT_SECONDARY)

    def show_page(self, tab_id):
        for page in self.pages.values():
            page.pack_forget()
        self.pages[tab_id].pack(fill="both", expand=True)

    def init_dashboard_page(self):
        page = tk.Frame(self.content_container, bg=BG_DARK)
        self.pages["dashboard"] = page
        
        title_label = tk.Label(
            page, 
            text="Choose an Automation Module", 
            font=("Segoe UI", 14, "bold"), 
            fg=TEXT_PRIMARY, 
            bg=BG_DARK
        )
        title_label.pack(anchor="w", pady=(5, 15))
        
        card_container = tk.Frame(page, bg=BG_DARK)
        card_container.pack(fill="both", expand=True)
        
        self.create_dashboard_card(
            card_container, 
            "📁 File Organizer", 
            "Clean and group your mess! Organize files by extensions into neat folders like Images, Documents, Videos, and Audio instantly.", 
            "organizer", 
            0, 0
        )
        self.create_dashboard_card(
            card_container, 
            "📧 Text & Emails Extractor", 
            "Scan any local files or input text block for email addresses, urls, phone numbers, or custom regex. Save matches instantly.", 
            "extractor", 
            0, 1
        )
        self.create_dashboard_card(
            card_container, 
            "🌐 Web Info Scraper", 
            "Fetch details from any URL. Extract page titles, meta tags, and list links or images for SEO and data scraping tasks.", 
            "scraper", 
            1, 0
        )

    def create_dashboard_card(self, parent, title, desc, target_tab, row, col):
        card = tk.Frame(parent, bg=BG_PANEL, bd=1, relief="flat", highlightbackground=BG_CARD, highlightthickness=1)
        card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")
        
        parent.columnconfigure(0, weight=1)
        parent.columnconfigure(1, weight=1)
        parent.rowconfigure(0, weight=1)
        parent.rowconfigure(1, weight=1)
        
        card_lbl = tk.Label(card, text=title, font=("Segoe UI", 12, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL)
        card_lbl.pack(anchor="w", padx=20, pady=(20, 5))
        
        desc_lbl = tk.Label(card, text=desc, font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_PANEL, justify="left", wraplength=280)
        desc_lbl.pack(anchor="w", padx=20, pady=(0, 20))
        
        btn = ModernButton(
            card, 
            text="Launch Module", 
            command=lambda: self.switch_tab(target_tab), 
            bg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_SECONDARY,
            width=140,
            height=32,
            corner_radius=8
        )
        btn.pack(anchor="w", padx=20, pady=(0, 20))

    def init_organizer_page(self):
        page = tk.Frame(self.content_container, bg=BG_DARK)
        self.pages["organizer"] = page
        
        tk.Label(page, text="📁 File Organizer & Cleaner", font=("Segoe UI", 14, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK).pack(anchor="w", pady=(5, 10))
        
        settings_frame = tk.Frame(page, bg=BG_PANEL, bd=1, relief="flat", highlightthickness=1, highlightbackground=BG_CARD)
        settings_frame.pack(fill="x", pady=10, ipady=10)
        
        tk.Label(settings_frame, text="Source Folder:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).grid(row=0, column=0, padx=15, pady=12, sticky="w")
        self.entry_src_dir = tk.Entry(settings_frame, bg=BG_CARD, fg=TEXT_PRIMARY, bd=0, insertbackground=TEXT_PRIMARY, width=50, font=("Segoe UI", 9))
        self.entry_src_dir.grid(row=0, column=1, padx=5, pady=12, sticky="w")
        
        btn_browse_src = ModernButton(
            settings_frame, 
            text="Browse", 
            command=self.browse_src_dir,
            bg_color=BG_CARD,
            hover_color=TEXT_MUTED,
            width=80,
            height=28,
            corner_radius=5
        )
        btn_browse_src.grid(row=0, column=2, padx=10, pady=12)
        
        ctrl_frame = tk.Frame(settings_frame, bg=BG_PANEL)
        ctrl_frame.grid(row=1, column=0, columnspan=3, padx=15, pady=5, sticky="w")
        
        tk.Label(ctrl_frame, text="Action Mode:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).pack(side="left")
        self.org_mode = tk.StringVar(value="Move")
        tk.Radiobutton(ctrl_frame, text="Move Files", variable=self.org_mode, value="Move", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=15)
        tk.Radiobutton(ctrl_frame, text="Copy Files (Safe)", variable=self.org_mode, value="Copy", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=5)
        
        types_frame = tk.Frame(page, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BG_CARD)
        types_frame.pack(fill="x", pady=5, ipady=8)
        
        tk.Label(types_frame, text="Select File Categories to Organize:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).pack(anchor="w", padx=15, pady=8)
        
        self.categories_to_organize = {
            "Images (.jpg, .jpeg, .png, .gif, .bmp)": tk.BooleanVar(value=True),
            "Documents (.pdf, .docx, .xlsx, .pptx, .txt, .csv)": tk.BooleanVar(value=True),
            "Audio & Music (.mp3, .wav, .aac, .flac)": tk.BooleanVar(value=False),
            "Videos & Movies (.mp4, .mkv, .avi, .mov)": tk.BooleanVar(value=False),
            "Archives & Zips (.zip, .rar, .tar, .gz)": tk.BooleanVar(value=False)
        }
        
        checkbox_grid = tk.Frame(types_frame, bg=BG_PANEL)
        checkbox_grid.pack(fill="x", padx=15)
        
        row_idx = 0
        col_idx = 0
        for name, var in self.categories_to_organize.items():
            cb = tk.Checkbutton(
                checkbox_grid,
                text=name,
                variable=var,
                bg=BG_PANEL,
                fg=TEXT_PRIMARY,
                selectcolor=BG_PANEL,
                activebackground=BG_PANEL,
                activeforeground=TEXT_PRIMARY
            )
            cb.grid(row=row_idx, column=col_idx, sticky="w", padx=10, pady=5)
            col_idx += 1
            if col_idx > 1:
                col_idx = 0
                row_idx += 1
                
        actions_frame = tk.Frame(page, bg=BG_DARK)
        actions_frame.pack(fill="x", pady=15)
        
        self.btn_preview_org = ModernButton(
            actions_frame,
            text="Preview Files",
            command=self.preview_organizer,
            bg_color=ACCENT_SECONDARY,
            hover_color=ACCENT_PRIMARY,
            width=150,
            height=36,
            corner_radius=8
        )
        self.btn_preview_org.pack(side="left")
        
        self.btn_run_org = ModernButton(
            actions_frame,
            text="⚡ Run Organizer",
            command=self.run_organizer,
            bg_color=COLOR_SUCCESS,
            hover_color="#059669",
            width=160,
            height=36,
            corner_radius=8
        )
        self.btn_run_org.pack(side="left", padx=15)
        
        self.progress_frame = tk.Frame(page, bg=BG_DARK)
        self.progress_frame.pack(fill="x", pady=(5, 0))
        
        self.lbl_progress = tk.Label(self.progress_frame, text="Progress: Idle", font=("Segoe UI", 9), fg=TEXT_SECONDARY, bg=BG_DARK)
        self.lbl_progress.pack(anchor="w", pady=(0, 3))
        
        self.progressbar = ttk.Progressbar(self.progress_frame, mode="determinate", style="TProgressbar")
        self.progressbar.pack(fill="x")

    def browse_src_dir(self):
        dir_path = filedialog.askdirectory()
        if dir_path:
            self.entry_src_dir.delete(0, tk.END)
            self.entry_src_dir.insert(0, dir_path)
            self.log_message(f"Selected source folder: {dir_path}", "info")

    def get_extension_mapping(self):
        mapping = {}
        cats = {
            "Images (.jpg, .jpeg, .png, .gif, .bmp)": (["jpg", "jpeg", "png", "gif", "bmp"], "Images"),
            "Documents (.pdf, .docx, .xlsx, .pptx, .txt, .csv)": (["pdf", "docx", "xlsx", "pptx", "txt", "csv"], "Documents"),
            "Audio & Music (.mp3, .wav, .aac, .flac)": (["mp3", "wav", "aac", "flac"], "Audio"),
            "Videos & Movies (.mp4, .mkv, .avi, .mov)": (["mp4", "mkv", "avi", "mov"], "Videos"),
            "Archives & Zips (.zip, .rar, .tar, .gz)": (["zip", "rar", "tar", "gz"], "Archives")
        }
        for name, var in self.categories_to_organize.items():
            if var.get():
                exts, folder_name = cats[name]
                for ext in exts:
                    mapping[ext] = folder_name
        return mapping

    def preview_organizer(self):
        src = self.entry_src_dir.get().strip()
        if not src or not os.path.exists(src):
            self.log_message("Please select a valid source directory.", "danger")
            messagebox.showerror("Error", "Please select a valid source directory.")
            return
            
        safe, err_msg = self.is_path_safe(src)
        if not safe:
            self.log_message(err_msg, "danger")
            messagebox.showerror("Security Restriction", err_msg)
            return
            
        mapping = self.get_extension_mapping()
        if not mapping:
            self.log_message("Please select at least one file category to organize.", "warning")
            return
            
        all_files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
        to_organize = []
        for f in all_files:
            _, ext = os.path.splitext(f)
            ext = ext.lower().replace(".", "")
            if ext in mapping:
                to_organize.append((f, mapping[ext]))
                
        if not to_organize:
            self.log_message(f"No files matching the selected criteria found in: {src}", "warning")
            messagebox.showinfo("Preview Result", "No files found to organize.")
        else:
            self.log_message(f"Preview: Found {len(to_organize)} file(s) to organize in '{src}':", "info")
            for filename, dest_folder in to_organize[:10]:
                self.log_message(f"  • '{filename}' -> will go to folder '{dest_folder}'", "info")
            if len(to_organize) > 10:
                self.log_message(f"  • ... and {len(to_organize) - 10} more files.", "info")

    def run_organizer(self):
        src = self.entry_src_dir.get().strip()
        if not src or not os.path.exists(src):
            self.log_message("Please select a valid source directory.", "danger")
            messagebox.showerror("Error", "Please select a valid source directory.")
            return
            
        safe, err_msg = self.is_path_safe(src)
        if not safe:
            self.log_message(err_msg, "danger")
            messagebox.showerror("Security Restriction", err_msg)
            return
            
        mapping = self.get_extension_mapping()
        if not mapping:
            self.log_message("Please select at least one file category to organize.", "warning")
            return
            
        mode = self.org_mode.get()
        
        threading.Thread(target=self._run_organizer_thread, args=(src, mapping, mode), daemon=True).start()

    def _run_organizer_thread(self, src, mapping, mode):
        all_files = [f for f in os.listdir(src) if os.path.isfile(os.path.join(src, f))]
        to_organize = []
        for f in all_files:
            _, ext = os.path.splitext(f)
            ext = ext.lower().replace(".", "")
            if ext in mapping:
                to_organize.append((f, mapping[ext]))
                
        if not to_organize:
            self.lbl_progress.config(text="Status: No files to organize.")
            self.log_message("No files found to process.", "warning")
            return
            
        self.log_message(f"Starting organization of {len(to_organize)} files in {mode} mode...", "info")
        self.progressbar["maximum"] = len(to_organize)
        self.progressbar["value"] = 0
        
        success_count = 0
        for i, (filename, dest_folder) in enumerate(to_organize):
            src_path = os.path.join(src, filename)
            dest_dir = os.path.join(src, dest_folder)
            
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)
                self.log_message(f"Created folder: {dest_folder}", "info")
                
            dest_path = os.path.join(dest_dir, filename)
            
            try:
                if mode == "Move":
                    shutil.move(src_path, dest_path)
                else:
                    shutil.copy2(src_path, dest_path)
                success_count += 1
                self.log_message(f"[{mode}d] {filename} -> {dest_folder}/", "success")
            except Exception as e:
                self.log_message(f"Failed to process {filename}: {str(e)}", "danger")
                
            self.progressbar["value"] = i + 1
            self.lbl_progress.config(text=f"Progress: Organized {i + 1}/{len(to_organize)} files")
            self.update_idletasks()
            
        self.log_message(f"Task finished! Successfully {mode.lower()}d {success_count} file(s).", "success")
        messagebox.showinfo("Success", f"File organization completed!\nSuccessfully processed {success_count} files.")

    def init_extractor_page(self):
        page = tk.Frame(self.content_container, bg=BG_DARK)
        self.pages["extractor"] = page
        
        tk.Label(page, text="📧 Text & Email Address Extractor", font=("Segoe UI", 14, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK).pack(anchor="w", pady=(5, 10))
        
        input_panel = tk.Frame(page, bg=BG_PANEL, bd=1, relief="flat", highlightthickness=1, highlightbackground=BG_CARD)
        input_panel.pack(fill="x", pady=5, ipady=8)
        
        tk.Label(input_panel, text="Choose Text File:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.entry_txt_file = tk.Entry(input_panel, bg=BG_CARD, fg=TEXT_PRIMARY, bd=0, insertbackground=TEXT_PRIMARY, width=50, font=("Segoe UI", 9))
        self.entry_txt_file.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        btn_browse_txt = ModernButton(
            input_panel,
            text="Browse",
            command=self.browse_txt_file,
            bg_color=BG_CARD,
            hover_color=TEXT_MUTED,
            width=80,
            height=28,
            corner_radius=5
        )
        btn_browse_txt.grid(row=0, column=2, padx=10, pady=8)
        
        criteria_frame = tk.Frame(input_panel, bg=BG_PANEL)
        criteria_frame.grid(row=1, column=0, columnspan=3, padx=15, pady=10, sticky="w")
        
        tk.Label(criteria_frame, text="Extraction Pattern:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).pack(side="left")
        self.extraction_type = tk.StringVar(value="email")
        
        tk.Radiobutton(criteria_frame, text="Emails Only", variable=self.extraction_type, value="email", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=10)
        tk.Radiobutton(criteria_frame, text="URLs", variable=self.extraction_type, value="url", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=10)
        tk.Radiobutton(criteria_frame, text="Phone Numbers", variable=self.extraction_type, value="phone", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=10)
        
        self.results_frame = tk.Frame(page, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BG_CARD)
        self.results_frame.pack(fill="both", expand=True, pady=10)
        
        columns = ("index", "extracted_value")
        self.tree_results = ttk.Treeview(self.results_frame, columns=columns, show="headings", selectmode="browse")
        self.tree_results.heading("index", text="#")
        self.tree_results.heading("extracted_value", text="Extracted Pattern Value")
        self.tree_results.column("index", width=50, minwidth=50, stretch=tk.NO, anchor="center")
        self.tree_results.column("extracted_value", width=500, minwidth=200)
        self.tree_results.pack(fill="both", expand=True, side="left", padx=5, pady=5)
        
        sb_tree = tk.Scrollbar(self.results_frame, command=self.tree_results.yview)
        sb_tree.pack(side="right", fill="y")
        self.tree_results.config(yscrollcommand=sb_tree.set)
        
        action_btn_frame = tk.Frame(page, bg=BG_DARK)
        action_btn_frame.pack(fill="x", pady=(0, 5))
        
        btn_extract = ModernButton(
            action_btn_frame,
            text="⚡ Extract Data",
            command=self.extract_data,
            bg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_SECONDARY,
            width=140,
            height=34,
            corner_radius=8
        )
        btn_extract.pack(side="left")
        
        self.btn_export_txt = ModernButton(
            action_btn_frame,
            text="📥 Save to File",
            command=self.export_results,
            bg_color=COLOR_SUCCESS,
            hover_color="#059669",
            width=140,
            height=34,
            corner_radius=8
        )
        self.btn_export_txt.pack(side="left", padx=15)
        
        self.extracted_items = []

    def browse_txt_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt *.csv *.log *.html *.json"), ("All files", "*.*")])
        if file_path:
            self.entry_txt_file.delete(0, tk.END)
            self.entry_txt_file.insert(0, file_path)
            self.log_message(f"Selected file for extraction: {file_path}", "info")

    def extract_data(self):
        file_path = self.entry_txt_file.get().strip()
        if not file_path or not os.path.exists(file_path):
            self.log_message("Please select a valid file to extract data.", "danger")
            messagebox.showerror("Error", "Please select a valid text file first.")
            return
            
        safe, err_msg = self.is_path_safe(file_path)
        if not safe:
            self.log_message(err_msg, "danger")
            messagebox.showerror("Security Restriction", err_msg)
            return
            
        pattern_type = self.extraction_type.get()
        
        if pattern_type == "email":
            regex = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        elif pattern_type == "url":
            regex = r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        else:
            regex = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
            
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
                
            matches = re.findall(regex, content)
            unique_matches = list(set(matches))
            unique_matches.sort()
            
            for child in self.tree_results.get_children():
                self.tree_results.delete(child)
                
            self.extracted_items = unique_matches
            
            for idx, val in enumerate(unique_matches, 1):
                self.tree_results.insert("", "end", values=(idx, val))
                
            self.log_message(f"Extracted {len(unique_matches)} unique {pattern_type}(s) from: {os.path.basename(file_path)}", "success")
            
        except Exception as e:
            self.log_message(f"Failed to read/extract file contents: {str(e)}", "danger")

    def export_results(self):
        if not self.extracted_items:
            self.log_message("No extracted items to export.", "warning")
            return
            
        dest_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("CSV File", "*.csv")],
            title="Save Extracted Items"
        )
        if not dest_file:
            return
            
        try:
            is_csv = dest_file.lower().endswith(".csv")
            with open(dest_file, "w", encoding="utf-8") as f:
                if is_csv:
                    f.write("Index,Extracted Value\n")
                    for idx, val in enumerate(self.extracted_items, 1):
                        f.write(f'{idx},"{val}"\n')
                else:
                    for val in self.extracted_items:
                        f.write(f"{val}\n")
                        
            self.log_message(f"Successfully saved {len(self.extracted_items)} items to: {dest_file}", "success")
            messagebox.showinfo("Export Successful", f"Saved successfully to:\n{dest_file}")
        except Exception as e:
            self.log_message(f"Failed to export results: {str(e)}", "danger")

    def init_scraper_page(self):
        page = tk.Frame(self.content_container, bg=BG_DARK)
        self.pages["scraper"] = page
        
        tk.Label(page, text="🌐 Web Info Scraper & Title Extractor", font=("Segoe UI", 14, "bold"), fg=TEXT_PRIMARY, bg=BG_DARK).pack(anchor="w", pady=(5, 10))
        
        scraper_panel = tk.Frame(page, bg=BG_PANEL, bd=1, relief="flat", highlightthickness=1, highlightbackground=BG_CARD)
        scraper_panel.pack(fill="x", pady=5, ipady=8)
        
        tk.Label(scraper_panel, text="Target URL:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).grid(row=0, column=0, padx=15, pady=8, sticky="w")
        self.entry_url = tk.Entry(scraper_panel, bg=BG_CARD, fg=TEXT_PRIMARY, bd=0, insertbackground=TEXT_PRIMARY, width=60, font=("Segoe UI", 9))
        self.entry_url.insert(0, "https://example.com")
        self.entry_url.grid(row=0, column=1, padx=5, pady=8, sticky="w")
        
        opts_frame = tk.Frame(scraper_panel, bg=BG_PANEL)
        opts_frame.grid(row=1, column=0, columnspan=2, padx=15, pady=5, sticky="w")
        
        tk.Label(opts_frame, text="Extraction Mode:", font=("Segoe UI", 9, "bold"), fg=TEXT_PRIMARY, bg=BG_PANEL).pack(side="left")
        self.scrape_mode = tk.StringVar(value="title")
        
        tk.Radiobutton(opts_frame, text="Page Title & Meta Description", variable=self.scrape_mode, value="title", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=10)
        tk.Radiobutton(opts_frame, text="All Links (href)", variable=self.scrape_mode, value="links", bg=BG_PANEL, fg=TEXT_PRIMARY, selectcolor=BG_PANEL, activebackground=BG_PANEL, activeforeground=TEXT_PRIMARY).pack(side="left", padx=10)
        
        self.scrape_results_frame = tk.Frame(page, bg=BG_PANEL, bd=1, highlightthickness=1, highlightbackground=BG_CARD)
        self.scrape_results_frame.pack(fill="both", expand=True, pady=10)
        
        self.scrape_text = tk.Text(
            self.scrape_results_frame,
            bg=BG_PANEL,
            fg=TEXT_PRIMARY,
            font=("Consolas", 9),
            bd=0,
            padx=10,
            pady=10,
            insertbackground=TEXT_PRIMARY
        )
        self.scrape_text.pack(fill="both", expand=True, side="left")
        
        sb_scrape = tk.Scrollbar(self.scrape_results_frame, command=self.scrape_text.yview)
        sb_scrape.pack(side="right", fill="y")
        self.scrape_text.config(yscrollcommand=sb_scrape.set)
        
        action_btn_frame = tk.Frame(page, bg=BG_DARK)
        action_btn_frame.pack(fill="x", pady=(0, 5))
        
        btn_scrape = ModernButton(
            action_btn_frame,
            text="⚡ Run Scraper",
            command=self.run_scraper,
            bg_color=ACCENT_PRIMARY,
            hover_color=ACCENT_SECONDARY,
            width=140,
            height=34,
            corner_radius=8
        )
        btn_scrape.pack(side="left")
        
        self.btn_export_scrape = ModernButton(
            action_btn_frame,
            text="📥 Save Report",
            command=self.save_scrape_report,
            bg_color=COLOR_SUCCESS,
            hover_color="#059669",
            width=140,
            height=34,
            corner_radius=8
        )
        self.btn_export_scrape.pack(side="left", padx=15)

    def run_scraper(self):
        url = self.entry_url.get().strip()
        if not url:
            self.log_message("Please enter a valid URL.", "danger")
            return
            
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
            self.entry_url.delete(0, tk.END)
            self.entry_url.insert(0, url)
            
        mode = self.scrape_mode.get()
        self.log_message(f"Scraping web address: {url} ...", "info")
        
        threading.Thread(target=self._run_scraper_thread, args=(url, mode), daemon=True).start()

    def _run_scraper_thread(self, url, mode):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        }
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code != 200:
                self.log_message(f"HTTP Response code: {response.status_code}", "danger")
                
            html = response.text
            
            self.scrape_text.config(state="normal")
            self.scrape_text.delete("1.0", "end")
            
            if mode == "title":
                title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE | re.DOTALL)
                title = title_match.group(1).strip() if title_match else "N/A"
                
                desc_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\'](.*?)["\']', html, re.IGNORECASE)
                if not desc_match:
                    desc_match = re.search(r'<meta[^>]*content=["\'](.*?)["\'][^>]*name=["\']description["\']', html, re.IGNORECASE)
                description = desc_match.group(1).strip() if desc_match else "N/A"
                
                report = f"URL: {url}\n"
                report += f"Response Status Code: {response.status_code}\n"
                report += f"="*50 + "\n"
                report += f"PAGE TITLE:\n{title}\n\n"
                report += f"META DESCRIPTION:\n{description}\n"
                
                self.scrape_text.insert("end", report)
                self.log_message(f"Successfully scraped title and metadata for {url}", "success")
                
            elif mode == "links":
                links = re.findall(r'href=["\'](https?://[^"\']+)["\']', html, re.IGNORECASE)
                unique_links = list(set(links))
                unique_links.sort()
                
                report = f"Scraped Links Report for: {url}\n"
                report += f"Total links found: {len(links)} ({len(unique_links)} unique)\n"
                report += f"="*50 + "\n"
                for idx, link in enumerate(unique_links, 1):
                    report += f"{idx}. {link}\n"
                    
                self.scrape_text.insert("end", report)
                self.log_message(f"Successfully extracted {len(unique_links)} unique web links.", "success")
                
            self.scrape_text.config(state="disabled")
            
        except Exception as e:
            self.log_message(f"Web request error: {str(e)}", "danger")
            self.scrape_text.config(state="normal")
            self.scrape_text.delete("1.0", "end")
            self.scrape_text.insert("end", f"Failed to retrieve/scrape page:\n{str(e)}")
            self.scrape_text.config(state="disabled")

    def save_scrape_report(self):
        content = self.scrape_text.get("1.0", "end").strip()
        if not content or content.startswith("Failed to retrieve"):
            self.log_message("No content to save.", "warning")
            return
            
        dest_file = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("HTML File", "*.html")],
            title="Save Scraping Report"
        )
        if not dest_file:
            return
            
        try:
            with open(dest_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.log_message(f"Scrape report successfully saved to: {dest_file}", "success")
            messagebox.showinfo("Export Successful", f"Report saved to:\n{dest_file}")
        except Exception as e:
            self.log_message(f"Failed to save report: {str(e)}", "danger")

    def is_path_safe(self, path):
        current_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
        current_dir = os.path.abspath(current_dir)
        path = os.path.abspath(path)
        
        # Check if path is within current_dir
        try:
            common = os.path.commonpath([current_dir, path])
            if os.path.normcase(common) == os.path.normcase(current_dir):
                if os.path.normcase(path) == os.path.normcase(current_dir):
                    return False, "To protect script files, do not run operations directly in the Task 3 root. Please target a subfolder (like 'demo_sandbox')."
                return True, ""
        except ValueError:
            pass
        return False, "For safety reasons, operations are restricted strictly to folders within the Task 3 workspace directory."

    def setup_demo_sandbox(self):
        current_dir = os.path.dirname(os.path.abspath(__file__)) if __file__ else os.getcwd()
        sandbox_dir = os.path.join(current_dir, "demo_sandbox")
        
        try:
            if not os.path.exists(sandbox_dir):
                os.makedirs(sandbox_dir)
                
            files_to_create = {
                "document1.txt": "This is a mock text file. Contact us at support@example.com or info@novacode.org for help. Visit https://example.com for info or call +1-555-0199.",
                "invoice.pdf": "%PDF-1.4 mock content invoice",
                "notes.docx": "Word doc mock content with mail admin@workspace.com",
                "photo1.jpg": "Mock JPG binary data",
                "graphic.png": "Mock PNG binary data",
                "song.mp3": "Mock MP3 audio data",
                "clip.mp4": "Mock MP4 video data",
                "backup.zip": "Mock ZIP archive data"
            }
            
            for fname, content in files_to_create.items():
                fpath = os.path.join(sandbox_dir, fname)
                with open(fpath, "w", encoding="utf-8") as f:
                    f.write(content)
            
            # Populate entry variables if they exist
            self.entry_src_dir.delete(0, tk.END)
            self.entry_src_dir.insert(0, sandbox_dir)
            
            sample_txt_path = os.path.join(sandbox_dir, "document1.txt")
            self.entry_txt_file.delete(0, tk.END)
            self.entry_txt_file.insert(0, sample_txt_path)
            
            self.log_message(f"Safe Sandbox environment configured at: {sandbox_dir}", "success")
            self.log_message("Auto-populated mock images, text files, and media.", "success")
            self.log_message("Inputs have been auto-configured to point to this folder.", "info")
            messagebox.showinfo("Sandbox Configured", f"Safe Sandbox environment created successfully at:\n{sandbox_dir}\n\nInputs have been configured to point to it.")
            
        except Exception as e:
            self.log_message(f"Failed to setup sandbox: {str(e)}", "danger")
            messagebox.showerror("Error", f"Could not create sandbox folder: {str(e)}")


if __name__ == "__main__":
    app = AutomationSuiteApp()
    app.mainloop()
