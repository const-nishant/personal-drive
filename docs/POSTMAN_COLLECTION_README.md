# Personal Drive Python Service - Postman Collection

This folder contains a complete Postman collection for testing the Personal Drive Python Service (FastAPI) endpoints directly.

## Files

- **Personal-Drive-API.postman_collection.json** - Main Postman collection with all API requests
- **Personal-Drive-Environment.postman_environment.json** - Environment variables for easy configuration

## Setup Instructions

### 1. Import Collection and Environment

1. Open Postman
2. Click **Import** button (top left)
3. Import both files:
   - `Personal-Drive-API.postman_collection.json`
   - `Personal-Drive-Environment.postman_environment.json`
4. Select the environment: **Personal Drive - Test Environment** (top right dropdown)

### 2. Configure Environment Variables

Update the following variables in the environment:

- **pythonServiceUrl**: Your Python service URL (default: `http://localhost:8000`)
- **apiKey**: Your Python service API key (set from `API_KEY` or `SEMANTIC_SERVICE_API_KEY` environment variable)
- **userId**: Your test user ID (default: `6950c2440001ee20a565`)
- **mimeType**: MIME type for test file (default: `text/plain`)

**Note:** `fileId`, `presignedUploadUrl`, and `presignedDownloadUrl` are automatically set by the collection tests.

### 3. Get Your API Key

The API key is set in the Python service configuration. You can find it by:

1. Checking your `.env` file in `backend/semantic/` for `API_KEY` or `SEMANTIC_SERVICE_API_KEY`
2. Or checking the service logs when it starts (it will show a warning with the generated key if not set)
3. Set this value in the Postman environment variable `apiKey`

### 4. Prepare Test File

For the "Upload File to S3" request:
1. Create a test file (e.g., `test.txt`)
2. In Postman, open the "2. Upload File to S3" request
3. Change body type to **binary**
4. Click **Select File** and choose your test file

## Collection Structure

The collection is organized into folders:

### System Endpoints
- **1. Get API Info** - Get API information and available endpoints (no auth)
- **2. Health Check** - Health check endpoint (no auth)
- **3. Get Stats** - Get service statistics (requires API key)

### File Upload Flow
- **1. Presign Upload** - Get presigned URL for uploading a file
- **2. Upload File to S3** - Upload file to S3 using presigned URL
- **3. Complete Upload** - Complete upload, extract text, and index

### File Management
- **1. List Files** - List user's files with pagination
- **2. Get File Metadata** - Get file metadata by ID
- **3. Update File Metadata** - Update file metadata (name, description, tags)
- **4. Get Download URL** - Get presigned download URL
- **5. Download File from S3** - Download file using presigned URL
- **6. Delete File** - Delete file and metadata

### Search
- **Semantic Search** - Perform semantic search across user's files

## Authentication

The Python service uses two headers for authentication:

- **X-API-Key**: Service API key (required for all endpoints except `/`, `/health`)
- **X-User-Id**: User ID from Appwrite authentication (required for user-specific operations)

## Running the Collection

### Option 1: Run Individual Requests

1. Start with **System Endpoints** to verify service is running
2. Execute **File Upload Flow** requests in order (1 → 3)
3. Use **File Management** to manage files
4. Test **Search** functionality
5. Variables are automatically saved between requests
6. Check test results in the **Test Results** tab

### Option 2: Run Collection Runner

1. Click on collection name → **Run**
2. Select all requests or specific folders
3. Click **Run Personal Drive Python Service API**
4. View results summary

## Test Assertions

Each request includes automated tests that verify:
- ✅ HTTP status codes
- ✅ Response structure
- ✅ Required fields
- ✅ Success indicators
- ✅ Data types and formats

## Complete Workflow Example

### 1. System Check
```
1. Get API Info → Verify service is running
2. Health Check → Check service health
3. Get Stats → Verify API key works
```

### 2. Upload and Index File
```
1. Presign Upload → Get fileId and upload URL
2. Upload File to S3 → Upload file (set body to binary, select file)
3. Complete Upload → Extract text and index file
```

