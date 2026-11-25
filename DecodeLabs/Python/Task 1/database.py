import sqlite3
import os
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional

DB_FILE = "taskmaster_pro.db"

class DatabaseManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def init_db(self):
        """Initialize all database tables and seed initial default data."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Categories Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT NOT NULL DEFAULT '#4F46E5',
                    icon TEXT NOT NULL DEFAULT '📁'
                );
            """)

            # Tasks Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    notes TEXT,
                    category_id INTEGER,
                    priority TEXT NOT NULL DEFAULT 'Medium', -- 'Urgent', 'High', 'Medium', 'Low'
                    status TEXT NOT NULL DEFAULT 'Pending',  -- 'Pending', 'In Progress', 'Completed', 'Archived'
                    due_date TEXT,
                    due_time TEXT,
                    reminder_datetime TEXT,
                    created_at TEXT NOT NULL,
                    completed_at TEXT,
                    estimated_pomodoros INTEGER DEFAULT 1,
                    completed_pomodoros INTEGER DEFAULT 0,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
                );
            """)

            # Subtasks Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subtasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    is_completed INTEGER NOT NULL DEFAULT 0,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                );
            """)

            # Tags Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT NOT NULL DEFAULT '#6B7280'
                );
            """)

            # Task-Tag Junction Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_tags (
                    task_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (task_id, tag_id),
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                );
            """)

            # Pomodoro Sessions Table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pomodoro_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    duration_minutes INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE SET NULL
                );
            """)

            # Default Categories
            default_categories = [
                ('Work', '#6366F1', '💼'),
                ('Personal', '#EC4899', '👤'),
                ('Health & Fitness', '#10B981', '🏋️'),
                ('Education', '#F59E0B', '📚'),
                ('Finance', '#14B8A6', '💰'),
                ('Shopping', '#8B5CF6', '🛒')
            ]
            for name, color, icon in default_categories:
                cursor.execute("""
                    INSERT OR IGNORE INTO categories (name, color, icon) VALUES (?, ?, ?)
                """, (name, color, icon))

            # Default Tags
            default_tags = [
                ('Urgent', '#EF4444'),
                ('DeepWork', '#8B5CF6'),
                ('Quick', '#10B981'),
                ('Planning', '#3B82F6')
            ]
            for name, color in default_tags:
                cursor.execute("""
                    INSERT OR IGNORE INTO tags (name, color) VALUES (?, ?)
                """, (name, color))

            conn.commit()

    # --- CATEGORY OPERATIONS ---
    def get_all_categories(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM categories ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def add_category(self, name: str, color: str, icon: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO categories (name, color, icon) VALUES (?, ?, ?)", (name, color, icon))
            conn.commit()
            return cursor.lastrowid

    # --- TAG OPERATIONS ---
    def get_all_tags(self) -> List[Dict[str, Any]]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tags ORDER BY name ASC")
            return [dict(row) for row in cursor.fetchall()]

    def add_tag(self, name: str, color: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO tags (name, color) VALUES (?, ?)", (name, color))
            conn.commit()
            return cursor.lastrowid

    # --- TASK OPERATIONS ---
    def add_task(self, title: str, notes: str = "", category_id: Optional[int] = None,
                 priority: str = "Medium", status: str = "Pending", due_date: Optional[str] = None,
                 due_time: Optional[str] = None, estimated_pomodoros: int = 1,
                 tag_ids: List[int] = None, subtasks: List[str] = None) -> int:
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tasks (title, notes, category_id, priority, status, due_date, due_time, created_at, estimated_pomodoros)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, notes, category_id, priority, status, due_date, due_time, created_at, estimated_pomodoros))
            task_id = cursor.lastrowid

            if tag_ids:
                for tid in tag_ids:
                    cursor.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, tid))

            if subtasks:
                for st in subtasks:
                    if st.strip():
                        cursor.execute("INSERT INTO subtasks (task_id, title) VALUES (?, ?)", (task_id, st.strip()))

            conn.commit()
            return task_id

    def update_task(self, task_id: int, title: str, notes: str, category_id: Optional[int],
                    priority: str, status: str, due_date: Optional[str], due_time: Optional[str],
                    estimated_pomodoros: int, tag_ids: List[int] = None) -> None:
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == 'Completed' else None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks
                SET title = ?, notes = ?, category_id = ?, priority = ?, status = ?,
                    due_date = ?, due_time = ?, estimated_pomodoros = ?,
                    completed_at = CASE WHEN ? = 'Completed' AND completed_at IS NULL THEN ? ELSE completed_at END
                WHERE id = ?
            """, (title, notes, category_id, priority, status, due_date, due_time, estimated_pomodoros, status, completed_at, task_id))

            # Update tags
            cursor.execute("DELETE FROM task_tags WHERE task_id = ?", (task_id,))
            if tag_ids:
                for tid in tag_ids:
                    cursor.execute("INSERT INTO task_tags (task_id, tag_id) VALUES (?, ?)", (task_id, tid))

            conn.commit()

    def set_task_status(self, task_id: int, status: str) -> None:
        completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S") if status == 'Completed' else None
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tasks
                SET status = ?, completed_at = ?
                WHERE id = ?
            """, (status, completed_at, task_id))
            conn.commit()

    def delete_task(self, task_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            conn.commit()

    def get_tasks(self, search_query: str = "", filter_status: str = "All",
                  category_id: Optional[int] = None, priority_filter: str = "All",
                  sort_by: str = "due_date") -> List[Dict[str, Any]]:
        query = """
            SELECT t.*, c.name as category_name, c.color as category_color, c.icon as category_icon,
                   (SELECT COUNT(*) FROM subtasks WHERE task_id = t.id) as total_subtasks,
                   (SELECT COUNT(*) FROM subtasks WHERE task_id = t.id AND is_completed = 1) as completed_subtasks
            FROM tasks t
            LEFT JOIN categories c ON t.category_id = c.id
            WHERE 1=1
        """
        params = []

        if search_query:
            query += " AND (t.title LIKE ? OR t.notes LIKE ?)"
            params.extend([f"%{search_query}%", f"%{search_query}%"])

        today_str = date.today().strftime("%Y-%m-%d")

        if filter_status == "Active":
            query += " AND t.status IN ('Pending', 'In Progress')"
        elif filter_status == "Completed":
            query += " AND t.status = 'Completed'"
        elif filter_status == "Archived":
            query += " AND t.status = 'Archived'"
        elif filter_status == "Today":
            query += " AND t.due_date = ? AND t.status != 'Archived'"
            params.append(today_str)
        elif filter_status == "Upcoming":
            query += " AND t.due_date > ? AND t.status != 'Archived'"
            params.append(today_str)
        elif filter_status == "Overdue":
            query += " AND t.due_date < ? AND t.status IN ('Pending', 'In Progress')"
            params.append(today_str)

        if category_id:
            query += " AND t.category_id = ?"
            params.append(category_id)

        if priority_filter != "All":
            query += " AND t.priority = ?"
            params.append(priority_filter)

        # Sorting logic
        if sort_by == "priority":
            query += " ORDER BY CASE t.priority WHEN 'Urgent' THEN 1 WHEN 'High' THEN 2 WHEN 'Medium' THEN 3 WHEN 'Low' THEN 4 END ASC"
        elif sort_by == "title":
            query += " ORDER BY t.title ASC"
        elif sort_by == "created":
            query += " ORDER BY t.created_at DESC"
        else: # default due_date
            query += " ORDER BY CASE WHEN t.due_date IS NULL OR t.due_date = '' THEN 1 ELSE 0 END, t.due_date ASC, t.due_time ASC"

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            tasks = [dict(row) for row in cursor.fetchall()]

            # Fetch tags and subtasks for each task
            for t in tasks:
                cursor.execute("""
                    SELECT tag.* FROM tags tag
                    JOIN task_tags tt ON tag.id = tt.tag_id
                    WHERE tt.task_id = ?
                """, (t['id'],))
                t['tags'] = [dict(r) for r in cursor.fetchall()]

                cursor.execute("SELECT * FROM subtasks WHERE task_id = ? ORDER BY id ASC", (t['id'],))
                t['subtask_list'] = [dict(r) for r in cursor.fetchall()]

            return tasks

    def get_task_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        tasks = self.get_tasks()
        for t in tasks:
            if t['id'] == task_id:
                return t
        return None

    # --- SUBTASK OPERATIONS ---
    def add_subtask(self, task_id: int, title: str) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO subtasks (task_id, title) VALUES (?, ?)", (task_id, title))
            conn.commit()
            return cursor.lastrowid

    def toggle_subtask(self, subtask_id: int, is_completed: bool) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE subtasks SET is_completed = ? WHERE id = ?", (1 if is_completed else 0, subtask_id))
            conn.commit()

    def delete_subtask(self, subtask_id: int) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subtasks WHERE id = ?", (subtask_id,))
            conn.commit()

    # --- POMODORO LOGS ---
    def log_pomodoro_session(self, task_id: Optional[int], duration: int = 25):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO pomodoro_logs (task_id, duration_minutes, completed_at) VALUES (?, ?, ?)",
                           (task_id, duration, now_str))
            if task_id:
                cursor.execute("UPDATE tasks SET completed_pomodoros = completed_pomodoros + 1 WHERE id = ?", (task_id,))
            conn.commit()

    # --- ANALYTICS / DASHBOARD QUERIES ---
    def get_dashboard_stats(self) -> Dict[str, Any]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status != 'Archived'")
            total_tasks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'Completed'")
            completed_tasks = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('Pending', 'In Progress')")
            pending_tasks = cursor.fetchone()[0]

            today_str = date.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM tasks WHERE due_date < ? AND status IN ('Pending', 'In Progress')", (today_str,))
            overdue_tasks = cursor.fetchone()[0]

            # Category Breakdown
            cursor.execute("""
                SELECT c.name, c.color, COUNT(t.id) as count
                FROM categories c
                LEFT JOIN tasks t ON c.id = t.category_id AND t.status != 'Archived'
                GROUP BY c.id
                HAVING count > 0
            """)
            category_stats = [dict(row) for row in cursor.fetchall()]

            # Last 7 Days Activity
            weekly_activity = []
            for i in range(6, -1, -1):
                day_date = date.today() - timedelta(days=i)
                day_str = day_date.strftime("%Y-%m-%d")
                cursor.execute("SELECT COUNT(*) FROM tasks WHERE DATE(completed_at) = ?", (day_str,))
                completed_count = cursor.fetchone()[0]
                weekly_activity.append({
                    'day_name': day_date.strftime("%a"),
                    'date': day_str,
                    'count': completed_count
                })

            completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0

            return {
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'pending_tasks': pending_tasks,
                'overdue_tasks': overdue_tasks,
                'completion_rate': round(completion_rate, 1),
                'category_stats': category_stats,
                'weekly_activity': weekly_activity
            }
