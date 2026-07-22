from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
import sqlite3
import string
import secrets

app = FastAPI()

DB_NAME = "urls.db"

def get_db():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False) # FIX: thread safe
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS urls
                 (id INTEGER PRIMARY KEY, original_url TEXT, short_code TEXT UNIQUE, clicks INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db() # run once on startup

def generate_short_code():
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))

@app.post("/shorten")
def shorten_url(url: str):
    conn = get_db()
    c = conn.cursor()
    short_code = generate_short_code()
    # collision check
    while True:
        c.execute('SELECT * FROM urls WHERE short_code=?', (short_code,))
        if not c.fetchone():
            break
        short_code = generate_short_code()

    c.execute("INSERT INTO urls (original_url, short_code) VALUES (?,?)", (url, short_code))
    conn.commit()
    conn.close()
    return {"short_code": short_code}

@app.get("/{short_code}")
def redirect_to_original_url(short_code: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT original_url, clicks FROM urls WHERE short_code=?', (short_code,))
    result = c.fetchone()
    if result:
        original_url, clicks = result
        c.execute('UPDATE urls SET clicks=? WHERE short_code=?', (clicks + 1, short_code))
        conn.commit()
        conn.close()
        return RedirectResponse(original_url)
    else:
        conn.close()
        raise HTTPException(status_code=404, detail="URL not found")

@app.get("/analytics/{short_code}")
def get_analytics(short_code: str):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT clicks FROM urls WHERE short_code=?', (short_code,))
    result = c.fetchone()
    conn.close()
    if result:
        return {"clicks": result[0]}
    else:
        raise HTTPException(status_code=404, detail="URL not found")
