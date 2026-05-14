from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_known_malware_url():
    resp = client.get(
        "/urlinfo/1/login-secure-update.com/banking/auth"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"


def test_known_safe_domain():
    resp = client.get(
        "/urlinfo/1/google.com/search"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "safe"


def test_unknown_url():
    resp = client.get(
        "/urlinfo/1/random-domain-123.com/test"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unknown"


def test_exact_malware_match():
    resp = client.get(
        "/urlinfo/1/free-movie-downloads.cl/installer.exe"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"


def test_similar_but_not_exact_url():
    resp = client.get(
        "/urlinfo/1/free-movie-downloads.cl/installer.ex"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unknown"


def test_port_based_malware_detection():
    resp = client.get(
        "/urlinfo/1/customer-support-alert.net:8080/login"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"


def test_different_port_not_malware():
    resp = client.get(
        "/urlinfo/1/customer-support-alert.net:9090/login"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unknown"


def test_trailing_slash_normalization():
    resp = client.get(
        "/urlinfo/1/login-secure-update.com/banking/auth"
    )

    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"


def test_missing_hostname():
    resp = client.get("/urlinfo/1/")
    assert resp.status_code == 404