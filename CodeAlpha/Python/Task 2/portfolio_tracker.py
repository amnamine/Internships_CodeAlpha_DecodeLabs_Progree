import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import os

# Hardcoded stock price database
STOCK_PRICES = {
    "AAPL": 180.00,
    "TSLA": 250.00,
    "MSFT": 420.00,
    "NVDA": 120.00,
    "AMZN": 185.00,
    "GOOGL": 175.00,
    "META": 480.00,
    "NFLX": 610.00,
    "AMD": 160.00,
    "COIN": 220.00
}

# Modern Dark Theme Colors
COLOR_BG = "#121214"
COLOR_CARD = "#1A1A1E"
COLOR_INPUT_BG = "#26262B"
COLOR_TEXT = "#E1E1E6"
COLOR_MUTED = "#8D8D99"
COLOR_ACCENT = "#6366F1"  # Indigo
COLOR_ACCENT_HOVER = "#4F46E5"
COLOR_SUCCESS = "#10B981"  # Emerald
COLOR_DANGER = "#EF4444"   # Red

# Palettes for the visualization slices
CHART_COLORS = ["#6366F1", "#10B981", "#F59E0B", "#EF4444", "#3B82F6", "#8B5CF6", "#EC4899", "#14B8A6", "#84CC16", "#06B6D4"]

class PortfolioTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Antigravity Stock Portfolio Tracker")
        self.root.geometry("1100x700")
        self.root.configure(bg=COLOR_BG)
        self.root.resizable(True, True)

        # Portfolio state: { "TICKER": quantity }
        self.portfolio = {
            "AAPL": 10.0,
            "TSLA": 5.0,
            "MSFT": 8.0,
            "NVDA": 25.0
        }

        self.setup_styles()
        self.create_widgets()
        self.update_ui()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        
        # Configure frames and labels
        style.configure("TFrame", background=COLOR_BG)
        style.configure("Card.TFrame", background=COLOR_CARD)
        
        style.configure("TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Card.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=COLOR_CARD, foreground=COLOR_TEXT, font=("Segoe UI", 16, "bold"))
        style.configure("Title.TLabel", background=COLOR_BG, foreground=COLOR_TEXT, font=("Segoe UI", 20, "bold"))
        
        # Treeview styling
        style.configure("Treeview", 
                        background=COLOR_CARD, 
                        fieldbackground=COLOR_CARD, 
                        foreground=COLOR_TEXT, 
                        font=("Segoe UI", 10),
                        rowheight=35)
        style.configure("Treeview.Heading", 
                        background=COLOR_INPUT_BG, 
                        foreground=COLOR_TEXT, 
                        relief="flat",
                        font=("Segoe UI", 10, "bold"))
        
        style.map("Treeview", 
                  background=[("selected", COLOR_ACCENT)],
                  foreground=[("selected", "#FFFFFF")])
        style.map("Treeview.Heading",
                  background=[("active", COLOR_ACCENT)],
                  foreground=[("active", "#FFFFFF")])

        # Configure Combobox style
        style.configure("TCombobox", fieldbackground=COLOR_INPUT_BG, background=COLOR_INPUT_BG, foreground=COLOR_TEXT)
        
    def create_widgets(self):
        # Header / Title Bar
        title_frame = tk.Frame(self.root, bg=COLOR_BG)
        title_frame.pack(fill="x", padx=30, pady=(25, 10))
        
        title_lbl = ttk.Label(title_frame, text="Stock Portfolio Tracker", style="Title.TLabel")
        title_lbl.pack(side="left")
        
        subtitle_lbl = ttk.Label(title_frame, text="Real-time Investment Metrics & Visualization", font=("Segoe UI", 10))
        subtitle_lbl.pack(side="left", padx=15, pady=(8, 0))

        # Main Layout Container
        main_container = tk.Frame(self.root, bg=COLOR_BG)
        main_container.pack(fill="both", expand=True, padx=30, pady=15)
        
        # Left Panel (Portfolio Table & Inputs)
        left_panel = tk.Frame(main_container, bg=COLOR_BG)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 15))
        
        # Stats Row
        stats_frame = tk.Frame(left_panel, bg=COLOR_BG)
        stats_frame.pack(fill="x", pady=(0, 15))
        
        self.stat_val_total = self.create_stat_card(stats_frame, "Total Portfolio Value", "$0.00", COLOR_SUCCESS)
        self.stat_val_assets = self.create_stat_card(stats_frame, "Unique Assets", "0", COLOR_ACCENT)
        self.stat_val_shares = self.create_stat_card(stats_frame, "Total Shares", "0", COLOR_MUTED)

        # Table Card Frame
        table_card = tk.Frame(left_panel, bg=COLOR_CARD, bd=0)
        table_card.pack(fill="both", expand=True)
        
        # Treeview Scrollbar
        scroll = ttk.Scrollbar(table_card)
        scroll.pack(side="right", fill="y")
        
        # Treeview table
        self.tree = ttk.Treeview(table_card, columns=("ticker", "price", "shares", "value", "allocation"), show="headings", yscrollcommand=scroll.set)
        self.tree.pack(fill="both", expand=True, padx=1, pady=1)
        scroll.config(command=self.tree.yview)
        
        self.tree.heading("ticker", text="Ticker")
        self.tree.heading("price", text="Price")
        self.tree.heading("shares", text="Shares Owned")
        self.tree.heading("value", text="Total Value")
        self.tree.heading("allocation", text="Allocation")
        
        self.tree.column("ticker", width=80, anchor="center")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("shares", width=100, anchor="e")
        self.tree.column("value", width=120, anchor="e")
        self.tree.column("allocation", width=100, anchor="center")
        
        self.tree.bind("<<TreeviewSelect>>", self.on_select_row)

        # Right Panel (Inputs, Controls, Charts)
        right_panel = tk.Frame(main_container, bg=COLOR_BG, width=420)
        right_panel.pack(side="right", fill="both")
        right_panel.pack_propagate(False)
        
        # Action Card (Add/Edit Stocks)
        action_card = tk.Frame(right_panel, bg=COLOR_CARD)
        action_card.pack(fill="x", pady=(0, 15))
        
        # Title of Action Card
        act_title = ttk.Label(action_card, text="Manage Assets", style="Header.TLabel")
        act_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        input_row = tk.Frame(action_card, bg=COLOR_CARD)
        input_row.pack(fill="x", padx=20, pady=5)
        
        # Ticker Select
        ticker_lbl = ttk.Label(input_row, text="Stock Symbol", style="Card.TLabel")
        ticker_lbl.grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        self.ticker_var = tk.StringVar()
        self.ticker_combo = ttk.Combobox(input_row, textvariable=self.ticker_var, values=list(STOCK_PRICES.keys()), state="readonly", width=12, font=("Segoe UI", 11))
        self.ticker_combo.grid(row=1, column=0, padx=(0, 10), sticky="w")
        self.ticker_combo.bind("<<ComboboxSelected>>", self.on_ticker_select)
        
        # Shares Entry
        shares_lbl = ttk.Label(input_row, text="Shares Quantity", style="Card.TLabel")
        shares_lbl.grid(row=0, column=1, sticky="w", pady=(0, 5))
        
        self.shares_var = tk.StringVar()
        self.shares_entry = tk.Entry(input_row, textvariable=self.shares_var, bg=COLOR_INPUT_BG, fg=COLOR_TEXT, insertbackground=COLOR_TEXT, bd=0, font=("Segoe UI", 12), width=12)
        self.shares_entry.grid(row=1, column=1, ipady=3, sticky="w")
        
        # Display price info
        self.price_lbl = ttk.Label(action_card, text="Select a stock to see details", style="Card.TLabel", foreground=COLOR_MUTED)
        self.price_lbl.pack(anchor="w", padx=20, pady=8)

        # Action Buttons Row
        btn_row = tk.Frame(action_card, bg=COLOR_CARD)
        btn_row.pack(fill="x", padx=20, pady=(10, 20))
        
        self.add_btn = self.create_flat_button(btn_row, "Add / Update Stock", COLOR_ACCENT, self.add_or_update_stock)
        self.add_btn.pack(side="left", expand=True, fill="x", padx=(0, 5))
        
        self.delete_btn = self.create_flat_button(btn_row, "Delete", COLOR_DANGER, self.delete_stock)
        self.delete_btn.pack(side="left", expand=True, fill="x", padx=(5, 0))

        # Chart Card
        chart_card = tk.Frame(right_panel, bg=COLOR_CARD)
        chart_card.pack(fill="both", expand=True)
        
        chart_title = ttk.Label(chart_card, text="Portfolio Allocation Breakdown", style="Header.TLabel")
        chart_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        # Canvas for custom donut chart
        self.chart_canvas = tk.Canvas(chart_card, bg=COLOR_CARD, highlightthickness=0, width=380, height=200)
        self.chart_canvas.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Footer Actions (Export buttons)
        footer_frame = tk.Frame(self.root, bg=COLOR_BG)
        footer_frame.pack(fill="x", padx=30, pady=(10, 20))
        
        self.export_csv_btn = self.create_flat_button(footer_frame, "💾 Export to CSV", COLOR_INPUT_BG, self.export_csv)
        self.export_csv_btn.pack(side="left", padx=(0, 10))
        
        self.export_txt_btn = self.create_flat_button(footer_frame, "📄 Save Report (TXT)", COLOR_INPUT_BG, self.export_txt)
        self.export_txt_btn.pack(side="left")
        
        developer_lbl = ttk.Label(footer_frame, text="Antigravity Suite • High Performance", font=("Segoe UI Semibold", 9), foreground=COLOR_MUTED)
        developer_lbl.pack(side="right")

    def create_stat_card(self, parent, label, val, accent_color):
        card = tk.Frame(parent, bg=COLOR_CARD, width=200, height=80)
        card.pack(side="left", fill="both", expand=True, padx=(0, 10) if parent.winfo_children() else 0)
        card.pack_propagate(False)
        
        lbl = ttk.Label(card, text=label.upper(), style="Card.TLabel", font=("Segoe UI Semibold", 8), foreground=COLOR_MUTED)
        lbl.pack(anchor="w", padx=15, pady=(12, 2))
        
        val_lbl = ttk.Label(card, text=val, style="Card.TLabel", font=("Segoe UI", 18, "bold"), foreground=accent_color)
        val_lbl.pack(anchor="w", padx=15)
        
        return val_lbl

    def create_flat_button(self, parent, text, color, command):
        # We simulate flat modern buttons with tk.Button having zero borders and relief
        btn = tk.Button(
            parent,
            text=text,
            bg=color,
            fg="#FFFFFF",
            activebackground=COLOR_ACCENT_HOVER,
            activeforeground="#FFFFFF",
            bd=0,
            relief="flat",
            font=("Segoe UI Semibold", 10),
            padx=15,
            pady=8,
            cursor="hand2",
            command=command
        )
        # Add basic hover effect
        def on_enter(e):
            if color == COLOR_INPUT_BG:
                btn["background"] = "#33333B"
            elif color == COLOR_DANGER:
                btn["background"] = "#DC2626"
            elif color == COLOR_ACCENT:
                btn["background"] = COLOR_ACCENT_HOVER
        def on_leave(e):
            btn["background"] = color
            
        btn.bind("<Enter>", on_enter)
        btn.bind("<Leave>", on_leave)
        return btn

    def on_ticker_select(self, event=None):
        ticker = self.ticker_var.get()
        if ticker in STOCK_PRICES:
            price = STOCK_PRICES[ticker]
            owned = self.portfolio.get(ticker, 0)
            self.price_lbl.config(
                text=f"Market Price: ${price:.2f} | Current Holdings: {owned} shares",
                foreground=COLOR_SUCCESS if owned > 0 else COLOR_MUTED
            )

    def on_select_row(self, event=None):
        selected_items = self.tree.selection()
        if not selected_items:
            return
        item = selected_items[0]
        values = self.tree.item(item, "values")
        if values:
            ticker = values[0]
            # Strip formatting to get numeric quantity
            shares = str(self.portfolio.get(ticker, 0))
            self.ticker_var.set(ticker)
            self.shares_var.set(shares)
            self.on_ticker_select()

    def add_or_update_stock(self):
        ticker = self.ticker_var.get()
        shares_str = self.shares_var.get().strip()
        
        if not ticker:
            messagebox.showerror("Error", "Please select a stock symbol.")
            return
        
        try:
            shares = float(shares_str)
            if shares < 0:
                raise ValueError("Shares cannot be negative.")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid positive quantity for shares.")
            return

        if shares == 0:
            if ticker in self.portfolio:
                del self.portfolio[ticker]
        else:
            self.portfolio[ticker] = shares

        self.update_ui()
        self.shares_var.set("")
        self.on_ticker_select()
        messagebox.showinfo("Success", f"Updated {ticker} to {shares} shares!")

    def delete_stock(self):
        ticker = self.ticker_var.get()
        if not ticker:
            messagebox.showerror("Error", "Please select a stock symbol to delete.")
            return
            
        if ticker in self.portfolio:
            confirm = messagebox.askyesno("Confirm", f"Are you sure you want to remove {ticker} from your portfolio?")
            if confirm:
                del self.portfolio[ticker]
                self.update_ui()
                self.shares_var.set("")
                self.on_ticker_select()
                messagebox.showinfo("Success", f"Removed {ticker} from portfolio.")
        else:
            messagebox.showerror("Error", f"{ticker} is not in your current portfolio.")

    def update_ui(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Calculate stats
        total_value = 0.0
        portfolio_details = []
        
        for ticker, qty in self.portfolio.items():
            price = STOCK_PRICES.get(ticker, 0.0)
            value = qty * price
            total_value += value
            portfolio_details.append((ticker, price, qty, value))
            
        # Populate table
        for ticker, price, qty, val in portfolio_details:
            alloc_pct = (val / total_value * 100) if total_value > 0 else 0
            self.tree.insert("", "end", values=(
                ticker,
                f"${price:,.2f}",
                f"{qty:,.2f}",
                f"${val:,.2f}",
                f"{alloc_pct:.1f}%"
            ))
            
        # Update stat labels
        self.stat_val_total.config(text=f"${total_value:,.2f}")
        self.stat_val_assets.config(text=str(len(self.portfolio)))
        
        total_shares = sum(self.portfolio.values())
        self.stat_val_shares.config(text=f"{total_shares:,.2f}")
        
        # Redraw charts
        self.draw_donut_chart(portfolio_details, total_value)

    def draw_donut_chart(self, portfolio_details, total_value):
        canvas = self.chart_canvas
        canvas.delete("all")
        
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        
        # Fallback dimensions if UI is not fully laid out yet
        if width < 50: width = 380
        if height < 50: height = 220
        
        center_x = width // 2 - 60
        center_y = height // 2
        radius = min(center_x, center_y) - 20
        
        if radius < 20: radius = 70
        
        if not portfolio_details or total_value == 0:
            # Draw empty placeholder
            canvas.create_oval(center_x - radius, center_y - radius, center_x + radius, center_y + radius, fill=COLOR_INPUT_BG, outline="")
            canvas.create_oval(center_x - radius/2, center_y - radius/2, center_x + radius/2, center_y + radius/2, fill=COLOR_CARD, outline="")
            canvas.create_text(center_x, center_y, text="Empty Portfolio", fill=COLOR_MUTED, font=("Segoe UI Semibold", 10))
            return
            
        # Sort details by value size
        sorted_details = sorted(portfolio_details, key=lambda x: x[3], reverse=True)
        
        start_angle = 90
        legend_y = 30
        
        for idx, (ticker, price, qty, val) in enumerate(sorted_details):
            pct = val / total_value
            extent_angle = pct * 360
            color = CHART_COLORS[idx % len(CHART_COLORS)]
            
            # Draw slice
            canvas.create_arc(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                start=start_angle, extent=extent_angle,
                fill=color, outline=""
            )
            
            start_angle += extent_angle
            
            # Draw Legend
            if legend_y + 15 < height:
                legend_x = center_x + radius + 30
                canvas.create_rectangle(legend_x, legend_y, legend_x + 12, legend_y + 12, fill=color, outline="")
                canvas.create_text(legend_x + 20, legend_y + 6, text=f"{ticker} ({pct*100:.1f}%)", fill=COLOR_TEXT, anchor="w", font=("Segoe UI", 9))
                legend_y += 22

        # Draw center donut cutout
        cutout_radius = radius * 0.55
        canvas.create_oval(
            center_x - cutout_radius, center_y - cutout_radius,
            center_x + cutout_radius, center_y + cutout_radius,
            fill=COLOR_CARD, outline=""
        )

    def export_csv(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Portfolio to CSV"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, mode="w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Ticker", "Price Per Share ($)", "Shares Quantity", "Total Value ($)", "Allocation (%)"])
                
                total_val = sum(qty * STOCK_PRICES.get(ticker, 0.0) for ticker, qty in self.portfolio.items())
                
                for ticker, qty in self.portfolio.items():
                    price = STOCK_PRICES.get(ticker, 0.0)
                    val = qty * price
                    alloc = (val / total_val * 100) if total_val > 0 else 0
                    writer.writerow([ticker, f"{price:.2f}", f"{qty:.2f}", f"{val:.2f}", f"{alloc:.1f}"])
            messagebox.showinfo("Success", f"Portfolio exported successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export CSV: {e}")

    def export_txt(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
            title="Save Portfolio Report"
        )
        if not file_path:
            return
            
        try:
            with open(file_path, mode="w") as f:
                f.write("=" * 60 + "\n")
                f.write("               STOCK PORTFOLIO REPORT\n")
                f.write("=" * 60 + "\n\n")
                
                total_val = 0.0
                portfolio_details = []
                for ticker, qty in self.portfolio.items():
                    price = STOCK_PRICES.get(ticker, 0.0)
                    val = qty * price
                    total_val += val
                    portfolio_details.append((ticker, price, qty, val))
                
                f.write(f"{'Ticker':<10}{'Price ($)':<12}{'Quantity':<12}{'Total Value ($)':<16}{'Allocation':<10}\n")
                f.write("-" * 60 + "\n")
                for ticker, price, qty, val in portfolio_details:
                    alloc = (val / total_val * 100) if total_val > 0 else 0
                    f.write(f"{ticker:<10}{price:<12.2f}{qty:<12.2f}{val:<16.2f}{alloc:<10.1f}%\n")
                
                f.write("-" * 60 + "\n")
                f.write(f"Total Unique Assets: {len(self.portfolio)}\n")
                f.write(f"Total Portfolio Value: ${total_val:,.2f}\n")
                f.write("=" * 60 + "\n")
                
            messagebox.showinfo("Success", f"Report saved successfully to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save report: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PortfolioTrackerApp(root)
    # Force drawing canvas layout update
    root.update()
    app.update_ui()
    root.mainloop()
