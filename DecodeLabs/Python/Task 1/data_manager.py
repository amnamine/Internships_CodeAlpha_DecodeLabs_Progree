import json
import csv
import os
from typing import List, Dict, Any
from tkinter import filedialog, messagebox

class DataManager:
    """Handles JSON and CSV data import/export and backup tasks."""
    def __init__(self, db_manager):
        self.db = db_manager

    def export_to_json(self, filepath: str = None) -> bool:
        tasks = self.db.get_tasks(filter_status="All")
        if not filepath:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
                title="Export Tasks to JSON"
            )
        if not filepath:
            return False

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(tasks, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Export Success", f"Successfully exported {len(tasks)} tasks to JSON:\n{filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting tasks to JSON:\n{e}")
            return False

    def export_to_csv(self, filepath: str = None) -> bool:
        tasks = self.db.get_tasks(filter_status="All")
        if not filepath:
            filepath = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
                title="Export Tasks to CSV"
            )
        if not filepath:
            return False

        try:
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "ID", "Title", "Status", "Priority", "Category",
                    "Due Date", "Due Time", "Subtasks Completed", "Total Subtasks", "Created At", "Notes"
                ])
                for t in tasks:
                    writer.writerow([
                        t['id'],
                        t['title'],
                        t['status'],
                        t['priority'],
                        t.get('category_name', ''),
                        t.get('due_date', ''),
                        t.get('due_time', ''),
                        t.get('completed_subtasks', 0),
                        t.get('total_subtasks', 0),
                        t.get('created_at', ''),
                        t.get('notes', '')
                    ])
            messagebox.showinfo("Export Success", f"Successfully exported {len(tasks)} tasks to CSV:\n{filepath}")
            return True
        except Exception as e:
            messagebox.showerror("Export Failed", f"Error exporting tasks to CSV:\n{e}")
            return False

    def seed_sample_data(self):
        """Seed sample tasks with subtasks and categories for testing/demo."""
        categories = self.db.get_all_categories()
        work_cat = next((c['id'] for c in categories if c['name'] == 'Work'), None)
        edu_cat = next((c['id'] for c in categories if c['name'] == 'Education'), None)
        health_cat = next((c['id'] for c in categories if c['name'] == 'Health & Fitness'), None)

        sample_tasks = [
            {
                "title": "Complete Python GUI To-Do List Assignment",
                "notes": "Integrate Tkinter, SQLite, custom animations, Pomodoro timer, and statistics dashboard.",
                "category_id": edu_cat,
                "priority": "Urgent",
                "status": "In Progress",
                "due_date": "2026-08-05",
                "due_time": "23:59",
                "subtasks": ["Set up SQLite DB schema", "Design Dark/Light design system", "Build Canvas progress ring & charts", "Test Pomodoro session logger"]
            },
            {
                "title": "Prepare Q3 Productivity Report",
                "notes": "Summarize task velocity, completion rate, and project milestones for team sync.",
                "category_id": work_cat,
                "priority": "High",
                "status": "Pending",
                "due_date": "2026-08-07",
                "due_time": "15:00",
                "subtasks": ["Gather metrics from SQLite", "Draft summary charts", "Export CSV report"]
            },
            {
                "title": "Morning 5K Run & Stretching Routine",
                "notes": "Maintain health streak and track hydration levels.",
                "category_id": health_cat,
                "priority": "Medium",
                "status": "Completed",
                "due_date": "2026-08-03",
                "due_time": "07:30",
                "subtasks": ["5K Warmup", "Hydrate 1L Water", "Post-workout stretch"]
            }
        ]

        for task in sample_tasks:
            self.db.add_task(
                title=task['title'],
                notes=task['notes'],
                category_id=task['category_id'],
                priority=task['priority'],
                status=task['status'],
                due_date=task['due_date'],
                due_time=task['due_time'],
                subtasks=task['subtasks']
            )
