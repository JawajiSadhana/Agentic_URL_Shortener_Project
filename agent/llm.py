import json
import os
from agent.traces import log
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

class GroqLLM:
    def __init__(self, api_key):
        self.client = Groq(api_key=api_key)
        self.token_usage = {"expensive": 0}
        self.BUDGET = 10000

    def count_tokens(self, text: str) -> int:
        return int(len(text.split()) * 1.3)

    def call(self, prompt: str, task_tool: str = "reasoning") -> dict:
        model_tier = "expensive"; tokens = self.count_tokens(prompt)
        self.token_usage[model_tier] += tokens
        log("token_usage", {"tier": model_tier, "tokens": tokens}, cost=tokens)
        log("llm_reasoning", {"steps": ["Using Groq LLM"]})

        system = """You are a senior Python engineer. Return ONLY valid JSON with complete working code.
CRITICAL RULES:
1. Build a URL shortener API using FastAPI + sqlite3 only. NO sqlalchemy.
2. Endpoints MUST be: POST /shorten, GET /{short_code}, GET /analytics/{short_code}
3. DB Table: urls(id INTEGER PRIMARY KEY, original_url TEXT, short_code TEXT UNIQUE, clicks INTEGER DEFAULT 0)
4. Generate short_code: 6 char base62 using secrets.choice from string.ascii_letters + string.digits
5. Increment clicks on every redirect
6. If prompt says "Add X to the existing URL shortener", EXTEND app/main.py and app/db.py. Do NOT create /codes endpoints
7. NO secrets, NO SECRET_KEY, NO hardcoded passwords in code
8. Paths must start with app/ or tests/

Return format:
{
  "intent": "string",
  "tasks": [{"tool": "file_write", "args": {"path": "app/db.py", "content": "FULL CODE"}}],
  "risks": [],
  "mitigations": []
}"""

        resp = self.client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(resp.choices[0].message.content)

def get_llm():
    api_key = os.getenv("GROQ_API_KEY").strip()
    if not api_key: raise ValueError("GROQ_API_KEY not found in.env")
    log("llm_init", {"mode": "groq_real"})
    return GroqLLM(api_key)

llm = get_llm()