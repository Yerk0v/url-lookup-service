from fastapi import FastAPI, Path

MALWARE_URLS = {
    "login-secure-update.com/banking/auth",
    "free-movie-downloads.cl/installer.exe",
    "customer-support-alert.net:8080/login"
}

app = FastAPI()

@app.get("/urlinfo/1/{hostname_and_port}/{original_path_and_query_string:path}")
def get_url_info(
    hostname_and_port: str = Path(..., min_length=3, max_length=255, pattern=r"^[a-zA-Z0-9.-]+(:\d+)?$"),
    original_path_and_query_string: str = Path(...)
):
    domain_part = hostname_and_port.lower()
    full_url = f"{domain_part}/{original_path_and_query_string}".rstrip("/")
    
    if full_url in MALWARE_URLS:
        return {"status": "unsafe", "message": "Malware detected on this URL."}
    
    return {"status": "safe", "message": "URL is clean."}