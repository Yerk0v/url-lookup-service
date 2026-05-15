from fastapi import FastAPI, HTTPException, Request
import logging
import time
import json
import os
import re
from prometheus_fastapi_instrumentator import Instrumentator
from dotenv import load_dotenv
import uuid

MAX_PATH_LENGTH = 2048
PATH_PATTERN = re.compile(r"^[A-Za-z0-9._~\-/%?&=:@!$'()*+,;]*$")

def validate_port(hostname_and_port: str) -> None:
    if ":" not in hostname_and_port:
        return
    _, port_str = hostname_and_port.rsplit(":", 1)
    if not port_str.isdigit() or not (1 <= int(port_str) <= 65535):
        raise HTTPException(status_code=400, detail="Invalid port (must be 1-65535)")

def validate_path(path: str) -> None:
    if len(path) > MAX_PATH_LENGTH:
        raise HTTPException(status_code=400, detail=f"Path too long (max {MAX_PATH_LENGTH})")
    if not PATH_PATTERN.match(path):
        raise HTTPException(status_code=400, detail="Path contains invalid characters")

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

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())[:8]
    start = time.time()

    response = await call_next(request)

    duration = round((time.time() - start) * 1000, 2)

    logging.info(
        f"rid={request_id} method={request.method} path={request.url.path} "
        f"status={response.status_code} duration_ms={duration}"
    )

    response.headers["X-Request-ID"] = request_id
    return response 

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
    logging.error(f"{file_path} not found")
    raise RuntimeError("File not found.")

except json.JSONDecodeError as e:
    logging.error(f"Invalid JSON in {file_path}: {e}")
    raise RuntimeError("Error decoding JSON File.")

except Exception as e:
    logging.error(f"Unexpected error: {e}")
    raise RuntimeError("Unknown error.")

@app.get("/urlinfo/1/{hostname_and_port}/{original_path_and_query_string:path}")
def get_url_info(
    hostname_and_port: str,
    original_path_and_query_string: str,
):
    validate_port(hostname_and_port)
    validate_path(original_path_and_query_string)

    try:
        domain = hostname_and_port.lower().strip()
        path = original_path_and_query_string.lower().strip()

        full_url = f"{domain}/{path}"

        logging.info(f"Checking URL: {full_url}...")

        malware_urls = set(data.get("MALWARE_URLS", []))
        safe_urls = set(data.get("SAFE_URLS", []))

        if full_url in malware_urls:
            return {
                "status": "unsafe",
                "message": "Malware detected in URLS"
            }

        if domain in safe_urls:
            return {
                "status": "safe",
                "message": "Trusted URL"
            }
        
        return {
            "status": "unknown",
            "message": "Unknown URL"
        }
    except Exception as e:
        logging.error(f"Unhandled error checking URL {full_url}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal Server Error"
        )
    