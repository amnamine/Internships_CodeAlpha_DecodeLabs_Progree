"""
database.py - Database Layer for ApexExpense
Manages SQLite database connection, tables creation, initial data seeding,
transaction CRUD, category budgets, recurring expenses, and statistical queries.
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

DB_FILE = os.path.join(os.path.dirname(__file__), "expenses.db")

class DatabaseManager:
    def __init__(self, db_path=DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        """Creates database schema if not present and seeds sample data."""
        first_run = not os.path.exists(self.db_path)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    icon TEXT NOT NULL,
                    color TEXT NOT NULL,
                    monthly_budget REAL DEFAULT 0.0
                )
            """)
            
            # Expenses / Income Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category_id INTEGER NOT NULL,
                    payment_method TEXT NOT NULL,
                    date TEXT NOT NULL,
                    notes TEXT,
                    is_income INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )
            """)
            
            # Savings Goals Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS savings_goals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    target_amount REAL NOT NULL,
                    current_amount REAL DEFAULT 0.0,
                    target_date TEXT,
                    color TEXT DEFAULT '#10B981'
                )
            """)
            
            # Recurring Transactions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS recurring_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    amount REAL NOT NULL,
                    category_id INTEGER NOT NULL,
                    frequency TEXT NOT NULL, -- Daily, Weekly, Monthly, Yearly
                    last_processed TEXT,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)
            
            conn.commit()

        if first_run or self.is_empty():
            self.seed_default_data()

    def is_empty(self):
        with self.get_connection() as conn:
            count = conn.cursor().execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
            return count == 0

    def seed_default_data(self):
        """Seeds categories, savings goals, and realistic transactions."""
        from theme import CATEGORY_PRESETS
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Seed Categories with monthly budgets
            category_map = {}
            default_budgets = {
                "Food & Dining": 650.0,
                "Transport & Fuel": 300.0,
                "Shopping & Retail": 450.0,
                "Bills & Utilities": 500.0,
                "Entertainment & Fun": 250.0,
                "Health & Fitness": 150.0,
                "Travel & Vacation": 400.0,
                "Education & Courses": 200.0,
                "Salary & Income": 0.0,
                "Investment & Stocks": 0.0,
                "Miscellaneous": 200.0
            }
            
            for cat_name, info in CATEGORY_PRESETS.items():
                budget = default_budgets.get(cat_name, 300.0)
                cursor.execute(
                    "INSERT OR IGNORE INTO categories (name, icon, color, monthly_budget) VALUES (?, ?, ?, ?)",
                    (cat_name, info["icon"], info["color"], budget)
                )
                
            cursor.execute("SELECT id, name FROM categories")
            for row in cursor.fetchall():
                category_map[row["name"]] = row["id"]
                
            # Seed Savings Goals
            cursor.execute("""
                INSERT INTO savings_goals (title, target_amount, current_amount, target_date, color)
                VALUES 
                ('Emergency Fund', 5000.0, 3200.0, '2026-12-31', '#10B981'),
                ('New Laptop / Tech', 2500.0, 1450.0, '2026-09-30', '#6366F1'),
                ('Summer Vacation', 3500.0, 1800.0, '2026-08-15', '#06B6D4')
            """)
            
            # Seed Realistic Expenses over past 30 days
            today = datetime.now()
            sample_expenses = [
                ("Whole Foods Grocery Shopping", 124.50, "Food & Dining", "💳 Credit Card", 0),
                ("Monthly Salary Credit", 4200.00, "Salary & Income", "🏦 Bank Transfer", 1),
                ("Gasoline Refill", 48.00, "Transport & Fuel", "💳 Credit Card", 0),
                ("Netflix & Spotify Subscription", 24.99, "Bills & Utilities", "📱 PayPal / E-Wallet", 0),
                ("Electricity & Water Bill", 135.20, "Bills & Utilities", "🏦 Bank Transfer", 0),
                ("Dinner at Italian Bistro", 86.40, "Food & Dining", "💳 Credit Card", 0),
                ("Amazon Tech Accessories", 65.99, "Shopping & Retail", "💳 Credit Card", 0),
                ("Gym Membership Fee", 45.00, "Health & Fitness", "💳 Credit Card", 0),
                ("Weekend Movie Tickets & Snacks", 38.50, "Entertainment & Fun", "💵 Cash", 0),
                ("Stock Portfolio Investment", 500.00, "Investment & Stocks", "🏦 Bank Transfer", 0),
                ("Pharmacy & Vitamins", 32.75, "Health & Fitness", "💳 Credit Card", 0),
                ("Uber Ride to Airport", 42.10, "Transport & Fuel", "💳 Credit Card", 0),
                ("Coffee Shop & Bakery", 14.80, "Food & Dining", "💵 Cash", 0),
                ("Online Python Certification", 89.00, "Education & Courses", "📱 PayPal / E-Wallet", 0),
                ("Clothing & Shoes", 142.00, "Shopping & Retail", "💳 Credit Card", 0),
                ("Freelance Web Design Payout", 650.00, "Salary & Income", "🏦 Bank Transfer", 1),
                ("Weekend Getaway Hotel Deposit", 210.00, "Travel & Vacation", "💳 Credit Card", 0),
                ("Supermarket Essentials", 78.30, "Food & Dining", "💳 Credit Card", 0),
                ("Car Maintenance & Oil Change", 115.00, "Transport & Fuel", "💳 Credit Card", 0)
            ]
            
            for i, (title, amount, cat_name, pay_method, is_inc) in enumerate(sample_expenses):
                days_ago = random.randint(0, 28)
                tx_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
                cat_id = category_map.get(cat_name, 1)
                cursor.execute(
                    "INSERT INTO expenses (title, amount, category_id, payment_method, date, notes, is_income) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (title, amount, cat_id, pay_method, tx_date, "Sample transaction", is_inc)
                )

            conn.commit()

    # --- EXPENSE CRUD ---
    def add_expense(self, title, amount, category_id, payment_method, date_str, notes="", is_income=0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO expenses (title, amount, category_id, payment_method, date, notes, is_income) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (title, float(amount), int(category_id), payment_method, date_str, notes, int(is_income))
            )
            conn.commit()
            return cursor.lastrowid

    def update_expense(self, expense_id, title, amount, category_id, payment_method, date_str, notes="", is_income=0):
        with self.get_connection() as conn:
            conn.cursor().execute(
                """UPDATE expenses 
                   SET title=?, amount=?, category_id=?, payment_method=?, date=?, notes=?, is_income=?
                   WHERE id=?""",
                (title, float(amount), int(category_id), payment_method, date_str, notes, int(is_income), int(expense_id))
            )
            conn.commit()

    def delete_expense(self, expense_id):
        with self.get_connection() as conn:
            conn.cursor().execute("DELETE FROM expenses WHERE id=?", (int(expense_id),))
            conn.commit()

    def get_expenses(self, search="", category_id=None, month=None, year=None, is_income=None):
        with self.get_connection() as conn:
            query = """
                SELECT e.*, c.name as category_name, c.icon as category_icon, c.color as category_color
                FROM expenses e
                JOIN categories c ON e.category_id = c.id
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (e.title LIKE ? OR e.notes LIKE ?)"
                params.extend([f"%{search}%", f"%{search}%"])
            if category_id and category_id != "All":
                query += " AND e.category_id = ?"
                params.append(category_id)
            if is_income is not None:
                query += " AND e.is_income = ?"
                params.append(is_income)
            if month and year:
                query += " AND strftime('%m', e.date) = ? AND strftime('%Y', e.date) = ?"
                params.extend([f"{int(month):02d}", str(year)])
                
            query += " ORDER BY e.date DESC, e.id DESC"
            return conn.cursor().execute(query, params).fetchall()

    # --- CATEGORY & BUDGET METHODS ---
    def get_categories(self):
        with self.get_connection() as conn:
            return conn.cursor().execute("SELECT * FROM categories ORDER BY name ASC").fetchall()

    def add_category(self, name, icon, color, monthly_budget=0.0):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO categories (name, icon, color, monthly_budget) VALUES (?, ?, ?, ?)",
                (name, icon, color, float(monthly_budget))
            )
            conn.commit()

    def update_category_budget(self, category_id, budget):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "UPDATE categories SET monthly_budget = ? WHERE id = ?",
                (float(budget), int(category_id))
            )
            conn.commit()

    # --- SAVINGS GOALS METHODS ---
    def get_savings_goals(self):
        with self.get_connection() as conn:
            return conn.cursor().execute("SELECT * FROM savings_goals").fetchall()

    def add_savings_goal(self, title, target_amount, current_amount, target_date, color):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "INSERT INTO savings_goals (title, target_amount, current_amount, target_date, color) VALUES (?, ?, ?, ?, ?)",
                (title, float(target_amount), float(current_amount), target_date, color)
            )
            conn.commit()

    def deposit_savings_goal(self, goal_id, amount):
        with self.get_connection() as conn:
            conn.cursor().execute(
                "UPDATE savings_goals SET current_amount = current_amount + ? WHERE id = ?",
                (float(amount), int(goal_id))
            )
            conn.commit()

    # --- AGGREGATE CALCULATIONS & METRICS ---
    def get_summary_stats(self):
        """Calculates total income, total spent (accumulator sum), net balance, and count."""
        now = datetime.now()
        current_month = f"{now.year}-{now.month:02d}"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Total Income (all time)
            total_income = cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE is_income = 1").fetchone()[0]
            
            # Total Spent Accumulator (all time)
            total_spent = cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE is_income = 0").fetchone()[0]
            
            # Monthly Spent (current month)
            monthly_spent = cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE is_income = 0 AND strftime('%Y-%m', date) = ?",
                (current_month,)
            ).fetchone()[0]
            
            # Monthly Income (current month)
            monthly_income = cursor.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE is_income = 1 AND strftime('%Y-%m', date) = ?",
                (current_month,)
            ).fetchone()[0]

            net_balance = total_income - total_spent
            transaction_count = cursor.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
            
            return {
                "total_income": total_income,
                "total_spent": total_spent,
                "net_balance": net_balance,
                "monthly_spent": monthly_spent,
                "monthly_income": monthly_income,
                "transaction_count": transaction_count
            }

    def get_category_spending_breakdown(self, month=None, year=None):
        """Returns spend per category with total budget comparison."""
        with self.get_connection() as conn:
            query = """
                SELECT c.id, c.name, c.icon, c.color, c.monthly_budget,
                       COALESCE(SUM(e.amount), 0) as total_spent
                FROM categories c
                LEFT JOIN expenses e ON c.id = e.category_id AND e.is_income = 0
            """
            params = []
            if month and year:
                query += " AND strftime('%m', e.date) = ? AND strftime('%Y', e.date) = ?"
                params.extend([f"{int(month):02d}", str(year)])
                
            query += " GROUP BY c.id ORDER BY total_spent DESC"
            return conn.cursor().execute(query, params).fetchall()

    def get_daily_spending_trend(self, days=14):
        """Returns daily totals for the last N days."""
        today = datetime.now().date()
        start_date = today - timedelta(days=days - 1)
        
        with self.get_connection() as conn:
            rows = conn.cursor().execute(
                """SELECT date, SUM(amount) as daily_total
                   FROM expenses
                   WHERE is_income = 0 AND date >= ?
                   GROUP BY date
                   ORDER BY date ASC""",
                (start_date.strftime("%Y-%m-%d"),)
            ).fetchall()
            
            dict_data = {row["date"]: row["daily_total"] for row in rows}
            
            result = []
            for d in range(days):
                curr = (start_date + timedelta(days=d)).strftime("%Y-%m-%d")
                result.append({"date": curr, "amount": dict_data.get(curr, 0.0)})
                
            return result
