import os, subprocess, time
from agent.traces import log
from agent.memory import Memory

class Executor:
    def __init__(self):
        # FIX: Added file_update
        self.tools = {"file_write": self.file_write, "file_update": self.file_write, "code_edit": self.code_edit, "code_search": self.code_search, "shell": self.shell, "test_runner": self.test_runner}
        self.memory = Memory()
        self.retry_cap = 2

    def execute_with_retry(self, task_id, task):
        if "file" in task.get("args", {}):
            task["args"]["path"] = task["args"].pop("file")

        for attempt in range(1, self.retry_cap+2):
            try:
                result = self.tools[task["tool"]](**task["args"])
                self.memory.save_task(task_id, None, task, result, attempt)
                return result
            except Exception as e:
                self.memory.save_retry(task_id, attempt, e)
                log("tool_error", {"tool": task["tool"], "error": str(e), "attempt": attempt})
                if attempt > self.retry_cap:
                    return f"Tool failed after {self.retry_cap} retries: {e}"
                time.sleep(2**attempt)

    def file_write(self, path, content, evidence=None):
        dir_name = os.path.dirname(path)
        if dir_name: os.makedirs(dir_name, exist_ok=True)
        open(path,"w",encoding="utf-8").write(content)
        log("tool_file_write",{"path":path}, evidence=evidence)
        return f"Written {path}"

    def code_edit(self, path, find, replace):
        if not os.path.exists(path): return f"File not found: {path}"
        code=open(path,"r",encoding="utf-8").read().replace(find,replace)
        open(path,"w",encoding="utf-8").write(code)
        log("tool_code_edit",{"path":path})
        return f"Edited {path}"

    def code_search(self, query): log("tool_code_search",{"query":query}); return "docs"
    def shell(self, command): log("tool_shell",{"command":command}); return subprocess.check_output(command,shell=True,text=True)

    def test_runner(self):
        log("tool_test_runner",{})
        try:
            out = subprocess.check_output("pytest -v", shell=True, text=True, stderr=subprocess.STDOUT)
            return out
        except subprocess.CalledProcessError as e:
            log("test_failed", {"output": e.output})
            return f"Tests failed with code {e.returncode}. Continuing..."

    def execute(self, task): return self.execute_with_retry(f"t{hash(str(task))}", task)