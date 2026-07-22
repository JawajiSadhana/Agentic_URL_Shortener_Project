from agent.traces import log
class Reviewer:
    def validate(self, artifact_path):
        log("reviewer_start", {"path": artifact_path})
        code = open(artifact_path, "r", encoding="utf-8").read()
        checks = {
            "has_clicks": "clicks" in code, 
            "has_endpoints": "/shorten" in code or "/analytics" in code
        }
        passed = checks["has_clicks"] and checks["has_endpoints"]
        result = {"passed": passed, "checks": checks}
        log("reviewer_done", result)
        return result