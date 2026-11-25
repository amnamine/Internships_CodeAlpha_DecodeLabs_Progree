"""
main.py - ApexExpense Main Application Shell
World-class, maximalist Tkinter Expense Tracker application.
"""

import os
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk
from datetime import datetime

# Matplotlib embedding
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Custom Modules
from theme import THEME, DARK_THEME, LIGHT_THEME, FONTS, CURRENCIES, CATEGORY_PRESETS
from database import DatabaseManager
from custom_widgets import (
    ModernStatCard,
    CanvasDonutChart,
    CanvasBarChart,
    RoundedProgressBar,
    ToastNotification
)
from dialogs import (
    AddExpenseDialog,
    CategoryBudgetDialog,
    SavingsGoalDialog,
    export_transactions_to_csv
)

# CustomTkinter setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ApexExpenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("ApexExpense - Ultimate Expense & Financial Tracker")
        self.geometry("1180x760")
        self.minsize(1020, 680)
        self.configure(fg_color=THEME["bg_dim"])
        
        # State
        self.db = DatabaseManager()
        self.currency_symbol = "$"
        self.current_theme_mode = "Dark"
        self.active_tab = "dashboard"

        # Apply ttk table styling
        self._configure_table_styles()
        
        # Layout Structure
        self._build_sidebar()
        self._build_header()
        self._build_content_area()
        
        # Initial View Load
        self.show_tab("dashboard")

    def _configure_table_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Table styles matching dark theme
        style.configure(
            "Treeview",
            background=THEME["bg_card"],
            foreground=THEME["text_primary"],
            rowheight=34,
            fieldbackground=THEME["bg_card"],
            bordercolor=THEME["border"],
            borderwidth=0,
            font=("Segoe UI", 10)
        )
        style.configure(
            "Treeview.Heading",
            background=THEME["bg_dim"],
            foreground=THEME["text_secondary"],
            font=("Segoe UI", 10, "bold"),
            relief="flat"
        )
        style.map(
            "Treeview",
            background=[("selected", THEME["accent_primary"])],
            foreground=[("selected", "#FFFFFF")]
        )

    # --- UI LAYOUT INITIALIZATION ---
    def _build_sidebar(self):
        self.sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color=THEME["bg_card"],
            border_width=1,
            border_color=THEME["border"]
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Brand / Logo
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=16, pady=(20, 30))
        
        lbl_logo_icon = ctk.CTkLabel(logo_frame, text="💎", font=("Segoe UI Emoji", 24))
        lbl_logo_icon.pack(side="left", padx=(0, 8))
        
        lbl_logo_text = ctk.CTkLabel(logo_frame, text="ApexExpense", font=("Segoe UI", 18, "bold"), text_color=THEME["accent_primary"])
        lbl_logo_text.pack(side="left")

        # Navigation Buttons
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "📊 Dashboard"),
            ("transactions", "💸 Transactions"),
            ("budgets", "🎯 Budgets & Goals"),
            ("analytics", "📈 Analytics Charts"),
            ("settings", "⚙️ App Settings")
        ]

        for tab_key, label_text in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=label_text,
                anchor="w",
                font=FONTS["body_bold"],
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=THEME["text_secondary"],
                hover_color=THEME["bg_card_hover"],
                command=lambda k=tab_key: self.show_tab(k)
            )
            btn.pack(fill="x", padx=12, pady=4)
            self.nav_buttons[tab_key] = btn

        # Quick Add Button at bottom of sidebar
        sidebar_footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        sidebar_footer.pack(side="bottom", fill="x", padx=12, pady=20)
        
        btn_quick_add = ctk.CTkButton(
            sidebar_footer,
            text="➕ Quick Add Expense",
            font=FONTS["body_bold"],
            height=40,
            corner_radius=8,
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            text_color="#FFFFFF",
            command=self.open_add_expense_modal
        )
        btn_quick_add.pack(fill="x")

    def _build_header(self):
        self.header = ctk.CTkFrame(
            self,
            height=60,
            corner_radius=0,
            fg_color=THEME["bg_card"],
            border_width=1,
            border_color=THEME["border"]
        )
        self.header.pack(side="top", fill="x")

        # Page Title Label
        self.lbl_page_title = ctk.CTkLabel(
            self.header,
            text="Dashboard Overview",
            font=FONTS["subtitle"],
            text_color=THEME["text_primary"]
        )
        self.lbl_page_title.pack(side="left", padx=20)

        # Header Right Controls
        right_controls = ctk.CTkFrame(self.header, fg_color="transparent")
        right_controls.pack(side="right", padx=16)

        # Currency Selector
        self.combo_currency = ctk.CTkComboBox(
            right_controls,
            values=list(CURRENCIES.keys()),
            width=110,
            height=32,
            font=FONTS["caption"],
            fg_color=THEME["bg_input"],
            text_color=THEME["text_primary"],
            command=self._on_currency_change
        )
        self.combo_currency.pack(side="left", padx=8)
        self.combo_currency.set("USD ($)")

        # Export CSV Button
        btn_export = ctk.CTkButton(
            right_controls,
            text="📥 Export CSV",
            width=100,
            height=32,
            font=FONTS["caption"],
            fg_color=THEME["bg_card_hover"],
            hover_color=THEME["border"],
            text_color=THEME["text_primary"],
            command=lambda: export_transactions_to_csv(self.db, self)
        )
        btn_export.pack(side="left", padx=8)

    def _build_content_area(self):
        self.main_container = ctk.CTkFrame(self, fg_color=THEME["bg_dim"])
        self.main_container.pack(side="top", fill="both", expand=True, padx=16, pady=16)

        # Views Dictionary
        self.views = {}
        self.views["dashboard"] = self._create_dashboard_view()
        self.views["transactions"] = self._create_transactions_view()
        self.views["budgets"] = self._create_budgets_view()
        self.views["analytics"] = self._create_analytics_view()
        self.views["settings"] = self._create_settings_view()

    # --- TAB NAVIGATION ---
    def show_tab(self, tab_key):
        self.active_tab = tab_key
        
        # Highlight active tab button
        for key, btn in self.nav_buttons.items():
            if key == tab_key:
                btn.configure(fg_color=THEME["accent_primary"], text_color="#FFFFFF")
            else:
                btn.configure(fg_color="transparent", text_color=THEME["text_secondary"])

        # Update Header Title
        title_map = {
            "dashboard": "📊 Financial Dashboard Overview",
            "transactions": "💸 All Expense & Income Transactions",
            "budgets": "🎯 Category Budgets & Savings Goals",
            "analytics": "📈 Advanced Visual Analytics & Trends",
            "settings": "⚙️ System & Data Preferences"
        }
        self.lbl_page_title.configure(text=title_map.get(tab_key, ""))

        # Hide all views and show active one
        for v_key, frame in self.views.items():
            if v_key == tab_key:
                frame.pack(fill="both", expand=True)
            else:
                frame.pack_forget()

        # Refresh active tab content
        self.refresh_all_views()

    # --- VIEW 1: DASHBOARD VIEW ---
    def _create_dashboard_view(self):
        view = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")

        # Top KPI Cards Grid
        self.kpi_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.kpi_frame.pack(fill="x", pady=(0, 16))

        stats = self.db.get_summary_stats()
        
        self.card_balance = ModernStatCard(
            self.kpi_frame, "Net Balance", f"{self.currency_symbol}{stats['net_balance']:,.2f}",
            "Total Inflow vs Outflow", "💰", THEME["accent_success"]
        )
        self.card_balance.pack(side="left", expand=True, fill="x", padx=(0, 8))

        self.card_monthly_spent = ModernStatCard(
            self.kpi_frame, "Monthly Spent", f"{self.currency_symbol}{stats['monthly_spent']:,.2f}",
            "Current Month Outflow", "📉", THEME["accent_danger"]
        )
        self.card_monthly_spent.pack(side="left", expand=True, fill="x", padx=4)

        self.card_total_spent = ModernStatCard(
            self.kpi_frame, "Total Spent (Accumulator)", f"{self.currency_symbol}{stats['total_spent']:,.2f}",
            f"{stats['transaction_count']} total records", "💸", THEME["accent_primary"]
        )
        self.card_total_spent.pack(side="left", expand=True, fill="x", padx=(8, 0))

        # Middle Visual Charts Row (Donut Ring Chart + Spending Trend Bar Chart)
        charts_row = ctk.CTkFrame(view, fg_color="transparent")
        charts_row.pack(fill="x", pady=(0, 16))

        # Donut Chart Container
        donut_container = ctk.CTkFrame(charts_row, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        donut_container.pack(side="left", fill="both", expand=True, padx=(0, 8))

        ctk.CTkLabel(donut_container, text="Category Spending Breakdown", font=FONTS["heading"], text_color=THEME["text_primary"]).pack(anchor="w", padx=16, pady=(12, 4))
        
        self.donut_chart = CanvasDonutChart(donut_container, width=320, height=220, bg_color=THEME["bg_card"])
        self.donut_chart.pack(padx=16, pady=(0, 12))

        # Bar Chart Container
        bar_container = ctk.CTkFrame(charts_row, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        bar_container.pack(side="right", fill="both", expand=True, padx=(8, 0))

        ctk.CTkLabel(bar_container, text="14-Day Daily Spending Trend", font=FONTS["heading"], text_color=THEME["text_primary"]).pack(anchor="w", padx=16, pady=(12, 4))

        self.bar_chart = CanvasBarChart(bar_container, width=440, height=220, bg_color=THEME["bg_card"])
        self.bar_chart.pack(padx=16, pady=(0, 12))

        # Recent Transactions Section
        recent_frame = ctk.CTkFrame(view, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        recent_frame.pack(fill="x", pady=(0, 16))

        rec_header = ctk.CTkFrame(recent_frame, fg_color="transparent")
        rec_header.pack(fill="x", padx=16, pady=12)
        
        ctk.CTkLabel(rec_header, text="Recent Transactions", font=FONTS["heading"], text_color=THEME["text_primary"]).pack(side="left")
        btn_view_all = ctk.CTkButton(rec_header, text="View All ➔", width=90, fg_color="transparent", text_color=THEME["accent_primary"], command=lambda: self.show_tab("transactions"))
        btn_view_all.pack(side="right")

        # Table widget
        self.tree_dash = ttk.Treeview(
            recent_frame,
            columns=("ID", "Title", "Category", "Amount", "Method", "Date"),
            show="headings",
            height=6
        )
        self.tree_dash.heading("ID", text="#")
        self.tree_dash.heading("Title", text="Title / Description")
        self.tree_dash.heading("Category", text="Category")
        self.tree_dash.heading("Amount", text="Amount")
        self.tree_dash.heading("Method", text="Payment Method")
        self.tree_dash.heading("Date", text="Date")

        self.tree_dash.column("ID", width=40, anchor="center")
        self.tree_dash.column("Title", width=220)
        self.tree_dash.column("Category", width=140)
        self.tree_dash.column("Amount", width=100, anchor="e")
        self.tree_dash.column("Method", width=140)
        self.tree_dash.column("Date", width=100, anchor="center")
        
        self.tree_dash.pack(fill="x", padx=16, pady=(0, 16))
        return view

    # --- VIEW 2: TRANSACTIONS VIEW ---
    def _create_transactions_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color="transparent")

        # Search & Filter Toolbar
        toolbar = ctk.CTkFrame(view, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        toolbar.pack(fill="x", pady=(0, 12))

        # Search Entry
        self.entry_search = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Search description...",
            width=240,
            fg_color=THEME["bg_input"],
            text_color=THEME["text_primary"]
        )
        self.entry_search.pack(side="left", padx=12, pady=12)
        self.entry_search.bind("<KeyRelease>", lambda e: self.refresh_transactions_table())

        # Category Filter Dropdown
        categories = self.db.get_categories()
        cat_filter_options = ["All Categories"] + [f"{c['icon']} {c['name']}" for c in categories]
        self.combo_filter_cat = ctk.CTkComboBox(
            toolbar,
            values=cat_filter_options,
            width=180,
            fg_color=THEME["bg_input"],
            text_color=THEME["text_primary"],
            command=lambda v: self.refresh_transactions_table()
        )
        self.combo_filter_cat.pack(side="left", padx=8, pady=12)
        self.combo_filter_cat.set("All Categories")

        # Buttons Right
        btn_add = ctk.CTkButton(
            toolbar, text="➕ Add Transaction",
            fg_color=THEME["accent_primary"], hover_color=THEME["accent_hover"],
            text_color="#FFFFFF", command=self.open_add_expense_modal
        )
        btn_add.pack(side="right", padx=12, pady=12)

        btn_delete = ctk.CTkButton(
            toolbar, text="🗑️ Delete Selected",
            fg_color=THEME["accent_danger"], hover_color="#B91C1C",
            text_color="#FFFFFF", command=self._delete_selected_transaction
        )
        btn_delete.pack(side="right", padx=4, pady=12)

        # Full Transactions Table Frame
        table_container = ctk.CTkFrame(view, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        table_container.pack(fill="both", expand=True)

        self.tree_tx = ttk.Treeview(
            table_container,
            columns=("ID", "Type", "Title", "Category", "Amount", "Method", "Date"),
            show="headings"
        )
        self.tree_tx.heading("ID", text="#")
        self.tree_tx.heading("Type", text="Type")
        self.tree_tx.heading("Title", text="Title / Description")
        self.tree_tx.heading("Category", text="Category")
        self.tree_tx.heading("Amount", text="Amount")
        self.tree_tx.heading("Method", text="Payment Method")
        self.tree_tx.heading("Date", text="Date")

        self.tree_tx.column("ID", width=40, anchor="center")
        self.tree_tx.column("Type", width=80, anchor="center")
        self.tree_tx.column("Title", width=260)
        self.tree_tx.column("Category", width=160)
        self.tree_tx.column("Amount", width=120, anchor="e")
        self.tree_tx.column("Method", width=160)
        self.tree_tx.column("Date", width=120, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree_tx.yview)
        self.tree_tx.configure(yscrollcommand=scrollbar.set)
        
        self.tree_tx.pack(side="left", fill="both", expand=True, padx=12, pady=12)
        scrollbar.pack(side="right", fill="y", pady=12)

        # Double click to edit
        self.tree_tx.bind("<Double-1>", self._on_table_double_click)

        return view

    # --- VIEW 3: BUDGETS & GOALS VIEW ---
    def _create_budgets_view(self):
        view = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")

        # Section 1: Category Budgets Header
        b_header = ctk.CTkFrame(view, fg_color="transparent")
        b_header.pack(fill="x", pady=(0, 8))
        
        ctk.CTkLabel(b_header, text="Monthly Category Budgets", font=FONTS["title"], text_color=THEME["text_primary"]).pack(side="left")
        
        btn_manage_b = ctk.CTkButton(
            b_header, text="⚙️ Set Budget Limits",
            fg_color=THEME["accent_primary"], text_color="#FFFFFF",
            command=self.open_category_budget_modal
        )
        btn_manage_b.pack(side="right")

        # Container for Budget Progress Items
        self.budgets_scroll_frame = ctk.CTkFrame(view, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        self.budgets_scroll_frame.pack(fill="x", pady=(0, 20))

        # Section 2: Savings Goals
        g_header = ctk.CTkFrame(view, fg_color="transparent")
        g_header.pack(fill="x", pady=(8, 8))
        
        ctk.CTkLabel(g_header, text="Savings Goals Tracker", font=FONTS["title"], text_color=THEME["text_primary"]).pack(side="left")
        
        btn_add_g = ctk.CTkButton(
            g_header, text="🎯 New Savings Goal",
            fg_color=THEME["accent_success"], text_color="#FFFFFF",
            command=self.open_savings_goal_modal
        )
        btn_add_g.pack(side="right")

        self.goals_scroll_frame = ctk.CTkFrame(view, fg_color="transparent")
        self.goals_scroll_frame.pack(fill="x", pady=(0, 16))

        return view

    # --- VIEW 4: ANALYTICS VIEW ---
    def _create_analytics_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        
        ctk.CTkLabel(view, text="Matplotlib Financial Analytics & Category Distribution", font=FONTS["heading"], text_color=THEME["text_primary"]).pack(anchor="w", padx=16, pady=12)

        # Embedded Matplotlib Figure
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(9, 4.5), facecolor=THEME["bg_card"])
        self.fig.tight_layout(pad=3.0)

        self.mpl_canvas = FigureCanvasTkAgg(self.fig, master=view)
        self.mpl_canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=(0, 16))

        return view

    # --- VIEW 5: SETTINGS VIEW ---
    def _create_settings_view(self):
        view = ctk.CTkFrame(self.main_container, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])

        container = ctk.CTkFrame(view, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=24, pady=24)

        ctk.CTkLabel(container, text="Application Preferences", font=FONTS["title"], text_color=THEME["text_primary"]).pack(anchor="w", pady=(0, 16))

        # Appearance Theme Toggle
        theme_frame = ctk.CTkFrame(container, fg_color=THEME["bg_dim"], corner_radius=10)
        theme_frame.pack(fill="x", pady=8, padx=4)

        ctk.CTkLabel(theme_frame, text="🎨 Appearance Mode", font=FONTS["body_bold"], text_color=THEME["text_primary"]).pack(side="left", padx=16, pady=16)

        self.switch_theme = ctk.CTkSwitch(
            theme_frame, text="Dark Mode",
            font=FONTS["body_bold"],
            command=self._toggle_theme
        )
        self.switch_theme.pack(side="right", padx=16, pady=16)
        self.switch_theme.select()

        # Reset Database Button
        danger_frame = ctk.CTkFrame(container, fg_color=THEME["bg_dim"], corner_radius=10)
        danger_frame.pack(fill="x", pady=16, padx=4)

        ctk.CTkLabel(danger_frame, text="⚠️ Reset Demo Data", font=FONTS["body_bold"], text_color=THEME["accent_danger"]).pack(side="left", padx=16, pady=16)
        
        btn_reset = ctk.CTkButton(
            danger_frame, text="Reset & Re-seed Data",
            fg_color=THEME["accent_danger"], hover_color="#B91C1C",
            text_color="#FFFFFF", command=self._reset_demo_data
        )
        btn_reset.pack(side="right", padx=16, pady=16)

        return view

    # --- DATA REFRESH LOGIC ---
    def refresh_all_views(self):
        self.refresh_dashboard_view()
        self.refresh_transactions_table()
        self.refresh_budgets_view()
        self.refresh_analytics_view()

    def refresh_dashboard_view(self):
        stats = self.db.get_summary_stats()
        c = self.currency_symbol

        # Update KPI Cards
        self.card_balance.update_amount(f"{c}{stats['net_balance']:,.2f}")
        self.card_monthly_spent.update_amount(f"{c}{stats['monthly_spent']:,.2f}")
        self.card_total_spent.update_amount(
            f"{c}{stats['total_spent']:,.2f}",
            f"{stats['transaction_count']} total records"
        )

        # Update Donut Chart
        breakdown = self.db.get_category_spending_breakdown()
        donut_data = [
            {"name": item["name"], "amount": item["total_spent"], "color": item["color"]}
            for item in breakdown if item["total_spent"] > 0
        ]
        self.donut_chart.render_chart(donut_data, currency_symbol=c)

        # Update Bar Chart
        trend_data = self.db.get_daily_spending_trend(days=14)
        self.bar_chart.render_chart(trend_data, currency_symbol=c)

        # Update Dashboard Recent Table
        for row in self.tree_dash.get_children():
            self.tree_dash.delete(row)

        recent_expenses = self.db.get_expenses()[:6]
        for e in recent_expenses:
            prefix = "+" if e["is_income"] else "-"
            amt_str = f"{prefix}{c}{e['amount']:,.2f}"
            self.tree_dash.insert("", "end", values=(
                e["id"], e["title"], f"{e['category_icon']} {e['category_name']}",
                amt_str, e["payment_method"], e["date"]
            ))

    def refresh_transactions_table(self):
        for row in self.tree_tx.get_children():
            self.tree_tx.delete(row)

        search_query = self.entry_search.get().strip() if hasattr(self, 'entry_search') else ""
        selected_cat = self.combo_filter_cat.get() if hasattr(self, 'combo_filter_cat') else "All Categories"
        
        cat_id = None
        if selected_cat != "All Categories":
            for cat in self.db.get_categories():
                if cat["name"] in selected_cat:
                    cat_id = cat["id"]
                    break

        expenses = self.db.get_expenses(search=search_query, category_id=cat_id)
        c = self.currency_symbol

        for e in expenses:
            t_type = "💰 Income" if e["is_income"] else "💸 Expense"
            prefix = "+" if e["is_income"] else "-"
            amt_str = f"{prefix}{c}{e['amount']:,.2f}"

            self.tree_tx.insert("", "end", values=(
                e["id"], t_type, e["title"], f"{e['category_icon']} {e['category_name']}",
                amt_str, e["payment_method"], e["date"]
            ))

    def refresh_budgets_view(self):
        # Clear previous items
        for widget in self.budgets_scroll_frame.winfo_children():
            widget.destroy()

        breakdown = self.db.get_category_spending_breakdown()
        c = self.currency_symbol

        for cat in breakdown:
            spent = cat["total_spent"]
            budget = cat["monthly_budget"]
            
            if budget <= 0 and spent <= 0:
                continue

            row = ctk.CTkFrame(self.budgets_scroll_frame, fg_color=THEME["bg_dim"], corner_radius=10)
            row.pack(fill="x", padx=12, pady=6)

            # Header info
            info_frame = ctk.CTkFrame(row, fg_color="transparent")
            info_frame.pack(fill="x", padx=12, pady=(8, 2))

            lbl_name = ctk.CTkLabel(info_frame, text=f"{cat['icon']} {cat['name']}", font=FONTS["body_bold"], text_color=THEME["text_primary"])
            lbl_name.pack(side="left")

            pct = (spent / budget * 100) if budget > 0 else 0
            lbl_amt = ctk.CTkLabel(
                info_frame,
                text=f"{c}{spent:,.2f} / {c}{budget:,.2f} ({pct:.0f}%)",
                font=FONTS["caption"],
                text_color=THEME["accent_danger"] if spent > budget > 0 else THEME["text_secondary"]
            )
            lbl_amt.pack(side="right")

            # Progress Bar
            pbar = RoundedProgressBar(row)
            pbar.pack(fill="x", padx=12, pady=(0, 10))
            pbar.set_progress(spent, budget if budget > 0 else 1.0)

        # Refresh Savings Goals
        for widget in self.goals_scroll_frame.winfo_children():
            widget.destroy()

        goals = self.db.get_savings_goals()
        for g in goals:
            card = ctk.CTkFrame(self.goals_scroll_frame, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
            card.pack(fill="x", pady=6)

            h_frame = ctk.CTkFrame(card, fg_color="transparent")
            h_frame.pack(fill="x", padx=16, pady=(12, 4))

            ctk.CTkLabel(h_frame, text=f"🎯 {g['title']}", font=FONTS["heading"], text_color=THEME["text_primary"]).pack(side="left")

            pct_g = (g["current_amount"] / g["target_amount"] * 100) if g["target_amount"] > 0 else 0
            ctk.CTkLabel(h_frame, text=f"{c}{g['current_amount']:,.2f} of {c}{g['target_amount']:,.2f} ({pct_g:.1f}%)", font=FONTS["body_bold"], text_color=THEME["accent_success"]).pack(side="right")

            pbar = RoundedProgressBar(card)
            pbar.pack(fill="x", padx=16, pady=(4, 8))
            pbar.set_progress(g["current_amount"], g["target_amount"])

            btn_dep = ctk.CTkButton(
                card, text="➕ Deposit", width=80, height=26, font=FONTS["caption"],
                fg_color=THEME["accent_success"], text_color="#FFFFFF",
                command=lambda g_data=g: self.open_savings_goal_modal(goal_data=g_data)
            )
            btn_dep.pack(anchor="e", padx=16, pady=(0, 12))

    def refresh_analytics_view(self):
        self.ax1.clear()
        self.ax2.clear()

        # Data
        breakdown = self.db.get_category_spending_breakdown()
        cats = [b["name"] for b in breakdown if b["total_spent"] > 0]
        spents = [b["total_spent"] for b in breakdown if b["total_spent"] > 0]
        colors = [b["color"] for b in breakdown if b["total_spent"] > 0]

        bg_col = THEME["bg_card"]
        txt_col = THEME["text_primary"]

        self.ax1.set_facecolor(bg_col)
        self.ax2.set_facecolor(bg_col)

        # Plot 1: Category Spending Pie Chart
        if spents:
            wedges, texts, autotexts = self.ax1.pie(
                spents, labels=cats, colors=colors, autopct='%1.1f%%',
                startangle=140, textprops=dict(color=txt_col, fontsize=8)
            )
            for at in autotexts:
                at.set_color('#FFFFFF')
                at.set_weight('bold')
            self.ax1.set_title("Category Distribution", color=txt_col, fontsize=11, fontweight='bold')
        else:
            self.ax1.text(0.5, 0.5, "No Expense Data", ha='center', va='center', color=txt_col)

        # Plot 2: Daily Spending Bar Chart
        trend_data = self.db.get_daily_spending_trend(days=10)
        dates = [t["date"].split("-")[-1] for t in trend_data]
        amounts = [t["amount"] for t in trend_data]

        self.ax2.bar(dates, amounts, color=THEME["accent_primary"], width=0.5)
        self.ax2.set_title("10-Day Spending Trend", color=txt_col, fontsize=11, fontweight='bold')
        self.ax2.tick_params(colors=txt_col, labelsize=8)
        self.ax2.spines['bottom'].set_color(THEME["border"])
        self.ax2.spines['left'].set_color(THEME["border"])
        self.ax2.spines['top'].set_visible(False)
        self.ax2.spines['right'].set_visible(False)

        self.mpl_canvas.draw()

    # --- USER EVENT HANDLERS ---
    def _on_currency_change(self, choice):
        self.currency_symbol = CURRENCIES.get(choice, "$")
        self.refresh_all_views()
        ToastNotification(self, f"Currency changed to {choice}")

    def _toggle_theme(self):
        if self.switch_theme.get() == 1:
            ctk.set_appearance_mode("Dark")
            THEME.update(DARK_THEME)
        else:
            ctk.set_appearance_mode("Light")
            THEME.update(LIGHT_THEME)
        
        self.configure(fg_color=THEME["bg_dim"])
        self._configure_table_styles()
        self.refresh_all_views()
        ToastNotification(self, "Theme appearance updated!")

    def open_add_expense_modal(self, expense_data=None):
        AddExpenseDialog(self, self.db, expense_data=expense_data, on_save_callback=self._on_transaction_saved)

    def open_category_budget_modal(self):
        CategoryBudgetDialog(self, self.db, on_update_callback=self.refresh_all_views)

    def open_savings_goal_modal(self, goal_data=None):
        SavingsGoalDialog(self, self.db, goal_data=goal_data, on_save_callback=self.refresh_all_views)

    def _on_transaction_saved(self):
        self.refresh_all_views()
        ToastNotification(self, "Transaction saved successfully! 💳")

    def _on_table_double_click(self, event):
        selected_item = self.tree_tx.selection()
        if not selected_item:
            return
        values = self.tree_tx.item(selected_item[0], "values")
        tx_id = values[0]
        
        expenses = self.db.get_expenses()
        target = next((e for e in expenses if e["id"] == int(tx_id)), None)
        if target:
            self.open_add_expense_modal(expense_data=target)

    def _delete_selected_transaction(self):
        selected_item = self.tree_tx.selection()
        if not selected_item:
            messagebox.showwarning("Select Item", "Please select a transaction to delete.", parent=self)
            return
            
        values = self.tree_tx.item(selected_item[0], "values")
        tx_id = values[0]
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this transaction?", parent=self):
            self.db.delete_expense(tx_id)
            self.refresh_all_views()
            ToastNotification(self, "Transaction deleted", is_error=True)

    def _reset_demo_data(self):
        if messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all data back to default demo state?", parent=self):
            db_path = self.db.db_path
            if os.path.exists(db_path):
                os.remove(db_path)
            self.db = DatabaseManager()
            self.refresh_all_views()
            ToastNotification(self, "Demo data reset successfully!")


if __name__ == "__main__":
    app = ApexExpenseApp()
    app.mainloop()
