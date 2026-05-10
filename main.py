from fastapi import FastAPI, Path, HTTPException
import logging 
import time 
import json 
import os 

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s %(levelname)s %(name)s %(message)s')

app = FastAPI()

with open("data/urls.json", "r") as file:
    data = json.load(file)

@app.get("/urlinfo/1/{hostname_and_port}/{original_path_and_query_string:path}")
def get_url_info(
    hostname_and_port: str = Path(..., 
    min_length=3, max_length=255, 
    pattern=r"^[a-zA-Z0-9.-]+(:\d+)?$"),
    original_path_and_query_string: str = Path(...,
    min_length=3,
    max_length=128,
    pattern=r"^[a-zA-Z0-9.-]+(:\d+)?$",
    )
):
    try: 
        domain_part = hostname_and_port.lower()
        full_url = f"{domain_part}/{original_path_and_query_string}".rstrip("/")
        
        logging.info(f"Checking URL: {full_url}...")

        if full_url in data['MALWARE_URLS']: 
            return {
            "status": "unsafe", 
            "message": "Malware detected on this URL."
            }
        
        return {
            "status": "safe",
            "message": "The URL is clean!"
        }
    
    except Exception as e:
        logging.error(f"Unhandled error checking URL {full_url}: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
        