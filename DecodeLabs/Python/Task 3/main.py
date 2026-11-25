"""
VaultShield Pro - Ultimate Password Generator & Security Manager
Main Application Entrypoint
"""

import tkinter as tk
from tkinter import ttk, messagebox

from theme import GLOBAL_THEME
from crypto_utils import (
    generate_random_password, generate_passphrase, generate_pronounceable_password,
    generate_pin, analyze_password_strength, check_breached_simulator
)
from database import VaultDatabase
from custom_widgets import CustomButton, CustomSlider, CustomToggleSwitch, StrengthMeterGauge, ToastNotification
from dialogs import MasterPasswordDialog, SaveEntryDialog, BulkGeneratorDialog

class VaultShieldApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("VaultShield Pro - Ultimate Password Generator & Security Vault")
        self.geometry("980x680")
        self.minsize(900, 600)

        self.db = VaultDatabase()
        self.master_password = None
        self.active_tab = "generator"
        self.generated_password = ""

        # UI state vars
        self.pwd_length = 16
        self.use_upper = True
        self.use_lower = True
        self.use_digits = True
        self.use_symbols = True
        self.exclude_ambig = False

        self.theme = GLOBAL_THEME.theme
        GLOBAL_THEME.register_listener(self.on_theme_change)

        self.configure(bg=self.theme["bg_dark"])
        self._build_layout()
        self._generate_active_password()

    def on_theme_change(self, theme):
        self.theme = theme
        self.configure(bg=self.theme["bg_dark"])
        self.sidebar.configure(bg=self.theme["bg_sidebar"])
        self.content_area.configure(bg=self.theme["bg_dark"])
        self.header_frame.configure(bg=self.theme["bg_dark"])
        self._refresh_tab_content()

    def _build_layout(self):
        # Sidebar Frame
        self.sidebar = tk.Frame(self, bg=self.theme["bg_sidebar"], width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand / Logo Header
        brand_frame = tk.Frame(self.sidebar, bg=self.theme["bg_sidebar"])
        brand_frame.pack(pady=(25, 20), padx=15, fill="x")

        tk.Label(brand_frame, text="🛡️ VaultShield", font=("Segoe UI", 14, "bold"), bg=self.theme["bg_sidebar"], fg=self.theme["accent_primary"]).pack(anchor="w")
        tk.Label(brand_frame, text="SECURITY SUITE", font=("Segoe UI", 7, "bold"), bg=self.theme["bg_sidebar"], fg=self.theme["fg_secondary"]).pack(anchor="w")

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("generator", "⚡ Password Gen", "⚡"),
            ("passphrase", "📝 Passphrase", "📝"),
            ("vault", "🔐 Vault Manager", "🔐"),
            ("audit", "📊 Security Audit", "📊"),
        ]

        for tab_id, label, icon in nav_items:
            btn = CustomButton(
                self.sidebar, text=label,
                command=lambda tid=tab_id: self._switch_tab(tid),
                width=190, height=42, radius=8,
                bg_color=self.theme["bg_card"],
                hover_color=self.theme["bg_card_hover"],
                fg_color=self.theme["fg_primary"],
                font=("Segoe UI", 10, "bold")
            )
            btn.pack(pady=6, padx=15)
            self.nav_buttons[tab_id] = btn

        # Theme toggle at bottom of sidebar
        theme_btn = CustomButton(
            self.sidebar, text="Toggle Theme", command=self._toggle_theme,
            width=190, height=36, radius=8,
            bg_color=self.theme["border_color"],
            hover_color=self.theme["fg_muted"],
            fg_color=self.theme["fg_primary"]
        )
        theme_btn.pack(side="bottom", pady=20, padx=15)

        # Content Main Area
        self.content_area = tk.Frame(self, bg=self.theme["bg_dark"])
        self.content_area.pack(side="right", fill="both", expand=True)

        # Top Header Bar
        self.header_frame = tk.Frame(self.content_area, bg=self.theme["bg_dark"])
        self.header_frame.pack(fill="x", padx=30, pady=(20, 10))

        self.header_title = tk.Label(self.header_frame, text="Password Generator", font=("Segoe UI", 18, "bold"), bg=self.theme["bg_dark"], fg=self.theme["fg_primary"])
        self.header_title.pack(side="left")

        # Container for dynamic view tabs
        self.tab_container = tk.Frame(self.content_area, bg=self.theme["bg_dark"])
        self.tab_container.pack(fill="both", expand=True, padx=30, pady=10)

        self._switch_tab("generator")

    def _toggle_theme(self):
        GLOBAL_THEME.toggle_theme()

    def _switch_tab(self, tab_id):
        self.active_tab = tab_id
        for tid, btn in self.nav_buttons.items():
            if tid == tab_id:
                btn.bg_color = self.theme["accent_primary"]
                btn.current_bg = self.theme["accent_primary"]
            else:
                btn.bg_color = self.theme["bg_card"]
                btn.current_bg = self.theme["bg_card"]
            btn.draw()

        titles = {
            "generator": "⚡ Custom Password Generator",
            "passphrase": "📝 Passphrase & Phonetic Generator",
            "vault": "🔐 Encrypted Password Vault",
            "audit": "📊 Vault Security Audit & Breach Checker"
        }
        self.header_title.config(text=titles.get(tab_id, "VaultShield"))
        self._refresh_tab_content()

    def _refresh_tab_content(self):
        for widget in self.tab_container.winfo_children():
            widget.destroy()

        if self.active_tab == "generator":
            self._render_generator_tab()
        elif self.active_tab == "passphrase":
            self._render_passphrase_tab()
        elif self.active_tab == "vault":
            self._render_vault_tab()
        elif self.active_tab == "audit":
            self._render_audit_tab()

    # --- TAB 1: CUSTOM PASSWORD GENERATOR ---
    def _render_generator_tab(self):
        card = tk.Frame(self.tab_container, bg=self.theme["bg_card"], bd=1, relief="solid")
        card.pack(fill="x", pady=(0, 20))

        # Password display banner
        pwd_banner = tk.Frame(card, bg=self.theme["bg_input"])
        pwd_banner.pack(fill="x", padx=20, pady=20)

        self.pwd_label = tk.Label(pwd_banner, text="", font=("Consolas", 20, "bold"), bg=self.theme["bg_input"], fg=self.theme["accent_primary"])
        self.pwd_label.pack(side="left", padx=15, pady=12)

        # Action Buttons inside banner
        btn_frame = tk.Frame(pwd_banner, bg=self.theme["bg_input"])
        btn_frame.pack(side="right", padx=15)

        CustomButton(btn_frame, text="Copy", command=self._copy_password, width=80, height=36, bg_color=self.theme["accent_success"]).pack(side="left", padx=4)
        CustomButton(btn_frame, text="↻ Refresh", command=self._generate_active_password, width=90, height=36, bg_color=self.theme["accent_primary"]).pack(side="left", padx=4)
        CustomButton(btn_frame, text="Save Vault", command=self._open_save_dialog, width=95, height=36, bg_color=self.theme["accent_purple"]).pack(side="left", padx=4)

        # Strength Meter Card
        meter_frame = tk.Frame(card, bg=self.theme["bg_card"])
        meter_frame.pack(fill="x", padx=20, pady=(0, 15))

        tk.Label(meter_frame, text="Strength Score:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_secondary"]).pack(anchor="w")
        
        sm_sub = tk.Frame(meter_frame, bg=self.theme["bg_card"])
        sm_sub.pack(fill="x", pady=4)

        self.gauge = StrengthMeterGauge(sm_sub, width=420, height=14)
        self.gauge.pack(side="left", padx=(0, 15))

        self.strength_lbl = tk.Label(sm_sub, text="Strong", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["accent_success"])
        self.strength_lbl.pack(side="left")

        self.info_lbl = tk.Label(meter_frame, text="", font=("Segoe UI", 8), bg=self.theme["bg_card"], fg=self.theme["fg_muted"])
        self.info_lbl.pack(anchor="w")

        # Controls & Customization Card
        ctrl_card = tk.Frame(self.tab_container, bg=self.theme["bg_card"])
        ctrl_card.pack(fill="both", expand=True)

        tk.Label(ctrl_card, text="Password Parameters", font=("Segoe UI", 11, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(anchor="w", padx=20, pady=(15, 5))

        # Slider row
        sl_frame = tk.Frame(ctrl_card, bg=self.theme["bg_card"])
        sl_frame.pack(fill="x", padx=20, pady=10)

        self.len_lbl = tk.Label(sl_frame, text=f"Length: {self.pwd_length}", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"], width=12, anchor="w")
        self.len_lbl.pack(side="left")

        self.slider = CustomSlider(sl_frame, from_=4, to=64, initial=self.pwd_length, command=self._on_length_change, width=480)
        self.slider.pack(side="left", padx=10)

        # Character Checkboxes Grid
        grid_frame = tk.Frame(ctrl_card, bg=self.theme["bg_card"])
        grid_frame.pack(fill="x", padx=20, pady=10)

        self.sw_upper = CustomToggleSwitch(grid_frame, text="Uppercase (A-Z)", initial=self.use_upper, command=lambda s: self._update_toggle("upper", s))
        self.sw_upper.grid(row=0, column=0, pady=6, sticky="w")

        self.sw_lower = CustomToggleSwitch(grid_frame, text="Lowercase (a-z)", initial=self.use_lower, command=lambda s: self._update_toggle("lower", s))
        self.sw_lower.grid(row=0, column=1, pady=6, sticky="w")

        self.sw_digits = CustomToggleSwitch(grid_frame, text="Numbers (0-9)", initial=self.use_digits, command=lambda s: self._update_toggle("digits", s))
        self.sw_digits.grid(row=1, column=0, pady=6, sticky="w")

        self.sw_symbols = CustomToggleSwitch(grid_frame, text="Symbols (!@#$)", initial=self.use_symbols, command=lambda s: self._update_toggle("symbols", s))
        self.sw_symbols.grid(row=1, column=1, pady=6, sticky="w")

        self.sw_ambig = CustomToggleSwitch(grid_frame, text="Exclude Ambiguous (l, 1, I, 0, O)", initial=self.exclude_ambig, command=lambda s: self._update_toggle("ambig", s))
        self.sw_ambig.grid(row=2, column=0, columnspan=2, pady=6, sticky="w")

        # Bottom Batch Export Callout
        b_frame = tk.Frame(ctrl_card, bg=self.theme["bg_card"])
        b_frame.pack(fill="x", padx=20, pady=15)

        CustomButton(b_frame, text="⚡ Open Bulk Generator", command=self._open_bulk_dialog, width=200, height=36, bg_color=self.theme["accent_primary"]).pack(side="right")

        self._update_password_display()

    def _on_length_change(self, val):
        self.pwd_length = val
        if hasattr(self, 'len_lbl'):
            self.len_lbl.config(text=f"Length: {self.pwd_length}")
        self._generate_active_password()

    def _update_toggle(self, key, state):
        if key == "upper": self.use_upper = state
        elif key == "lower": self.use_lower = state
        elif key == "digits": self.use_digits = state
        elif key == "symbols": self.use_symbols = state
        elif key == "ambig": self.exclude_ambig = state
        self._generate_active_password()

    def _generate_active_password(self):
        self.generated_password = generate_random_password(
            length=self.pwd_length,
            use_upper=self.use_upper,
            use_lower=self.use_lower,
            use_digits=self.use_digits,
            use_symbols=self.use_symbols,
            exclude_ambiguous=self.exclude_ambig
        )
        self._update_password_display()

    def _update_password_display(self):
        if hasattr(self, 'pwd_label'):
            self.pwd_label.config(text=self.generated_password)
            score, status, ckey, crack = analyze_password_strength(self.generated_password)
            self.gauge.update_gauge(score, ckey)
            self.strength_lbl.config(text=f"{status} ({score}%)", fg=self.theme.get(ckey, self.theme["fg_primary"]))
            self.info_lbl.config(text=f"Entropy: ~{int(score * 0.9)} bits | Est. Time to Crack: {crack}")

    def _copy_password(self):
        if self.generated_password:
            self.clipboard_clear()
            self.clipboard_append(self.generated_password)
            ToastNotification(self, "Password copied to clipboard!")

    # --- TAB 2: PASSPHRASE & PHONETIC GENERATOR ---
    def _render_passphrase_tab(self):
        card = tk.Frame(self.tab_container, bg=self.theme["bg_card"])
        card.pack(fill="both", expand=True)

        tk.Label(card, text="🧠 Memorable Passphrase & Phonetic Generator", font=("Segoe UI", 12, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(anchor="w", padx=20, pady=15)

        # Output Banner
        out_banner = tk.Frame(card, bg=self.theme["bg_input"])
        out_banner.pack(fill="x", padx=20, pady=10)

        self.passphrase_lbl = tk.Label(out_banner, text="", font=("Consolas", 16, "bold"), bg=self.theme["bg_input"], fg=self.theme["accent_success"], wraplength=550)
        self.passphrase_lbl.pack(side="left", padx=15, pady=15)

        CustomButton(out_banner, text="Copy", command=self._copy_passphrase, width=80, height=36, bg_color=self.theme["accent_success"]).pack(side="right", padx=15)

        # Options
        opt_frame = tk.Frame(card, bg=self.theme["bg_card"])
        opt_frame.pack(fill="x", padx=20, pady=20)

        self.pp_mode = tk.StringVar(value="diceware")

        tk.Radiobutton(opt_frame, text="Diceware Word Passphrase (e.g. Correct-Horse-Battery-42)", variable=self.pp_mode, value="diceware", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"], selectcolor=self.theme["bg_card"]).pack(anchor="w", pady=4)
        tk.Radiobutton(opt_frame, text="Phonetic Pronounceable Password (e.g. Bodu-Teka-91)", variable=self.pp_mode, value="phonetic", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"], selectcolor=self.theme["bg_card"]).pack(anchor="w", pady=4)
        tk.Radiobutton(opt_frame, text="Numeric PIN Code (e.g. 849204)", variable=self.pp_mode, value="pin", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"], selectcolor=self.theme["bg_card"]).pack(anchor="w", pady=4)

        CustomButton(card, text="🔄 Generate New Passphrase", command=self._gen_passphrase_action, width=240, height=40, bg_color=self.theme["accent_primary"]).pack(pady=20)
        self._gen_passphrase_action()

    def _gen_passphrase_action(self):
        mode = self.pp_mode.get()
        if mode == "diceware":
            self.active_passphrase = generate_passphrase(words_count=4)
        elif mode == "phonetic":
            self.active_passphrase = generate_pronounceable_password(length=12)
        else:
            self.active_passphrase = generate_pin(length=6)

        if hasattr(self, 'passphrase_lbl'):
            self.passphrase_lbl.config(text=self.active_passphrase)

    def _copy_passphrase(self):
        if hasattr(self, 'active_passphrase'):
            self.clipboard_clear()
            self.clipboard_append(self.active_passphrase)
            ToastNotification(self, "Passphrase copied to clipboard!")

    # --- TAB 3: ENCRYPTED VAULT MANAGER ---
    def _render_vault_tab(self):
        if not self.master_password:
            is_setup = not self.db.is_master_set()
            dlg = MasterPasswordDialog(self, self.db, is_setup=is_setup)
            self.wait_window(dlg)
            if dlg.unlocked:
                self.master_password = dlg.master_password
            else:
                tk.Label(self.tab_container, text="🔒 Vault Locked. Master key required.", font=("Segoe UI", 12), bg=self.theme["bg_dark"], fg=self.theme["accent_danger"]).pack(pady=50)
                return

        # Top Control Bar
        bar = tk.Frame(self.tab_container, bg=self.theme["bg_dark"])
        bar.pack(fill="x", pady=(0, 15))

        self.search_ent = tk.Entry(bar, font=("Segoe UI", 10), width=24, bg=self.theme["bg_input"], fg=self.theme["fg_primary"], insertbackground=self.theme["fg_primary"])
        self.search_ent.pack(side="left", padx=(0, 10))
        self.search_ent.insert(0, "Search vault...")
        self.search_ent.bind("<KeyRelease>", lambda e: self._refresh_vault_list())

        CustomButton(bar, text="+ Add Entry", command=self._open_save_dialog, width=110, height=34, bg_color=self.theme["accent_success"]).pack(side="left", padx=5)
        CustomButton(bar, text="🔒 Lock Vault", command=self._lock_vault, width=100, height=34, bg_color=self.theme["accent_danger"]).pack(side="right")

        # Vault Table Frame
        table_frame = tk.Frame(self.tab_container, bg=self.theme["bg_card"])
        table_frame.pack(fill="both", expand=True)

        columns = ("id", "title", "username", "category", "password")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Title / Service")
        self.tree.heading("username", text="Username / Email")
        self.tree.heading("category", text="Category")
        self.tree.heading("password", text="Password")

        self.tree.column("id", width=40, anchor="center")
        self.tree.column("title", width=160)
        self.tree.column("username", width=180)
        self.tree.column("category", width=100, anchor="center")
        self.tree.column("password", width=160)

        self.tree.pack(fill="both", expand=True, side="left")
        
        # Scrollbar
        sb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")

        # Table Action Buttons
        act_frame = tk.Frame(self.tab_container, bg=self.theme["bg_dark"])
        act_frame.pack(fill="x", pady=10)

        CustomButton(act_frame, text="Copy Password", command=self._copy_selected_vault_pwd, width=130, height=34, bg_color=self.theme["accent_primary"]).pack(side="left", padx=5)
        CustomButton(act_frame, text="Delete Entry", command=self._delete_selected_vault_entry, width=120, height=34, bg_color=self.theme["accent_danger"]).pack(side="left", padx=5)

        self._refresh_vault_list()

    def _refresh_vault_list(self):
        if not hasattr(self, 'tree') or not self.master_password:
            return
        for item in self.tree.get_children():
            self.tree.delete(item)

        q = self.search_ent.get() if hasattr(self, 'search_ent') else ""
        if q == "Search vault...": q = ""

        entries = self.db.get_all_entries(self.master_password, search_query=q)
        for e in entries:
            masked = "•" * min(12, len(e["password"]))
            self.tree.insert("", "end", values=(e["id"], e["title"], e["username"], e["category"], masked), tags=(e["password"],))

    def _copy_selected_vault_pwd(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Select Item", "Please select a vault entry first.")
            return
        tags = self.tree.item(sel[0], "tags")
        if tags:
            self.clipboard_clear()
            self.clipboard_append(tags[0])
            ToastNotification(self, "Vault password copied!")

    def _delete_selected_vault_entry(self):
        sel = self.tree.selection()
        if not sel:
            return
        item = self.tree.item(sel[0])
        entry_id = item["values"][0]
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this credential?"):
            self.db.delete_entry(entry_id)
            self._refresh_vault_list()

    def _lock_vault(self):
        self.master_password = None
        self._refresh_tab_content()

    # --- TAB 4: SECURITY AUDIT & BREACH CHECKER ---
    def _render_audit_tab(self):
        card = tk.Frame(self.tab_container, bg=self.theme["bg_card"])
        card.pack(fill="both", expand=True)

        tk.Label(card, text="📊 Vault Security Audit & Breach Checker", font=("Segoe UI", 12, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(anchor="w", padx=20, pady=15)

        # Single Password Breach Check Simulator
        chk_frame = tk.Frame(card, bg=self.theme["bg_input"])
        chk_frame.pack(fill="x", padx=20, pady=10)

        tk.Label(chk_frame, text="Breach Lookup Simulator:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_input"], fg=self.theme["fg_primary"]).pack(anchor="w", padx=15, pady=(10, 2))
        
        sub = tk.Frame(chk_frame, bg=self.theme["bg_input"])
        sub.pack(fill="x", padx=15, pady=(0, 10))

        self.audit_ent = tk.Entry(sub, font=("Segoe UI", 10), width=32, bg=self.theme["bg_card"], fg=self.theme["fg_primary"], insertbackground=self.theme["fg_primary"])
        self.audit_ent.pack(side="left", padx=(0, 10))

        CustomButton(sub, text="Check Breach Database", command=self._run_breach_check, width=170, height=34, bg_color=self.theme["accent_primary"]).pack(side="left")

        self.audit_result_lbl = tk.Label(chk_frame, text="", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_input"])
        self.audit_result_lbl.pack(anchor="w", padx=15, pady=(0, 10))

        # Overall Vault Health Report
        tk.Label(card, text="Vault Health Summary:", font=("Segoe UI", 10, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(anchor="w", padx=20, pady=(15, 5))

        if self.master_password:
            entries = self.db.get_all_entries(self.master_password)
            weak_cnt = sum(1 for e in entries if calculate_entropy(e["password"]) < 50)
            reused_cnt = len(entries) - len(set(e["password"] for e in entries))

            report_txt = f"• Total Vault Entries: {len(entries)}\n• Weak Passwords (< 50 bits): {weak_cnt}\n• Reused Passwords Detected: {reused_cnt}"
        else:
            report_txt = "Vault is currently locked. Unlock Vault tab to audit saved credentials."

        tk.Label(card, text=report_txt, font=("Segoe UI", 10), bg=self.theme["bg_card"], fg=self.theme["fg_secondary"], justify="left").pack(anchor="w", padx=20)

    def _run_breach_check(self):
        pwd = self.audit_ent.get()
        if not pwd:
            return
        is_breached, count = check_breached_simulator(pwd)
        if is_breached:
            self.audit_result_lbl.config(text=f"⚠️ WARNING: Password found in {count} known data breaches!", fg=self.theme["accent_danger"])
        else:
            self.audit_result_lbl.config(text="✓ Good news! Password was NOT found in breach databases.", fg=self.theme["accent_success"])

    # --- DIALOG CALLOUTS ---
    def _open_save_dialog(self):
        if not self.master_password:
            if not self.db.is_master_set():
                dlg = MasterPasswordDialog(self, self.db, is_setup=True)
                self.wait_window(dlg)
                if dlg.unlocked:
                    self.master_password = dlg.master_password
            else:
                dlg = MasterPasswordDialog(self, self.db, is_setup=False)
                self.wait_window(dlg)
                if dlg.unlocked:
                    self.master_password = dlg.master_password

        if self.master_password:
            init_data = {"password": self.generated_password}
            SaveEntryDialog(self, self.db, self.master_password, initial_data=init_data)

    def _open_bulk_dialog(self):
        BulkGeneratorDialog(self)

if __name__ == "__main__":
    app = VaultShieldApp()
    app.mainloop()
