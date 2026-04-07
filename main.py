from fastapi import FastAPI

malware_urls = {
    "www.example.site.cl", 
    "www.example.site.2.cl/badpath", 
    "www.example.site.3.com"
}

app = FastAPI()

@app.get("/urlinfo/1/{hostname_and_port}/{original_path_and_query_string:path}")
def get_url_info(hostname_and_port: str, original_path_and_query_string: str):
    
    full_url = f"{hostname_and_port}/{original_path_and_query_string}"
    full_url = full_url.rstrip("/")

    if full_url in malware_urls:
        return {"status": "unsafe", "message": "Malware detected on this URL."}
    
    return {"status": "safe", "message": "URL is clean."}