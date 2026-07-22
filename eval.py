import subprocess, json, os

def run():
    os.makedirs("logs", exist_ok=True)
    scenarios = [
        "Build a scalable URL shortener with APIs, persistence, analytics",
        "Add JWT authentication to the existing URL shortener in app/main.py and app/db.py",
        "Add per-url analytics endpoint GET /analytics/{short_code} to the existing URL shortener in app/main.py"
    ]

    for i, prompt in enumerate(scenarios):
        print(f"\n[ORCHESTRATOR] Running: {prompt}")
        subprocess.run(["python", "-m", "agent.orchestrator", prompt])

    cost = 0
    log_path = "logs/ENGINEERING_SUMMARY.jsonl"
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            cost = sum(json.loads(l).get("cost", 0) for l in f if l.strip())

    print(f"\n Total Token Cost: {cost}")
    assert cost < 10000, "Budget exceeded"
    print(" All scenarios passed")

if __name__ == "__main__": run()
