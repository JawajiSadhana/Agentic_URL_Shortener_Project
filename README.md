# Agentic URL Shortener
## Run
pip install -r requirements.txt
python eval.py
pytest -v
uvicorn app.main:app --reload