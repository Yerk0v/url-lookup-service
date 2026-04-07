from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_safe_url_like_google():
    response = client.get("/urlinfo/1/google.com/search?q=cats")
    assert response.status_code == 200
    assert response.json() == {"status": "safe", "message": "URL is clean."}

def test_unsafe_malware_url():
    response = client.get("/urlinfo/1/login-secure-update.com/banking/auth")
    assert response.status_code == 200
    assert response.json() == {"status": "unsafe", "message": "Malware detected on this URL."}

def test_weird_request_is_blocked():
    response = client.get("/urlinfo/1/b@d_h0stn@me!/path")
    assert response.status_code == 422