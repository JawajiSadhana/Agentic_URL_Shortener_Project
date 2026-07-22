import sys, os, uuid
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from app.main import app

c = TestClient(app)

def test_shorten():
    r = c.post("/shorten", params={"url": f"https://google.com/{uuid.uuid4()}"})
    assert r.status_code == 200
    assert "short_code" in r.json()
    return r.json()["short_code"]

def test_redirect():
    code = test_shorten()
    r = c.get(f"/{code}", follow_redirects=False)
    assert r.status_code in [302, 307]

def test_analytics():
    code = test_shorten()
    r = c.get(f"/analytics/{code}")
    assert r.status_code == 200
    assert r.json()["clicks"] == 0