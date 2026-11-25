"""
dialogs.py - Modal Dialog Windows for ApexExpense
Contains interactive pop-up modals:
- Add / Edit Expense & Income Dialog
- Category & Monthly Budget Manager Dialog
- Savings Goal Creator & Deposit Modal
- Export & Data Backup Dialog
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from datetime import datetime
import csv
import json
from theme import THEME, FONTS, PAYMENT_METHODS

class AddExpenseDialog(ctk.CTkToplevel):
    """Modal dialog for adding or editing transactions."""
    def __init__(self, parent, db, expense_data=None, on_save_callback=None):
        super().__init__(parent)
        self.db = db
        self.expense_data = expense_data
        self.on_save_callback = on_save_callback
        
        self.title("Edit Transaction" if expense_data else "➕ Add New Transaction")
        self.geometry("450x580")
        self.resizable(False, False)
        self.configure(fg_color=THEME["bg_dim"])
        
        # Grab focus
        self.transient(parent)
        self.grab_set()

        self.categories = self.db.get_categories()
        self._build_ui()
        if expense_data:
            self._populate_fields()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        # Header Title
        title_text = "Edit Transaction" if self.expense_data else "New Transaction"
        lbl_header = ctk.CTkLabel(container, text=title_text, font=FONTS["title"], text_color=THEME["text_primary"])
        lbl_header.pack(anchor="w", padx=20, pady=(16, 12))

        # Income / Expense Toggle
        self.var_type = tk.StringVar(value="expense")
        self.type_frame = ctk.CTkFrame(container, fg_color=THEME["bg_dim"], corner_radius=8)
        self.type_frame.pack(fill="x", padx=20, pady=(0, 12))

        self.btn_expense = ctk.CTkRadioButton(
            self.type_frame, text="💸 Expense", value="expense", variable=self.var_type,
            text_color=THEME["text_primary"], fg_color=THEME["accent_danger"]
        )
        self.btn_expense.pack(side="left", padx=16, pady=8)

        self.btn_income = ctk.CTkRadioButton(
            self.type_frame, text="💰 Income", value="income", variable=self.var_type,
            text_color=THEME["text_primary"], fg_color=THEME["accent_success"]
        )
        self.btn_income.pack(side="right", padx=16, pady=8)

        # Title Field
        ctk.CTkLabel(container, text="Title / Description", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
        self.entry_title = ctk.CTkEntry(container, placeholder_text="e.g. Grocery Store, Salary...", fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
        self.entry_title.pack(fill="x", padx=20, pady=(0, 10))

        # Amount Field
        ctk.CTkLabel(container, text="Amount ($)", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
        self.entry_amount = ctk.CTkEntry(container, placeholder_text="0.00", fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
        self.entry_amount.pack(fill="x", padx=20, pady=(0, 10))

        # Category Dropdown
        ctk.CTkLabel(container, text="Category", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
        cat_options = [f"{c['icon']} {c['name']}" for c in self.categories]
        self.combo_category = ctk.CTkComboBox(container, values=cat_options, fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
        self.combo_category.pack(fill="x", padx=20, pady=(0, 10))
        if cat_options:
            self.combo_category.set(cat_options[0])

        # Payment Method Dropdown
        ctk.CTkLabel(container, text="Payment Method", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
        self.combo_method = ctk.CTkComboBox(container, values=PAYMENT_METHODS, fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
        self.combo_method.pack(fill="x", padx=20, pady=(0, 10))
        self.combo_method.set(PAYMENT_METHODS[0])

        # Date Field
        ctk.CTkLabel(container, text="Date (YYYY-MM-DD)", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
        self.entry_date = ctk.CTkEntry(container, fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
        self.entry_date.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.entry_date.pack(fill="x", padx=20, pady=(0, 10))

        # Action Buttons
        btn_frame = ctk.CTkFrame(container, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(16, 12))

        btn_cancel = ctk.CTkButton(btn_frame, text="Cancel", fg_color="transparent", border_width=1, border_color=THEME["border"], text_color=THEME["text_primary"], command=self.destroy)
        btn_cancel.pack(side="left", expand=True, fill="x", padx=(0, 6))

        btn_save = ctk.CTkButton(btn_frame, text="💾 Save Transaction", fg_color=THEME["accent_primary"], hover_color=THEME["accent_hover"], text_color="#FFFFFF", command=self._save)
        btn_save.pack(side="right", expand=True, fill="x", padx=(6, 0))

    def _populate_fields(self):
        d = self.expense_data
        self.entry_title.insert(0, d["title"])
        self.entry_amount.insert(0, str(d["amount"]))
        self.entry_date.delete(0, tk.END)
        self.entry_date.insert(0, d["date"])
        if d.get("is_income"):
            self.var_type.set("income")
        
        # Select matching category
        cat_name = d.get("category_name", "")
        for val in self.combo_category._values:
            if cat_name in val:
                self.combo_category.set(val)
                break
                
        if d.get("payment_method") in PAYMENT_METHODS:
            self.combo_method.set(d["payment_method"])

    def _save(self):
        title = self.entry_title.get().strip()
        amount_str = self.entry_amount.get().strip()
        date_str = self.entry_date.get().strip()
        cat_str = self.combo_category.get()
        method_str = self.combo_method.get()
        is_income = 1 if self.var_type.get() == "income" else 0

        if not title:
            messagebox.showerror("Validation Error", "Please enter a transaction title.", parent=self)
            return

        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Validation Error", "Please enter a valid positive number for amount.", parent=self)
            return

        # Extract category ID
        category_id = self.categories[0]["id"] if self.categories else 1
        for cat in self.categories:
            if cat["name"] in cat_str:
                category_id = cat["id"]
                break

        if self.expense_data:
            self.db.update_expense(self.expense_data["id"], title, amount, category_id, method_str, date_str, is_income=is_income)
        else:
            self.db.add_expense(title, amount, category_id, method_str, date_str, is_income=is_income)

        if self.on_save_callback:
            self.on_save_callback()

        self.destroy()


class CategoryBudgetDialog(ctk.CTkToplevel):
    """Modal dialog to create categories or edit monthly budgets."""
    def __init__(self, parent, db, on_update_callback=None):
        super().__init__(parent)
        self.db = db
        self.on_update_callback = on_update_callback
        
        self.title("⚙️ Category Budget Manager")
        self.geometry("500x520")
        self.resizable(False, False)
        self.configure(fg_color=THEME["bg_dim"])
        
        self.transient(parent)
        self.grab_set()
        
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(container, text="Manage Category Budgets", font=FONTS["title"], text_color=THEME["text_primary"]).pack(anchor="w", padx=20, pady=(16, 8))

        scroll = ctk.CTkScrollableFrame(container, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=12, pady=8)

        categories = self.db.get_categories()
        self.budget_entries = {}

        for cat in categories:
            row = ctk.CTkFrame(scroll, fg_color=THEME["bg_dim"], corner_radius=8)
            row.pack(fill="x", pady=4, padx=4)

            lbl = ctk.CTkLabel(
                row,
                text=f"{cat['icon']} {cat['name']}",
                font=FONTS["body_bold"],
                text_color=THEME["text_primary"],
                width=180,
                anchor="w"
            )
            lbl.pack(side="left", padx=10, pady=8)

            entry = ctk.CTkEntry(row, width=110, fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
            entry.insert(0, str(cat["monthly_budget"]))
            entry.pack(side="right", padx=10, pady=8)

            self.budget_entries[cat["id"]] = entry

        btn_save = ctk.CTkButton(
            container,
            text="💾 Save Budget Limits",
            fg_color=THEME["accent_primary"],
            hover_color=THEME["accent_hover"],
            text_color="#FFFFFF",
            command=self._save_budgets
        )
        btn_save.pack(fill="x", padx=20, pady=(12, 16))

    def _save_budgets(self):
        try:
            for cat_id, entry in self.budget_entries.items():
                val = float(entry.get().strip() or 0.0)
                self.db.update_category_budget(cat_id, val)
                
            if self.on_update_callback:
                self.on_update_callback()
                
            messagebox.showinfo("Success", "Category budgets updated successfully!", parent=self)
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values for all budgets.", parent=self)


class SavingsGoalDialog(ctk.CTkToplevel):
    """Modal to add a new savings goal or contribute deposit."""
    def __init__(self, parent, db, goal_data=None, on_save_callback=None):
        super().__init__(parent)
        self.db = db
        self.goal_data = goal_data
        self.on_save_callback = on_save_callback
        
        self.title("Deposit to Goal" if goal_data else "🎯 New Savings Goal")
        self.geometry("400x380")
        self.resizable(False, False)
        self.configure(fg_color=THEME["bg_dim"])
        
        self.transient(parent)
        self.grab_set()
        self._build_ui()

    def _build_ui(self):
        container = ctk.CTkFrame(self, fg_color=THEME["bg_card"], corner_radius=12, border_width=1, border_color=THEME["border"])
        container.pack(fill="both", expand=True, padx=16, pady=16)

        if self.goal_data:
            ctk.CTkLabel(container, text=f"Deposit to: {self.goal_data['title']}", font=FONTS["title"], text_color=THEME["text_primary"]).pack(anchor="w", padx=20, pady=(16, 12))
            
            ctk.CTkLabel(container, text="Deposit Amount ($)", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
            self.entry_deposit = ctk.CTkEntry(container, placeholder_text="0.00", fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
            self.entry_deposit.pack(fill="x", padx=20, pady=(0, 16))

            btn_submit = ctk.CTkButton(container, text="💰 Confirm Deposit", fg_color=THEME["accent_success"], text_color="#FFFFFF", command=self._save_deposit)
            btn_submit.pack(fill="x", padx=20, pady=(12, 16))
        else:
            ctk.CTkLabel(container, text="Create Savings Goal", font=FONTS["title"], text_color=THEME["text_primary"]).pack(anchor="w", padx=20, pady=(16, 12))

            ctk.CTkLabel(container, text="Goal Name", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
            self.entry_name = ctk.CTkEntry(container, placeholder_text="e.g. New Car, House Downpayment...", fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
            self.entry_name.pack(fill="x", padx=20, pady=(0, 10))

            ctk.CTkLabel(container, text="Target Amount ($)", font=FONTS["body_bold"], text_color=THEME["text_secondary"]).pack(anchor="w", padx=20, pady=(4, 2))
            self.entry_target = ctk.CTkEntry(container, placeholder_text="5000.00", fg_color=THEME["bg_input"], text_color=THEME["text_primary"])
            self.entry_target.pack(fill="x", padx=20, pady=(0, 10))

            btn_create = ctk.CTkButton(container, text="🎯 Create Goal", fg_color=THEME["accent_primary"], text_color="#FFFFFF", command=self._save_new_goal)
            btn_create.pack(fill="x", padx=20, pady=(12, 16))

    def _save_deposit(self):
        try:
            amt = float(self.entry_deposit.get().strip())
            if amt <= 0:
                raise ValueError()
            self.db.deposit_savings_goal(self.goal_data["id"], amt)
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid deposit amount.", parent=self)

    def _save_new_goal(self):
        name = self.entry_name.get().strip()
        try:
            target = float(self.entry_target.get().strip())
            if not name or target <= 0:
                raise ValueError()
            self.db.add_savings_goal(name, target, 0.0, '2026-12-31', '#10B981')
            if self.on_save_callback:
                self.on_save_callback()
            self.destroy()
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid goal title and target amount.", parent=self)


def export_transactions_to_csv(db, parent_window):
    """Exports all transaction logs to a user chosen CSV file."""
    file_path = filedialog.asksaveasfilename(
        parent=parent_window,
        defaultextension=".csv",
        filetypes=[("CSV Spreadsheet", "*.csv"), ("All Files", "*.*")],
        title="Export Transactions to CSV"
    )
    if not file_path:
        return
        
    expenses = db.get_expenses()
    try:
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Title", "Amount", "Type", "Category", "Payment Method", "Date", "Notes"])
            for e in expenses:
                t_type = "Income" if e["is_income"] else "Expense"
                writer.writerow([
                    e["id"], e["title"], e["amount"], t_type,
                    e["category_name"], e["payment_method"], e["date"], e["notes"] or ""
                ])
        messagebox.showinfo("Export Successful", f"Exported {len(expenses)} transactions to:\n{file_path}")
    except Exception as ex:
        messagebox.showerror("Export Failed", f"Could not export data: {ex}")
