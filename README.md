# URL LookUp Service

This small application listens to GET requests and returns wether the URL passed is safe or not.

Example:

### Request
```bash
 GET /urlinfo/1/{hostname_and_port}/{original_path_and_query_string}
```

### Response
```json
{
    "status", "success",
    "data" : "URL is safe!" 
}
```

---

## Setup

...

