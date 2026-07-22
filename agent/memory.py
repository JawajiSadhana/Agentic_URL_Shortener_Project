import sqlite3, json
from datetime import datetime
class Memory:
    def __init__(self): # FIX: was _init_
        self.conn = sqlite3.connect("agent_memory.db")
        self.conn.execute("CREATE TABLE IF NOT EXISTS tasks(id INTEGER PRIMARY KEY, task_id TEXT, parent_id TEXT, timestamp TEXT, tool TEXT, status TEXT, attempt INT, details TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS retries(id INTEGER PRIMARY KEY, task_id TEXT, attempt INT, error TEXT, timestamp TEXT)")
        self.conn.execute("CREATE TABLE IF NOT EXISTS assumptions(id INTEGER PRIMARY KEY, key TEXT, value TEXT, timestamp TEXT)")
        self.conn.commit()
    def save_task(self, task_id, parent_id, task, result, attempt=1): self.conn.execute("INSERT INTO tasks(task_id, parent_id, timestamp, tool, status, attempt, details) VALUES(?,?,?,?,?,?,?)",(task_id, parent_id, datetime.now().isoformat(), task["tool"], "done", attempt, json.dumps(result))); self.conn.commit()
    def save_retry(self, task_id, attempt, error): self.conn.execute("INSERT INTO retries(task_id, attempt, error, timestamp) VALUES(?,?,?,?)",(task_id, attempt, str(error), datetime.now().isoformat())); self.conn.commit()
    def get_dag(self): rows = self.conn.execute("SELECT task_id, parent_id, tool FROM tasks").fetchall(); return [{"id":r[0], "parent":r[1], "tool":r[2]} for r in rows]
    def get_summary(self): tasks = self.conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]; retries = self.conn.execute("SELECT COUNT(*) FROM retries").fetchone()[0]; return {"tasks_done": tasks, "retries": retries, "dag_nodes": len(self.get_dag())}