### 3. Search and Manage
```
1. List Files → See all your files
2. Get File Metadata → Get details of uploaded file
3. Semantic Search → Search for files
4. Update File Metadata → Update file info
5. Get Download URL → Get download link
6. Download File from S3 → Download file
7. Delete File → Remove file
```

## Troubleshooting

### "Invalid or missing API key" error
- Verify `apiKey` is set in environment variables
- Check that the API key matches the service configuration
- Ensure `X-API-Key` header is included in the request

### "User ID is required" error
- Verify `userId` is set in environment variables
- Ensure `X-User-Id` header is included in the request

### "fileId is not set" error
- Make sure you run requests in order
- Check that "1. Presign Upload" completed successfully
- Verify the test saved `fileId` to collection variables

### Upload fails
- Ensure body type is set to **binary** (not raw)
- Verify the presigned URL hasn't expired (15 minutes)
- Check file size doesn't exceed limits (100MB default)
- Verify MIME type is allowed

### Search returns no results
- Wait a few seconds after completing upload (step 3)
- Verify the file was indexed successfully (check `indexed: true` in response)
- Try a different search query
- Check that files exist for the user

### Download URL expired
- Presigned URLs expire after 1 hour (default)
- Re-run "4. Get Download URL" to get a new URL
- You can specify `expiresIn` query parameter (max 86400 seconds)

### Service not responding
- Verify Python service is running on `pythonServiceUrl`
- Check service logs for errors
- Ensure all required environment variables are set
- Verify service can connect to Appwrite and S3

## Variables Reference

### Collection Variables (Auto-set)
- `fileId` - Set by "1. Presign Upload"
- `presignedUploadUrl` - Set by "1. Presign Upload"
- `presignedDownloadUrl` - Set by "4. Get Download URL"
- `uploadId` - Set by "1. Presign Upload" (for multipart uploads)

### Environment Variables (Manual)
- `pythonServiceUrl` - Python service base URL (default: `http://localhost:8000`)
- `apiKey` - Service API key (from environment variable)
- `userId` - Test user ID
- `mimeType` - MIME type for test file (default: `text/plain`)

## API Endpoints Reference

### System
- `GET /` - API information
- `GET /health` - Health check
- `GET /stats` - Service statistics

### Upload
- `POST /api/v1/upload/presign` - Get presigned upload URL
- `POST /api/v1/upload/complete` - Complete upload and index

### Files
- `GET /api/v1/files` - List files (with pagination and filters)
- `GET /api/v1/files/{file_id}` - Get file metadata
- `PUT /api/v1/files/{file_id}` - Update file metadata
- `DELETE /api/v1/files/{file_id}` - Delete file
- `GET /api/v1/files/{file_id}/download` - Get download URL

### Search
- `POST /api/v1/search` - Semantic search

## Request Examples

### Presign Upload (Single)
```json
{
  "name": "document.pdf",
  "size": 1024000,
  "mimeType": "application/pdf"
}
```

### Presign Upload (Multipart)
```json
{
  "name": "large-file.pdf",
  "size": 104857600,
  "mimeType": "application/pdf",
  "uploadMode": "multipart",
  "parts": 5
}
```

### Complete Upload
```json
{
  "fileId": "unique_file_id"
}
```

### Update File
```json
{
  "name": "new-name.pdf",
  "description": "Updated description",
  "tags": ["tag1", "tag2"],
  "folderId": "folder_id"
}
```

### Search
```json
{
  "query": "Python programming tutorial",
  "k": 5,
  "folderId": "optional_folder_id"
}
```

## Notes

- All endpoints (except `/` and `/health`) require `X-API-Key` header
- User-specific operations require `X-User-Id` header
- Presigned URLs expire (upload: 15 min, download: 1 hour default)
- File indexing happens automatically in "Complete Upload"
- Collection variables persist across requests in the same session
- Use query parameters for pagination and filtering in List Files

## Interactive Documentation

The Python service provides automatic interactive documentation:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

You can test all endpoints directly from your browser!

## Related Documentation

- See `backend/semantic/API.md` for detailed API documentation
- See `backend/semantic/app.py` for endpoint implementations
- See `backend/semantic/TESTING.md` for testing patterns
