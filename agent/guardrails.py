from agent.traces import log
import re
import json

class Guardrails:
    RISK_TIERS = {"file_write": "write", "code_edit": "write", "shell": "destructive", "code_search": "read", "test_runner": "read"}
    ALLOWLIST = ["app/", "tests/", "scenarios/"]
    
    def check(self, task):
        # FIX: If task is string, parse it
        if isinstance(task, str):
            try:
                task = json.loads(task)
            except:
                return False

        tool = task.get("tool"); args = str(task.get("args", {}))
        if not tool: return False

        if self.RISK_TIERS.get(tool) == "destructive":
            if "uvicorn" in args: log("guardrail_blocked", {"reason": "LLM tried to run server"}); return False
            log("guardrail_approval", task); return "approval_required"
        
        if tool in ["file_write", "code_edit"]:
            path = task["args"].get("path")
            if not path: return False
            if not any(path.startswith(p) for p in self.ALLOWLIST): log("guardrail_blocked", {"reason": "Path not allowed", "path": path}); return False
        
        if re.search(r'(sk-|api[_-]?key|password)', args, re.I): log("guardrail_blocked", {"reason": "Secret detected"}); return False
        return True