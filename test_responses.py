from fastapi.testclient import TestClient
from main import app


client = TestClient(app)


def test_host_only_safe_when_only_path_listed():
    # Malware entry has path; host-only should be safe
    resp = client.get("/urlinfo/1/login-secure-update.com/")
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "safe"


def test_host_only_safe():
    resp = client.get("/urlinfo/1/example.com/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "safe"


def test_path_unsafe_trailing_slash():
    resp = client.get("/urlinfo/1/login-secure-update.com/banking/auth/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"


def test_path_safe_different_path():
    resp = client.get("/urlinfo/1/login-secure-update.com/other")
    assert resp.status_code == 200
    assert resp.json()["status"] == "safe"


def test_port_in_hostname_malware_and_other_port_safe():
    # Exact port 8080 with path is malware
    resp = client.get("/urlinfo/1/customer-support-alert.net:8080/login")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"
    # Different port should be safe (not in list)
    resp2 = client.get("/urlinfo/1/customer-support-alert.net:9090/login")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "safe"


def test_query_string_ignored_for_lookup():
    # Query parameters should not affect the lookup result with current logic
    resp = client.get("/urlinfo/1/login-secure-update.com/banking/auth?x=1&y=2")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"


def test_missing_hostname_results_in_404():
    resp = client.get("/urlinfo/1/")
    assert resp.status_code == 404


def test_file_exact_malware_and_similar_safe():
    # Exact malware file path
    resp = client.get("/urlinfo/1/free-movie-downloads.cl/installer.exe")
    assert resp.status_code == 200
    assert resp.json()["status"] == "unsafe"
    # Similar but not exact
    resp2 = client.get("/urlinfo/1/free-movie-downloads.cl/installer.ex")
    assert resp2.status_code == 200
    assert resp2.json()["status"] == "safe"
