import json, uuid, os
from datetime import datetime

def log(event_type, data, parent=None, cost=0, evidence=None):
    os.makedirs("logs", exist_ok=True)
    entry = {"id": str(uuid.uuid4()), "parent": parent, "timestamp": datetime.now().isoformat(), "event": event_type, "data": data, "cost": cost, "evidence": evidence or []}
    with open("logs/ENGINEERING_SUMMARY.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
    return entry["id"]

def replay(session_id):
    with open("logs/ENGINEERING_SUMMARY.jsonl") as f:
        events = [json.loads(l) for l in f if json.loads(l)["parent"]==session_id or json.loads(l)["id"]==session_id]
    for e in events: print(f"[{e['timestamp']}] {e['event']} -> {e['data']}")