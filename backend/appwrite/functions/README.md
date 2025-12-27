# Appwrite Functions Implementation

## Overview

This directory contains all Appwrite Cloud Functions for the Personal Drive system. These functions handle file uploads, indexing, search, and download URL generation.

## Functions

### 1. presignUpload
**Purpose:** Generate presigned URLs for secure S3 uploads and create initial metadata records.

**Flow:**
1. Validates user authentication
2. Validates file name, size (max 100MB), and MIME type
3. Generates unique fileId
4. Creates storage path (`photos/YYYY/MM/` or `documents/user_id/`)
5. Generates S3 presigned URL (15 minutes expiration)
6. Creates initial metadata record with `status: 'pending'`
7. Returns presigned URL + fileId to client

**Request Body:**
```json
{
  "name": "document.pdf",
  "size": 1024000,
  "mimeType": "application/pdf",
  "folderId": "optional_folder_id",
  "description": "Optional description",
  "tags": ["tag1", "tag2"]
}
```

**Response:**
```json
{
  "success": true,
  "fileId": "unique_file_id",
  "presignedUrl": "https://s3...",
  "expiresIn": 900,
  "metadata": { ... }
}
```

**Environment Variables Required:**
- `S3_ENDPOINT`
- `S3_ACCESS_KEY_ID`
- `S3_SECRET_ACCESS_KEY`
- `S3_BUCKET_NAME`
- `S3_REGION` (optional)
- `FILES_COLLECTION_ID` (optional, defaults to 'files')
- `APPWRITE_DATABASE_ID` (optional, defaults to 'default')
- `MAX_FILE_SIZE` (optional, defaults to 1073741824 = 1GB)
- `ALLOWED_MIME_TYPES` (optional, has defaults)

---

### 2. indexFile
**Purpose:** Download file from S3, extract text, compute hash, index via semantic service, and update metadata.

**Flow:**
1. Validates user authentication and fileId
2. Fetches file metadata from database
3. Verifies user ownership
4. Downloads file from S3 using storagePath
5. Computes SHA-256 hash
6. Checks for deduplication (reuses existing file if hash matches)
7. Extracts text based on MIME type:
   - PDF: pdf-parse
   - DOCX: mammoth
   - TXT: direct read
   - Images: filename + description
8. Calls semantic service `/index` endpoint
9. Updates metadata with hash, indexed status, vectorId

**Request Body:**
```json
{
  "fileId": "file_id_from_presignUpload"
}
```

**Response:**
```json
{
  "success": true,
  "message": "File indexed successfully",
  "fileId": "file_id",
  "hash": "sha256_hash",
  "indexed": true,
  "textLength": 1234
}
```

**Environment Variables Required:**
- `S3_ENDPOINT` - S3-compatible storage endpoint
- `S3_ACCESS_KEY_ID` - S3 access key
- `S3_SECRET_ACCESS_KEY` - S3 secret key
- `S3_BUCKET_NAME` - S3 bucket name
- `S3_REGION` - S3 region (optional, defaults to us-east-1)
- `SEMANTIC_SERVICE_URL` - Base URL of semantic service
- `SEMANTIC_SERVICE_API_KEY` - API key for semantic service authentication
- `APPWRITE_DATABASE_ID` - Database ID (optional, defaults to 'default')
- `FILES_COLLECTION_ID` - Collection ID (optional, defaults to 'files')

**Dependencies:**
- `pdf-parse` for PDF text extraction
- `mammoth` for DOCX text extraction

---

### 3. search
**Purpose:** Handle search queries, coordinate with semantic service, and return complete results with metadata.

**Flow:**
1. Validates user authentication
2. Validates and sanitizes search query (max 500 chars)
3. Validates k parameter (1-100)
4. Calls semantic service `/search` endpoint
5. Receives file_ids array
6. Fetches file metadata from database for each fileId
7. Filters by user ownership and indexed status
8. Returns complete results with metadata

**Request Body:**
```json
{
  "query": "search query text",
  "k": 5
}
```

**Response:**
```json
{
  "success": true,
  "query": "search query text",
  "results": [
    {
      "fileId": "file_id",
      "name": "document.pdf",
      "mimeType": "application/pdf",
      "size": 1024000,
      "storagePath": "documents/user_id/file_id_document.pdf",
      "createdAt": "2024-01-01T00:00:00Z",
      "description": "...",
      "tags": ["tag1"],
      "folderId": null
    }
  ],
  "count": 1
}
```

**Environment Variables Required:**
- `SEMANTIC_SERVICE_URL` - Base URL of semantic service
- `SEMANTIC_SERVICE_API_KEY` - API key for semantic service authentication
- `APPWRITE_DATABASE_ID` - Database ID (optional, defaults to 'default')
- `FILES_COLLECTION_ID` - Collection ID (optional, defaults to 'files')

