# Python Service API Documentation

## Overview

The Python Service is a unified FastAPI backend that handles all operations for Personal Drive:
- File upload/download (presigned URLs)
- File metadata management (Appwrite Tables)
- Text extraction from files
- Semantic indexing (FAISS)
- Semantic search

## Base URL

```
http://localhost:8000  # Development
https://your-domain.com  # Production
```

## Authentication

### API Key Authentication

All endpoints (except `/health` and `/`) require an API key in the `X-API-Key` header.

```http
X-API-Key: your-service-api-key
```

### User Context

For user-specific operations, include the `X-User-Id` header (set by Flutter after Appwrite authentication):

```http
X-User-Id: user-id-from-appwrite
```

## Endpoints

### System Endpoints

#### GET /

Get API information and available endpoints.

**Authentication:** None required

**Response:**
```json
{
  "service": "Personal Drive Python Service",
  "status": "running",
  "endpoints": {
    "health": "/health",
    "stats": "/stats",
    "upload": {
      "presign": "/api/v1/upload/presign",
      "complete": "/api/v1/upload/complete"
    },
    "files": {
      "list": "/api/v1/files",
      "get": "/api/v1/files/{file_id}",
      "update": "/api/v1/files/{file_id}",
      "delete": "/api/v1/files/{file_id}",
      "download": "/api/v1/files/{file_id}/download"
    },
    "search": "/api/v1/search"
  },
  "docs": "/docs"
}
```

#### GET /health

Health check endpoint.

**Authentication:** None required

**Response:**
```json
{
  "status": "ok",
  "model_loaded": true,
  "index_initialized": true,
  "index_size": 100,
  "documents_indexed": 100
}
```

#### GET /stats

Get service statistics.

**Authentication:** API key required

**Headers:**
- `X-API-Key`: Your service API key

**Response:**
```json
{
  "model": "all-MiniLM-L6-v2",
  "embedding_dimension": 384,
  "index_size": 100,
  "documents_indexed": 100,
  "index_path": "./index/faiss.index",
  "meta_path": "./index/meta.pkl"
}
```

### File Upload Endpoints

#### POST /api/v1/upload/presign

Generate a presigned URL for file upload.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Request Body:**
```json
{
  "name": "document.pdf",
  "size": 1024000,
  "mimeType": "application/pdf",
  "folderId": "optional_folder_id",
  "description": "Optional description",
  "tags": ["tag1", "tag2"],
  "uploadMode": "single"
}
```

**Response:**
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

**Multipart Upload:**
```json
{
  "name": "large-file.pdf",
  "size": 104857600,
  "mimeType": "application/pdf",
  "uploadMode": "multipart",
  "parts": 5
}
```

**Response:**
```json
{
  "fileId": "unique_file_id",
  "upload": {
    "mode": "multipart",
    "uploadId": "multipart-upload-id",
    "parts": [
      {
        "partNumber": 1,
        "url": "https://s3-endpoint.com/presigned-url-1"
      },
      {
        "partNumber": 2,
        "url": "https://s3-endpoint.com/presigned-url-2"
      }
    ]
  }
}
```

**Error Responses:**
- `400`: Invalid request (missing fields, file too large, invalid MIME type)
- `401`: Invalid or missing API key
- `500`: Internal server error

#### POST /api/v1/upload/complete

Complete file upload, extract text, compute hash, and index semantically.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Request Body:**
```json
{
  "fileId": "unique_file_id"
}
```

**Response:**
```json
{
  "status": "indexed",
  "fileId": "unique_file_id",
  "hash": "sha256-hash-of-file",
  "textExtracted": true,
  "indexed": true
}
```

**Error Responses:**
- `400`: Invalid fileId or file not found
- `401`: Invalid or missing API key
- `404`: File not found in S3
- `500`: Text extraction or indexing failed

### File Management Endpoints

#### GET /api/v1/files

List user's files with pagination.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Query Parameters:**
- `limit` (optional, default: 50): Number of files to return
- `offset` (optional, default: 0): Pagination offset
- `folderId` (optional): Filter by folder ID
- `mimeType` (optional): Filter by MIME type

**Response:**
```json
{
  "files": [
    {
      "fileId": "file_id_1",
      "name": "document.pdf",
      "size": 1024000,
      "mimeType": "application/pdf",
      "hash": "sha256-hash",
      "storagePath": "documents/user_id/file_id_document.pdf",
      "createdAt": "2024-01-01T00:00:00Z",
      "userId": "user_id",
      "folderId": null,
      "description": null,
      "tags": [],
      "indexed": true,
      "status": "completed"
    }
  ],
  "total": 100,
  "limit": 50,
  "offset": 0
}
```

#### GET /api/v1/files/{file_id}

