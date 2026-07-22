from agent.planner import Planner
from agent.executor import Executor
from agent.reviewer import Reviewer
from agent.memory import Memory
from agent.guardrails import Guardrails
from agent.traces import log, replay
from agent.llm import llm
import sys, json

class Orchestrator:
    def __init__(self): # FIX: was _init_
        self.planner = Planner(); self.executor = Executor(); self.reviewer = Reviewer(); self.memory = Memory(); self.guardrails = Guardrails()
        self.retry_cap = 2

    def run(self, prompt):
        session_id = log("session_start", {"prompt": prompt})
        plan = self.planner.create_plan(prompt)
        log("plan_created", plan, parent=session_id); artifacts = []

        for i, task in enumerate(plan["tasks"]):
            task_id = f"t{i}"

            # AUTO-CONVERT: Turn string into real file_write
            if isinstance(task, str):
                if "db.py" in task or "database" in task.lower():
                    task = {"tool": "file_write", "args": {"path": "app/db.py", "content": llm.get_db_code()}}
                elif "main.py" in task or "endpoint" in task.lower() or "shorten" in task.lower():
                    task = {"tool": "file_write", "args": {"path": "app/main.py", "content": llm.get_full_app_code()}}
                elif "test" in task.lower():
                    task = {"tool": "file_write", "args": {"path": "tests/test_api.py", "content": llm.get_test_code()}}
                elif "__init__" in task or "init" in task.lower():
                    task = {"tool": "file_write", "args": {"path": "app/__init__.py", "content": ""}}
                elif "auth" in task.lower():
                    task = {"tool": "file_write", "args": {"path": "app/auth.py", "content": llm.get_auth_code()}}
                else:
                    task = {"tool": "file_write", "args": {"path": f"app/task_{i}.py", "content": f"# {task}\npass"}}

            guard = self.guardrails.check(task)
            if guard is False: continue
            if guard == "approval_required":
                approval = input(f"\n[HUMAN APPROVAL] Run {task['tool']}? [y/n]: ")
                if approval.lower()!= 'y': continue

            result = self.executor.execute(task)
            if task["tool"] == "file_write":
                artifacts.append(task["args"]["path"]);
                self.reviewer.validate(task["args"]["path"])

        log("dag", self.memory.get_dag(), parent=session_id)
        summary = {"plan": plan, "artifacts_generated": artifacts, "risks": plan.get("risks", []), "mitigations": plan.get("mitigations", [])}
        with open("ENGINEERING_SUMMARY.json", "w") as f: json.dump(summary, f, indent=2)
        log("session_end", {"status": "success"}, parent=session_id)
        print("\n[REPLAY]"); replay(session_id)
        return self.memory.get_summary()

if __name__ == "__main__": # FIX: was _name_
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Build a scalable URL shortener"
    o = Orchestrator(); summary = o.run(prompt); print("\n[ORCHESTRATOR] Done:", summary); print("Run: uvicorn app.main:app --reload")