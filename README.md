# Agentic URL Shortener v2.17.4

An agentic system that build and test a FastAPI URL shortener.

## Features
- **Real LLM**: Groq `llama-3.3-70b-versatile` for code generation
- **Traces + Memory**: All tool calls and DAG saved to `logs/ENGINEERING_SUMMARY.jsonl`
- **Guardrails**: Blocks destructive tools and secret leaks
- **Ambiguity Handling**: Logs `ambiguity_auto_resolved` for vague prompts
- **Auto Testing**: Runs `pytest` and reports success/failure
- **Endpoints**: `POST /shorten`, `GET /{short_code}`, `GET /analytics/{short_code}`

## Setup

#Install dependencies
```bash
pip install -r requirements.txt

## Run
python eval.py
pytest -v
uvicorn app.main:app --reload
