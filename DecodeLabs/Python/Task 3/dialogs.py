"""
Modal Dialogs for Save Entry, Master Password Setup/Unlock, Bulk Generation, and Exporting
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from theme import GLOBAL_THEME
from custom_widgets import CustomButton
from crypto_utils import generate_random_password, generate_passphrase
import json
import csv

class MasterPasswordDialog(tk.Toplevel):
    """Modal for master password unlock or initial setup."""
    def __init__(self, parent, db, is_setup=False):
        super().__init__(parent)
        self.db = db
        self.is_setup = is_setup
        self.unlocked = False
        self.master_password = None
        self.theme = GLOBAL_THEME.theme

        self.title("VaultShield Master Key" if not is_setup else "Create Vault Master Key")
        self.geometry("380x300")
        self.resizable(False, False)
        self.configure(bg=self.theme["bg_card"])
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        title_text = "🔐 Master Password Setup" if self.is_setup else "🔐 Vault Authentication"
        sub_text = "Set a strong master key to encrypt your local password vault." if self.is_setup else "Enter master key to unlock encrypted credentials."

        tk.Label(self, text=title_text, font=("Segoe UI", 13, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(pady=(20, 5))
        tk.Label(self, text=sub_text, font=("Segoe UI", 9), wraplength=320, bg=self.theme["bg_card"], fg=self.theme["fg_secondary"]).pack(pady=(0, 15))

        f = tk.Frame(self, bg=self.theme["bg_card"])
        f.pack(pady=5)

        tk.Label(f, text="Master Password:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(anchor="w")
        self.pwd_entry = tk.Entry(f, show="•", width=32, font=("Segoe UI", 11), bg=self.theme["bg_input"], fg=self.theme["fg_primary"], insertbackground=self.theme["fg_primary"])
        self.pwd_entry.pack(pady=4)
        self.pwd_entry.focus()

        if self.is_setup:
            tk.Label(f, text="Confirm Password:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(anchor="w", pady=(8, 0))
            self.confirm_entry = tk.Entry(f, show="•", width=32, font=("Segoe UI", 11), bg=self.theme["bg_input"], fg=self.theme["fg_primary"], insertbackground=self.theme["fg_primary"])
            self.confirm_entry.pack(pady=4)

        btn_text = "Create Vault" if self.is_setup else "Unlock Vault"
        btn = CustomButton(self, text=btn_text, command=self._submit, width=280, height=38, bg_color=self.theme["accent_primary"])
        btn.pack(pady=20)

    def _submit(self):
        pwd = self.pwd_entry.get()
        if not pwd:
            messagebox.showerror("Error", "Master password cannot be empty!", parent=self)
            return

        if self.is_setup:
            conf = self.confirm_entry.get()
            if pwd != conf:
                messagebox.showerror("Error", "Passwords do not match!", parent=self)
                return
            if len(pwd) < 6:
                messagebox.showerror("Error", "Master password must be at least 6 characters long!", parent=self)
                return
            self.db.set_master_password(pwd)
            self.master_password = pwd
            self.unlocked = True
            self.destroy()
        else:
            if self.db.verify_master_password(pwd):
                self.master_password = pwd
                self.unlocked = True
                self.destroy()
            else:
                messagebox.showerror("Access Denied", "Incorrect Master Password!", parent=self)


class SaveEntryDialog(tk.Toplevel):
    """Modal for adding or editing password vault entries."""
    def __init__(self, parent, db, master_password, initial_data=None):
        super().__init__(parent)
        self.db = db
        self.master_password = master_password
        self.initial_data = initial_data
        self.saved = False
        self.theme = GLOBAL_THEME.theme

        self.title("Edit Vault Item" if initial_data else "Save To Vault")
        self.geometry("420x460")
        self.resizable(False, False)
        self.configure(bg=self.theme["bg_card"])
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="🔑 Save Credentials", font=("Segoe UI", 14, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(pady=(15, 10))

        form = tk.Frame(self, bg=self.theme["bg_card"])
        form.pack(padx=30, fill="x")

        def add_field(lbl_text, default="", is_pwd=False):
            tk.Label(form, text=lbl_text, font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_secondary"]).pack(anchor="w", pady=(6, 2))
            ent = tk.Entry(form, font=("Segoe UI", 10), bg=self.theme["bg_input"], fg=self.theme["fg_primary"], insertbackground=self.theme["fg_primary"])
            if is_pwd:
                ent.config(show="")
            if default:
                ent.insert(0, default)
            ent.pack(fill="x")
            return ent

        init = self.initial_data or {}
        self.title_ent = add_field("Account / Service Title:", init.get("title", ""))
        self.user_ent = add_field("Username / Email:", init.get("username", ""))
        self.pwd_ent = add_field("Password:", init.get("password", ""), is_pwd=True)
        self.site_ent = add_field("Website URL:", init.get("website", ""))

        tk.Label(form, text="Category Tag:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_secondary"]).pack(anchor="w", pady=(6, 2))
        self.cat_var = tk.StringVar(value=init.get("category", "General"))
        cats = ["General", "Social", "Work", "Banking", "Email", "Personal"]
        cat_menu = ttk.OptionMenu(form, self.cat_var, self.cat_var.get(), *cats)
        cat_menu.pack(fill="x")

        btn_text = "Update Entry" if self.initial_data else "Save Entry"
        btn = CustomButton(self, text=btn_text, command=self._save, width=360, height=38, bg_color=self.theme["accent_success"])
        btn.pack(pady=20)

    def _save(self):
        title = self.title_ent.get().strip()
        user = self.user_ent.get().strip()
        pwd = self.pwd_ent.get()
        site = self.site_ent.get().strip()
        cat = self.cat_var.get()

        if not title or not pwd:
            messagebox.showerror("Error", "Title and Password fields are required!", parent=self)
            return

        if self.initial_data:
            self.db.update_entry(self.initial_data["id"], title, user, pwd, site, cat, "", self.master_password)
        else:
            self.db.add_entry(title, user, pwd, site, cat, "", self.master_password)

        self.saved = True
        self.destroy()


class BulkGeneratorDialog(tk.Toplevel):
    """Modal for generating password batches and exporting them."""
    def __init__(self, parent):
        super().__init__(parent)
        self.theme = GLOBAL_THEME.theme
        self.title("⚡ Bulk Password Batch Generator")
        self.geometry("540x520")
        self.resizable(False, False)
        self.configure(bg=self.theme["bg_card"])
        self.transient(parent)
        self.grab_set()

        self._build_ui()

    def _build_ui(self):
        tk.Label(self, text="⚡ Bulk Password Batch Generator", font=("Segoe UI", 13, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_primary"]).pack(pady=15)

        ctrl_frame = tk.Frame(self, bg=self.theme["bg_card"])
        ctrl_frame.pack(padx=20, fill="x")

        tk.Label(ctrl_frame, text="Quantity:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_secondary"]).grid(row=0, column=0, sticky="w", padx=5)
        self.spin_count = tk.Spinbox(ctrl_frame, from_=5, to=100, width=8, font=("Segoe UI", 10))
        self.spin_count.delete(0, "end")
        self.spin_count.insert(0, "20")
        self.spin_count.grid(row=0, column=1, sticky="w", padx=5)

        tk.Label(ctrl_frame, text="Length:", font=("Segoe UI", 9, "bold"), bg=self.theme["bg_card"], fg=self.theme["fg_secondary"]).grid(row=0, column=2, sticky="w", padx=5)
        self.spin_len = tk.Spinbox(ctrl_frame, from_=8, to=48, width=8, font=("Segoe UI", 10))
        self.spin_len.delete(0, "end")
        self.spin_len.insert(0, "16")
        self.spin_len.grid(row=0, column=3, sticky="w", padx=5)

        btn_gen = CustomButton(ctrl_frame, text="Generate Batch", command=self._generate, width=120, height=30, bg_color=self.theme["accent_primary"])
        btn_gen.grid(row=0, column=4, padx=10)

        # Result box
        self.txt_area = tk.Text(self, font=("Consolas", 10), bg=self.theme["bg_input"], fg=self.theme["fg_primary"], insertbackground=self.theme["fg_primary"])
        self.txt_area.pack(padx=20, pady=15, fill="both", expand=True)

        exp_frame = tk.Frame(self, bg=self.theme["bg_card"])
        exp_frame.pack(pady=(0, 15))

        CustomButton(exp_frame, text="Export TXT", command=self._export_txt, width=130, height=34, bg_color=self.theme["accent_purple"]).pack(side="left", padx=10)
        CustomButton(exp_frame, text="Export CSV", command=self._export_csv, width=130, height=34, bg_color=self.theme["accent_success"]).pack(side="left", padx=10)

        self._generate()

    def _generate(self):
        try:
            count = int(self.spin_count.get())
            length = int(self.spin_len.get())
        except ValueError:
            count, length = 20, 16

        passwords = [generate_random_password(length=length) for _ in range(count)]
        self.txt_area.delete("1.0", "end")
        self.txt_area.insert("1.0", "\n".join(passwords))

    def _export_txt(self):
        content = self.txt_area.get("1.0", "end").strip()
        if not content:
            return
        fn = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if fn:
            with open(fn, "w") as f:
                f.write(content)
            messagebox.showinfo("Export Success", f"Exported to {fn}")

    def _export_csv(self):
        content = self.txt_area.get("1.0", "end").strip().splitlines()
        if not content:
            return
        fn = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if fn:
            with open(fn, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Index", "Password", "Length"])
                for i, pwd in enumerate(content, 1):
                    writer.writerow([i, pwd, len(pwd)])
            messagebox.showinfo("Export Success", f"Exported to {fn}")
