import sqlite3
import string
import secrets

def get_db():
    return sqlite3.connect('urls.db')

def create_table(db):
    cursor = db.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS urls (id INTEGER PRIMARY KEY, original_url TEXT, short_code TEXT UNIQUE, clicks INTEGER DEFAULT 0)')
    db.commit()

def create_short_code(db):
    while True:
        short_code = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(6))
        cursor = db.cursor()
        cursor.execute('SELECT * FROM urls WHERE short_code = ?', (short_code,))
        if cursor.fetchone() is None:
            return short_code

def create_url(db, url, short_code):
    cursor = db.cursor()
    cursor.execute('INSERT INTO urls (original_url, short_code) VALUES (?, ?)', (url, short_code))
    db.commit()

def get_url(db, short_code):
    cursor = db.cursor()
    cursor.execute('SELECT original_url FROM urls WHERE short_code = ?', (short_code,))
    row = cursor.fetchone()
    return row[0] if row else None

def increment_clicks(db, short_code):
    cursor = db.cursor()
    cursor.execute('UPDATE urls SET clicks = clicks + 1 WHERE short_code = ?', (short_code,))
    db.commit()
