# URL LookUp Service

A small application who listens to GET requests and returns wether the URL passed is safe or not.

## API Usage

### Request
The service listens for `GET` requests in the following format:
`GET /urlinfo/1/{hostname_and_port}/{original_path_and_query_string}`

**Example:**
`GET http://localhost:8000/urlinfo/1/google.com/search`

### Responses
**Safe URL:**
```json
{
    "status": "safe",
    "message": "URL is clean."
}
```

**UnSafe URL:**
```json
{
    "status": "unsafe",
    "message": "Malware detected on this URL."
}
```

## Running the application

You can run this application locally using Python or via Docker.

### Option 1: using Docker

1. Ensure docker & docker compose are installed.

2. Run the following command:

```bash
docker compose up -d
```

3. The service will be available at http://localhost:8000

### Option 2: Local Python environment

1. Create and activate the virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
2. Install dependencies:
```bash
pip install -r requirements.txt
```  
3. Start the web server:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```  

## Quick curl tests

```bash
curl -s http://localhost:8000/urlinfo/1/www.example.site.cl/
curl -s http://localhost:8000/urlinfo/1/www.example.site.2.cl/badpath
curl -s http://localhost:8000/urlinfo/1/www.example.site.3.com/
curl -s http://localhost:8000/urlinfo/1/www.google.com/search
```
## Running tests

To run the automated test suite, ensure your dependencies are installed and run:

```bash
pytest
```  

**Note**: Make sure you use the same environment to run the app locally to run tests.

