# Personal Drive API - Postman Collection

This folder contains a complete Postman collection for testing the Personal Drive API endpoints.

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

- **appwriteEndpoint**: Your Appwrite endpoint (default: `https://sgp.cloud.appwrite.io/v1`)
- **projectId**: Your Appwrite project ID (default: `694f94f00016c4a31254`)
- **userId**: Your test user ID (default: `6950c2440001ee20a565`)
- **mimeType**: MIME type for test file (default: `text/plain`)

**Note:** `fileId`, `presignedUploadUrl`, and `presignedDownloadUrl` are automatically set by the collection tests.

### 3. Prepare Test File

For the "Upload File to S3" request:
1. Create a test file (e.g., `test.txt`)
2. In Postman, open the "2. Upload File to S3" request
3. Change body type to **binary**
4. Click **Select File** and choose your test file

## Collection Structure

The collection contains 6 requests in the correct execution order:

### 1. Presign Upload
- **Purpose**: Get presigned URL for uploading a file
- **Method**: POST
- **Body**: File metadata (name, size, mimeType)
- **Response**: Returns `fileId` and `presignedUploadUrl`
- **Auto-saves**: `fileId` and `presignedUploadUrl` to collection variables

### 2. Upload File to S3
- **Purpose**: Upload file to S3 using presigned URL
- **Method**: PUT
- **Body**: Binary file (select file in Postman)
- **URL**: Uses `presignedUploadUrl` from step 1
- **Note**: Change body type to **binary** and select your test file

### 3. Index File
- **Purpose**: Index uploaded file for semantic search
- **Method**: POST
- **Body**: `fileId` (automatically uses saved variable)
- **Response**: Confirms file is indexed

### 4. Search Files
- **Purpose**: Search for files using semantic search
- **Method**: POST
- **Body**: Search query and result limit
- **Response**: Array of matching files

### 5. Presign Download
- **Purpose**: Get presigned URL for downloading a file
- **Method**: POST
- **Body**: `fileId` (automatically uses saved variable)
- **Response**: Returns `presignedDownloadUrl`
- **Auto-saves**: `presignedDownloadUrl` to collection variables

### 6. Download File from S3
- **Purpose**: Download file from S3 using presigned URL
- **Method**: GET
- **URL**: Uses `presignedDownloadUrl` from step 5
- **Response**: File content

## Running the Collection

### Option 1: Run Individual Requests
1. Execute requests in order (1 → 6)
2. Variables are automatically saved between requests
3. Check test results in the **Test Results** tab

### Option 2: Run Collection Runner
1. Click on collection name → **Run**
2. Select all requests
3. Click **Run Personal Drive API**
4. View results summary

## Test Assertions

Each request includes automated tests that verify:
- ✅ HTTP status codes
- ✅ Response structure
- ✅ Required fields
- ✅ Success indicators

## Troubleshooting

### "fileId is not set" error
- Make sure you run requests in order
- Check that "1. Presign Upload" completed successfully
- Verify the test saved `fileId` to collection variables

### Upload fails
- Ensure body type is set to **binary** (not raw)
- Verify the presigned URL hasn't expired (15 minutes)
- Check file size doesn't exceed limits

### Search returns no results
- Wait a few seconds after indexing (step 3)
- Verify the file was indexed successfully
- Try a different search query

### Download URL expired
- Presigned URLs expire after 1 hour
- Re-run "5. Presign Download" to get a new URL

## Variables Reference

### Collection Variables (Auto-set)
- `fileId` - Set by "1. Presign Upload"
- `presignedUploadUrl` - Set by "1. Presign Upload"
- `presignedDownloadUrl` - Set by "5. Presign Download"

### Environment Variables (Manual)
- `appwriteEndpoint` - Appwrite API endpoint
- `projectId` - Appwrite project ID
- `userId` - Test user ID
- `mimeType` - MIME type for test file

## Example Workflow

1. **Import** collection and environment
2. **Configure** environment variables (projectId, userId, etc.)
3. **Run** "1. Presign Upload" → Get fileId and upload URL
4. **Configure** "2. Upload File to S3" → Set body to binary, select file
5. **Run** "2. Upload File to S3" → File uploaded to S3
6. **Run** "3. Index File" → File indexed for search
7. **Wait** 5-10 seconds for indexing to complete
8. **Run** "4. Search Files" → Search for indexed file
9. **Run** "5. Presign Download" → Get download URL
10. **Run** "6. Download File from S3" → Verify file download

## Notes

- All requests require `X-Appwrite-Project` header
- User authentication via `x-appwrite-user-id` header
- Presigned URLs expire (upload: 15 min, download: 1 hour)
- File indexing may take a few seconds to complete
- Collection variables persist across requests in the same session

## Related Documentation

- See `backend/appwrite/functions/TESTING.md` for detailed API documentation
- See `test-personal-drive.ps1` for PowerShell test script reference