Get file metadata by ID.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Response:**
```json
{
  "fileId": "file_id",
  "name": "document.pdf",
  "size": 1024000,
  "mimeType": "application/pdf",
  "hash": "sha256-hash",
  "storagePath": "documents/user_id/file_id_document.pdf",
  "createdAt": "2024-01-01T00:00:00Z",
  "userId": "user_id",
  "folderId": null,
  "description": null,
  "tags": [],
  "indexed": true,
  "status": "completed"
}
```

**Error Responses:**
- `401`: Invalid or missing API key
- `403`: File belongs to different user
- `404`: File not found

#### PUT /api/v1/files/{file_id}

Update file metadata.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Request Body:**
```json
{
  "name": "new-name.pdf",
  "description": "Updated description",
  "tags": ["tag1", "tag2"],
  "folderId": "new_folder_id"
}
```

**Response:**
```json
{
  "status": "updated",
  "file": {
    "fileId": "file_id",
    "name": "new-name.pdf",
    "description": "Updated description",
    "tags": ["tag1", "tag2"],
    "folderId": "new_folder_id"
  }
}
```

**Error Responses:**
- `400`: Invalid request body
- `401`: Invalid or missing API key
- `403`: File belongs to different user
- `404`: File not found

#### DELETE /api/v1/files/{file_id}

Delete a file and its metadata.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Response:**
```json
{
  "status": "deleted",
  "fileId": "file_id"
}
```

**Error Responses:**
- `401`: Invalid or missing API key
- `403`: File belongs to different user
- `404`: File not found
- `500`: Failed to delete from S3 or remove from index

#### GET /api/v1/files/{file_id}/download

Get a presigned download URL for a file.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Query Parameters:**
- `expiresIn` (optional, default: 3600): URL expiration time in seconds (max: 86400)

**Response:**
```json
{
  "url": "https://s3-endpoint.com/presigned-download-url",
  "expiresIn": 3600,
  "fileId": "file_id"
}
```

**Error Responses:**
- `401`: Invalid or missing API key
- `403`: File belongs to different user
- `404`: File not found

### Search Endpoint

#### POST /api/v1/search

Perform semantic search across user's files.

**Authentication:** API key + User ID required

**Headers:**
- `X-API-Key`: Your service API key
- `X-User-Id`: User ID from Appwrite authentication

**Request Body:**
```json
{
  "query": "Python programming tutorial",
  "k": 5,
  "folderId": "optional_folder_id"
}
```

**Response:**
```json
{
  "results": [
    {
      "fileId": "file_id_1",
      "name": "python-tutorial.pdf",
      "score": 0.95,
      "size": 1024000,
      "mimeType": "application/pdf",
      "createdAt": "2024-01-01T00:00:00Z",
      "description": "Python programming guide"
    },
    {
      "fileId": "file_id_2",
      "name": "advanced-python.pdf",
      "score": 0.87,
      "size": 2048000,
      "mimeType": "application/pdf",
      "createdAt": "2024-01-02T00:00:00Z",
      "description": "Advanced Python concepts"
    }
  ],
  "query": "Python programming tutorial",
  "total": 2
}
```

**Error Responses:**
- `400`: Invalid query (empty or too long)
- `401`: Invalid or missing API key
- `500`: Search failed

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request (validation error)
- `401`: Unauthorized (invalid or missing API key)
- `403`: Forbidden (user doesn't own the resource)
- `404`: Not Found
- `500`: Internal Server Error

## Rate Limiting

Rate limiting may be implemented in production. Check response headers:
- `X-RateLimit-Limit`: Maximum requests per time window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when rate limit resets

## Examples

### Complete Upload Flow

```bash
# 1. Get presigned URL
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "X-API-Key: your-api-key" \
  -H "X-User-Id: user-id" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "document.pdf",
    "size": 1024000,
    "mimeType": "application/pdf"
  }'

# 2. Upload file to S3 using presigned URL
curl -X PUT "presigned-url-from-step-1" \
  -H "Content-Type: application/pdf" \
  --data-binary "@document.pdf"

# 3. Complete upload and index
curl -X POST http://localhost:8000/api/v1/upload/complete \
  -H "X-API-Key: your-api-key" \
  -H "X-User-Id: user-id" \
  -H "Content-Type: application/json" \
  -d '{"fileId": "file-id-from-step-1"}'
```

### Search Example

```bash
curl -X POST http://localhost:8000/api/v1/search \
  -H "X-API-Key: your-api-key" \
  -H "X-User-Id: user-id" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Python programming",
    "k": 10
  }'
```

### List Files Example

```bash
curl -X GET "http://localhost:8000/api/v1/files?limit=20&offset=0" \
  -H "X-API-Key: your-api-key" \
  -H "X-User-Id: user-id"
```

## Interactive Documentation

FastAPI provides automatic interactive documentation:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

You can test all endpoints directly from your browser!

