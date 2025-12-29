# Testing Guide for Python Service (Unified Backend)

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

3. Set up environment variables (create `.env` file):
```env
API_KEY=your-service-api-key
APPWRITE_ENDPOINT=https://sgp.cloud.appwrite.io/v1
APPWRITE_PROJECT_ID=your-project-id
APPWRITE_API_KEY=your-appwrite-api-key
APPWRITE_DATABASE_ID=your-database-id
APPWRITE_TABLE_ID=your-table-id
S3_ENDPOINT=your-s3-endpoint
S3_ACCESS_KEY_ID=your-access-key
S3_SECRET_ACCESS_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket-name
```

## API Key Authentication

The Python service endpoints are protected with API key authentication. The following endpoints require an API key:
- All `/api/v1/*` endpoints
- `GET /stats` - Get service statistics

The `/health` and `/` endpoints are public and do not require authentication.

For user-specific operations, you also need to include the `X-User-Id` header (simulating Flutter client behavior after Appwrite authentication).

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

Include the API key in the `X-API-Key` header, and for user operations, include `X-User-Id`:

```bash
# User operation example
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{"name": "test.pdf", "size": 1024, "mimeType": "application/pdf"}'

# System operation example (no user ID needed)
curl -X GET http://localhost:8000/stats \
  -H "X-API-Key: your-api-key-here"
```

For the test script, set the environment variable before running:
```bash
export API_KEY="your-api-key-here"
export TEST_USER_ID="test-user-id"  # For testing user operations
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
- File upload presign
- File upload complete
- File listing
- File retrieval
- File update
- File deletion
- Download URL generation
- Semantic search
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

#### Upload Presign
```bash
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{
    "name": "test.pdf",
    "size": 1024,
    "mimeType": "application/pdf"
  }'
```

#### Complete Upload (after uploading to S3)
```bash
curl -X POST http://localhost:8000/api/v1/upload/complete \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{"fileId": "file-id-from-presign"}'
```

#### Search Documents
```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{"query": "Python programming", "k": 5}'
```

#### List Files
```bash
curl -X GET "http://localhost:8000/api/v1/files?limit=10&offset=0" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id"
```

### 4. Using Python Requests

```python
import os
import requests

BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY") or os.getenv("SEMANTIC_SERVICE_API_KEY")
USER_ID = os.getenv("TEST_USER_ID", "test-user-id")

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY,
    "X-User-Id": USER_ID
}

# Get presigned upload URL
response = requests.post(
    f"{BASE_URL}/api/v1/upload/presign",
    json={
        "name": "test.pdf",
        "size": 1024,
        "mimeType": "application/pdf"
    },
    headers=headers
)
print(response.json())
file_id = response.json()["fileId"]

# Complete upload (after uploading to S3)
response = requests.post(
    f"{BASE_URL}/api/v1/upload/complete",
    json={"fileId": file_id},
    headers=headers
)
print(response.json())

# Search
response = requests.post(
    f"{BASE_URL}/api/v1/search",
    json={"query": "test document", "k": 5},
    headers=headers
)
print(response.json())

# List files
response = requests.get(
    f"{BASE_URL}/api/v1/files",
    headers=headers,
    params={"limit": 10, "offset": 0}
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
   curl http://localhost:8000/stats \
     -H "X-API-Key: your-api-key-here"
   ```

2. **Upload and index files**
   ```bash
   # Step 1: Get presigned URL
   curl -X POST http://localhost:8000/api/v1/upload/presign \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -H "X-User-Id: test-user-id" \
     -d '{"name": "doc1.pdf", "size": 1024, "mimeType": "application/pdf"}'
   
   # Step 2: Upload file to S3 using presigned URL (from step 1)
   # (Use the URL from the response)
   
   # Step 3: Complete upload and index
   curl -X POST http://localhost:8000/api/v1/upload/complete \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -H "X-User-Id: test-user-id" \
     -d '{"fileId": "file-id-from-step-1"}'
   ```

3. **Search for similar content**
   ```bash
   curl -X POST http://localhost:8000/api/v1/search \
     -H "Content-Type: application/json" \
     -H "X-API-Key: your-api-key-here" \
     -H "X-User-Id: test-user-id" \
     -d '{"query": "data analysis", "k": 5}'
   ```

4. **List files**
   ```bash
   curl -X GET "http://localhost:8000/api/v1/files?limit=10" \
     -H "X-API-Key: your-api-key-here" \
     -H "X-User-Id: test-user-id"
   ```

5. **Check stats**
   ```bash
   curl http://localhost:8000/stats \
     -H "X-API-Key: your-api-key-here"
   ```

### Error Testing

Test validation errors:
```bash
# Empty query
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{"query": "", "k": 5}'

# Invalid k
curl -X POST http://localhost:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{"query": "test", "k": -1}'

# Missing required fields
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -H "X-User-Id: test-user-id" \
  -d '{"name": "test.pdf"}'

# Missing API key (should return 401)
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -H "X-User-Id: test-user-id" \
  -d '{"name": "test.pdf", "size": 1024, "mimeType": "application/pdf"}'

# Invalid API key (should return 401)
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key" \
  -H "X-User-Id: test-user-id" \
  -d '{"name": "test.pdf", "size": 1024, "mimeType": "application/pdf"}'

# Missing user ID (should return 400 or 401)
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your-api-key-here" \
  -d '{"name": "test.pdf", "size": 1024, "mimeType": "application/pdf"}'
```

## Expected Responses

### Successful Presign
```json
{
  "fileId": "unique_file_id",
  "upload": {
    "mode": "single",
    "url": "https://s3-endpoint.com/presigned-url",
    "expiresIn": 900
  }
}
```

### Successful Upload Complete
```json
{
  "status": "indexed",
  "fileId": "unique_file_id",
  "hash": "sha256-hash",
  "textExtracted": true,
  "indexed": true
}
```

### Search Results
```json
{
  "results": [
    {
      "fileId": "file_id_1",
      "name": "document.pdf",
      "score": 0.95,
      "size": 1024000,
      "mimeType": "application/pdf",
      "createdAt": "2024-01-01T00:00:00Z"
    }
  ],
  "query": "Python programming",
  "total": 1
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
4. **Empty search results**: Make sure you've uploaded and indexed some files first
5. **401 Unauthorized**: Make sure you're including the `X-API-Key` header with a valid API key
   - Check server logs for the generated API key if running in development mode
   - Set `API_KEY` environment variable for production
6. **400 Bad Request**: Check that you're including the `X-User-Id` header for user operations
7. **Appwrite connection errors**: Verify your Appwrite environment variables are set correctly
8. **S3 connection errors**: Verify your S3 credentials and endpoint are correct
9. **File not found errors**: Make sure files are uploaded to S3 before calling `/upload/complete`
10. **Text extraction failures**: Check that the file format is supported (PDF, DOCX, etc.)

