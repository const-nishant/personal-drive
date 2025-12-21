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
curl http://localhost:8000/stats
```

#### Index a Document
```bash
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test123", "text": "This is a test document about Python programming."}'
```

#### Search Documents
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Python programming", "k": 5}'
```

### 4. Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Index a document
response = requests.post(
    f"{BASE_URL}/index",
    json={"file_id": "doc1", "text": "FastAPI is a web framework"}
)
print(response.json())

# Search
response = requests.post(
    f"{BASE_URL}/search",
    json={"query": "web framework", "k": 3}
)
print(response.json())
```

### 5. Using HTTPie (if installed)

```bash
# Index
http POST localhost:8000/index file_id=doc1 text="Sample text"

# Search
http POST localhost:8000/search query="sample" k:=3

# Health
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
     -d '{"file_id": "doc1", "text": "Python is great for data science"}'
   
   curl -X POST http://localhost:8000/index \
     -H "Content-Type: application/json" \
     -d '{"file_id": "doc2", "text": "FastAPI makes API development easy"}'
   ```

3. **Search for similar content**
   ```bash
   curl -X POST http://localhost:8000/search \
     -H "Content-Type: application/json" \
     -d '{"query": "data analysis", "k": 2}'
   ```

4. **Check stats**
   ```bash
   curl http://localhost:8000/stats
   ```

### Error Testing

Test validation errors:
```bash
# Empty query
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "", "k": 5}'

# Invalid k
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": -1}'

# Missing file_id
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"file_id": "", "text": "test"}'
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

