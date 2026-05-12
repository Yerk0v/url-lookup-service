from fastapi import FastAPI, Path, HTTPException
import logging 
import time 
import json 
import os 
import sys
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv

load_dotenv()

def setup_metrics(app: FastAPI) -> None:
    enable_metrics = os.getenv("ENABLE_METRICS", "false").lower() == "true"

    if not enable_metrics:
        logging.info("Prometheus metrics disabled")
        return

    try:
        Instrumentator(
            excluded_handlers=[
                "/metrics",
                "/docs",
                "/openapi.json",
            ],
            should_group_status_codes=False,
        ).instrument(app).expose(app)

        logging.info("Prometheus metrics enabled")

    except Exception as e:
        logging.error(f"Error enabling Prometheus metrics: {e}")

log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(level=getattr(logging, log_level), format='%(asctime)s %(levelname)s %(name)s %(message)s')

app = FastAPI()

setup_metrics(app)

startup_time = time.time()

file_path = os.getenv("FILE_PATH", "data/urls.json")

@app.get("/health")
def health_check():
    return {"status": "Healthy"}

@app.get("/ready")
def readiness_check():
    checks = {
        "database_conn": True,
        "cache_conn": True,
    }

    if not all(checks.values()):
        raise HTTPException(status_code=503, detail="Service unavailable")
    
    return {
        "status": "Ready",
        "uptime_seconds": round(time.time() - startup_time, 2)
    }

try:
    with open(file_path, "r") as file:
        data = json.load(file)
    logging.info(f"{file_path} loaded successfully!")

except FileNotFoundError:
    logging.error(f"{file_path} doesn't exist")
    sys.exit(-1)

except json.JSONDecodeError as e:
    logging.error(f"Invalid JSON in {file_path}: {e}")
    sys.exit(-1)

except Exception as e:
    logging.error(f"Unexpected error: {e}")
    sys.exit(-1)

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
        