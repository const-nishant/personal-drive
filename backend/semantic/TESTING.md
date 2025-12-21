# Testing Guide for Semantic Search Service

## Prerequisites

1. Install dependencies:
```bash
cd backend/semantic
pip install -r requirements.txt
```

2. Install requests for testing (if not already installed):
```bash
pip install requests
```

## API Key Authentication

The semantic service endpoints are protected with API key authentication. The following endpoints require an API key:
- `POST /index` - Index documents
- `POST /search` - Search documents
- `GET /stats` - Get service statistics

The `/health` endpoint is public and does not require authentication.

### Setting Up API Key

**Option 1: Set Environment Variable (Recommended for Production)**
```bash
# Windows PowerShell
$env:API_KEY="your-secret-api-key-here"

# Windows CMD
set API_KEY=your-secret-api-key-here

# Linux/Mac
export API_KEY="your-secret-api-key-here"
```

**Option 2: Use SEMANTIC_SERVICE_API_KEY**
```bash
export SEMANTIC_SERVICE_API_KEY="your-secret-api-key-here"
```

**Option 3: Development Mode (Auto-generated)**
If no API key is set, the server will generate a random API key and log it to the console. Check the server logs for the generated key.

### Using API Key in Requests

Include the API key in the `X-API-Key` header:

```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"file_id": "test123", "text": "Sample text"}'
```

For the test script, set the environment variable before running:
```bash
export API_KEY="your-api-key-here"
python test_service.py
```

## Starting the Server

Start the FastAPI server:

**PowerShell (Windows):**
```powershell
cd backend\semantic
python -m uvicorn app:app --reload
```

**Bash/Linux/Mac:**
```bash
cd backend/semantic
uvicorn app:app --reload
```

**Alternative (if uvicorn is in PATH):**
```bash
cd backend/semantic
uvicorn app:app --reload
```

The server will start at `http://localhost:8000`

## Testing Methods

### 1. Using the Test Script (Recommended)

Run the automated test script:
```bash
cd backend/semantic
python test_service.py
```

This will test all endpoints including:
- Health check
- Stats endpoint
- Document indexing
- Search functionality
- Error handling

### 2. Using FastAPI Interactive Docs

FastAPI provides automatic interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

You can test all endpoints directly from your browser!

### 3. Using cURL

#### Health Check
```bash
curl http://localhost:8000/health
```

#### Get Stats
```bash
curl http://localhost:8000/stats \
  -H "X-API-Key: your-api-key-here"
```

#### Index a Document
```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"file_id": "test123", "text": "This is a test document about Python programming."}'
```

#### Search Documents
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"query": "Python programming", "k": 5}'
```

### 4. Using Python Requests

```python
import os
import requests

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY") or os.getenv("SEMANTIC_SERVICE_API_KEY")

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

# Index a document
response = requests.post(
    f"{BASE_URL}/index",
    json={"file_id": "doc1", "text": "FastAPI is a web framework"},
    headers=headers
)
print(response.json())

# Search
response = requests.post(
    f"{BASE_URL}/search",
    json={"query": "web framework", "k": 3},
    headers=headers
)
print(response.json())
```

### 5. Using HTTPie (if installed)

```bash
# Index
http POST localhost:8000/index \
  X-API-Key:your-api-key-here \
  file_id=doc1 text="Sample text"

# Search
http POST localhost:8000/search \
  X-API-Key:your-api-key-here \
  query="sample" k:=3

# Stats
http GET localhost:8000/stats X-API-Key:your-api-key-here

# Health (no API key required)
http GET localhost:8000/health
```

## Test Scenarios

### Basic Flow

1. **Start with empty index**
   ```bash
   curl http://localhost:8000/stats
   ```

2. **Index multiple documents**
   ```bash
   curl -X POST http://localhost:8000/index \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"file_id": "doc1", "text": "Python is great for data science"}'
   
   curl -X POST http://localhost:8000/index \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"file_id": "doc2", "text": "FastAPI makes API development easy"}'
   ```

3. **Search for similar content**
   ```bash
   curl -X POST http://localhost:8000/search \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -d '{"query": "data analysis", "k": 2}'
   ```

4. **Check stats**
   ```bash
   curl http://localhost:8000/stats \
     -H "X-API-Key: your-api-key-here"
   ```

### Error Testing

Test validation errors:
```bash
# Empty query
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"query": "", "k": 5}'

# Invalid k
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"query": "test", "k": -1}'

# Missing file_id
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"file_id": "", "text": "test"}'

# Missing API key (should return 401)
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test123", "text": "test"}'

# Invalid API key (should return 401)
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key" \
  -d '{"file_id": "test123", "text": "test"}'
```

## Expected Responses

### Successful Index
```json
{
  "status": "indexed"
}
```

### Already Indexed
```json
{
  "status": "already_indexed"
}
```

### Search Results
```json
{
  "file_ids": ["doc1", "doc2", "doc3"]
}
```

### Health Check
```json
{
  "status": "ok",
  "model_loaded": true,
  "index_initialized": true,
  "index_size": 5,
  "documents_indexed": 5
}
```

## Troubleshooting

1. **Connection refused**: Make sure the server is running on port 8000
2. **Model download slow**: First run will download the sentence transformer model (~80MB)
3. **Index not persisting**: Check that the `index/` directory is writable
4. **Empty search results**: Make sure you've indexed some documents first
5. **401 Unauthorized**: Make sure you're including the `X-API-Key` header with a valid API key
   - Check server logs for the generated API key if running in development mode
   - Set `API_KEY` or `SEMANTIC_SERVICE_API_KEY` environment variable for production