---

### 4. presignDownload
**Purpose:** Generate presigned URLs for secure S3 downloads on-demand.

**Flow:**
1. Validates user authentication
2. Validates fileId
3. Fetches file metadata from database
4. Verifies user ownership
5. Generates S3 presigned URL (1 hour expiration)
6. Returns presigned URL + metadata

**Request Body:**
```json
{
  "fileId": "file_id"
}
```

**Response:**
```json
{
  "success": true,
  "fileId": "file_id",
  "presignedUrl": "https://s3...",
  "expiresIn": 3600,
  "metadata": {
    "fileId": "file_id",
    "name": "document.pdf",
    "mimeType": "application/pdf",
    "size": 1024000
  }
}
```

**Environment Variables Required:**
- `S3_ENDPOINT` - S3-compatible storage endpoint
- `S3_ACCESS_KEY_ID` - S3 access key
- `S3_SECRET_ACCESS_KEY` - S3 secret key
- `S3_BUCKET_NAME` - S3 bucket name
- `S3_REGION` - S3 region (optional, defaults to us-east-1)
- `APPWRITE_DATABASE_ID` - Database ID (optional, defaults to 'default')
- `FILES_COLLECTION_ID` - Collection ID (optional, defaults to 'files')

---

## Database Schema

The functions expect the following fields in the `files` collection:

**Required Fields:**
- `fileId` (string) - Unique file identifier
- `name` (string) - Original filename
- `size` (integer) - File size in bytes
- `mimeType` (string) - MIME type
- `userId` (string) - Owner user ID
- `createdAt` (datetime) - Creation timestamp

**Optional Fields:**
- `folderId` (string) - Folder ID
- `description` (string) - File description
- `tags` (string array) - File tags
- `indexed` (boolean) - Whether file is indexed
- `vectorId` (string) - Vector ID from semantic service
- `hash` (string) - SHA-256 hash for deduplication
- `storagePath` (string) - S3 storage path/key
- `status` (string) - Status: 'pending', 'indexed', 'failed'

**Indexes:**
- `userId_idx` on `userId`
- `hash_idx` on `hash` (for deduplication)
- `status_idx` on `status` (for cleanup)
- `indexed_idx` on `indexed`
- `mimeType_idx` on `mimeType`
- `folderId_idx` on `folderId`

---

## File Upload Flow

```
1. Client → presignUpload: Request presigned URL (with file info)
2. presignUpload → Database: Create initial metadata (status: 'pending')
3. presignUpload → Client: Return presigned URL + fileId
4. Client → S3: Upload file using presigned URL
5. Client → indexFile: Call with fileId (to index uploaded file)
6. indexFile → S3: Download file from S3
7. indexFile → Extract text, compute hash
8. indexFile → Semantic Service: POST /index
9. indexFile → Database: Update metadata (hash, indexed: true, status: 'indexed')
```

---

## Security Features

1. **Authentication:** All functions require user authentication via `x-appwrite-user-id` header
2. **Authorization:** Functions verify user ownership before operations
3. **Input Validation:**
   - File names sanitized (alphanumeric + hyphens/underscores/dots only)
   - File size limits (max 100MB)
   - MIME type whitelist
   - Search query length limits (max 500 chars)
   - FileId format validation
4. **Presigned URLs:** Time-limited (15 min upload, 1 hour download)
5. **No Credential Exposure:** S3 credentials never exposed to client

---

## Error Handling

All functions return consistent error responses:
```json
{
  "success": false,
  "error": "Error message"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Bad request (validation errors)
- `401`: Unauthorized (authentication required)
- `403`: Forbidden (authorization failed)
- `404`: Not found
- `500`: Internal server error

---

## Deployment

1. **Install Dependencies:**
   ```bash
   cd backend/appwrite/functions/presignUpload
   npm install
   
   cd ../indexFile
   npm install
   
   cd ../search
   npm install
   
   cd ../presignDownload
   npm install
   ```

2. **Deploy to Appwrite Cloud:**
   - Use Appwrite Console or CLI
   - Set environment variables in function settings
   - Deploy each function with Node.js 18+ runtime

3. **Configure Environment Variables:**
   - Set all required environment variables in Appwrite Functions console
   - Never expose S3 credentials or API keys in client code

---

## Notes

- **Deduplication:** Files with matching SHA-256 hashes reuse existing storage paths
- **Status Tracking:** Files have status field for tracking upload/indexing state
- **Cleanup:** Failed uploads can be identified by `status: 'failed'` and cleaned up later
- **Text Extraction:** Limited support for images (uses filename + description). Full OCR would require additional dependencies like tesseract.js
- **Storage Paths:** Automatically organized by type (photos vs documents) and date/user

