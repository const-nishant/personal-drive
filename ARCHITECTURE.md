# Personal Drive Architecture

## Overview

Personal Drive is a single-user, private Google-Drive-like system with semantic search and auto photo sync. The system follows a thin client architecture where the Flutter client handles only UI and API calls, while all ML/AI processing happens server-side. The goal is to minimize recurring costs, with only storage being a recurring expense.

## Implementation Status

### ✅ Completed
- **Semantic Search Service (FastAPI)**: Fully implemented and tested
  - FastAPI application with all endpoints (`/index`, `/search`, `/health`, `/stats`)
  - FAISS IndexFlatL2 with disk persistence
  - Sentence Transformer model (all-MiniLM-L6-v2)
  - Thread-safe operations
  - Comprehensive testing documentation

### 🔄 In Progress
- **Appwrite Functions**: Basic structure in place, needs integration with semantic service
- **Flutter Client**: Basic structure and Appwrite SDK integration started

### 📋 Planned
- **Appwrite Cloud Setup**: Project creation and configuration
- **S3 Storage**: Backblaze B2 or Cloudflare R2 integration
- **Database Schema**: File metadata collection setup
- **File Management**: Upload, download, preview, delete functionality
- **Search UI**: Flutter interface for semantic search
- **Android Photo Sync**: Background photo synchronization

## System Architecture

### High-Level Architecture

```
┌─────────────────┐         ┌──────────────────────────────────────┐
│   Flutter       │         │   Python Service (FastAPI)          │
│   Client        │────────►│   (Unified Backend)                 │
│   (Thin)        │         │   ┌──────────────────────────────┐  │
│                 │         │   │  - File Operations            │  │
│   Appwrite SDK  │         │   │  - S3 Presigned URLs          │  │
│   (Auth Only)   │         │   │  - Text Extraction           │  │
└─────────────────┘         │   │  - Semantic Indexing         │  │
                            │   │  - Search                    │  │
                            │   └──────────────────────────────┘  │
                            └──────────────────────────────────────┘
                                    │              │              │
                                    ▼              ▼              ▼
                            ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
                            │   Appwrite  │ │ S3 Storage  │ │   FAISS     │
                            │   Tables    │ │  (B2/R2)    │ │   Index     │
                            │   (Metadata)│ │             │ │ (Disk-based)│
                            └─────────────┘ └─────────────┘ └─────────────┘
```

## Components

### 1. Frontend (Flutter - Thin Client) 📋 **PLANNED**

**Location:** `frontend/personal_drive/`

**Responsibilities:**
- User interface and user experience
- File upload and management (UI only)
- Search interface (UI only)
- Authentication handling (via Appwrite SDK)
- Android auto photo sync (Android only)

**Key Features:**
- Flutter-based cross-platform client (Android/Desktop)
- Appwrite SDK integration (authentication only)
- Direct API calls to Python service (with API key)
- File upload/download via presigned URLs
- Semantic search interface
- File preview capabilities
- **NO ML/AI processing** - all handled server-side
- **NO direct S3 access** - uses presigned URLs from Python service
- **NO Appwrite Functions** - all logic in Python service

**Architecture Principle:** Thin client - lightweight with no ML/AI processing

**Status:** Basic structure exists, full implementation pending.

### 2. Backend (Appwrite) ✅ **AUTHENTICATION ONLY**

**Location:** `backend/appwrite/` (for reference only, not actively used)

**Components:**

#### Appwrite Tables
- **files:** Stores file metadata (fileId, name, hash, mime, size, storagePath, createdAt, userId) - ✅ Configured

**Responsibilities:**
- User authentication and authorization (single-user system)
- **NO orchestration** - Python service handles all operations
- **NO Functions** - removed from architecture
- Metadata storage via Appwrite Tables API (accessed by Python service)

**Architecture Principle:** Authentication and metadata storage only

**Status:** Tables configured, authentication working. No functions needed.

### 3. Python Service (Unified Backend) 🔄 **IN PROGRESS**

**Location:** `backend/semantic/`

**Technology Stack:**
- FastAPI (Web framework)
- FAISS IndexFlatL2 (Vector database)
- Sentence Transformers (all-MiniLM-L6-v2 model, 384 dimensions)
- Appwrite Python SDK (Tables API)
- Boto3 (S3 operations)
- Thread-safe operations with Lock

**Responsibilities:**
- **File Operations**: Upload presigned URLs, download presigned URLs, file metadata CRUD
- **Text Extraction**: PDF, DOCX, and other file formats
- **Semantic Indexing**: Vector embedding generation and FAISS index management
- **Search**: Semantic search with file metadata filtering
- **S3 Integration**: Presigned URL generation, file upload/download coordination
- **Appwrite Tables**: Metadata storage and retrieval
- **Direct client access** - Flutter client calls Python service directly (with API key)

**Architecture Principle:** Unified backend - all business logic in one service

**Status:** Modular structure being implemented. See API.md for endpoint documentation.

## Data Flow

### File Upload Flow (MUST FOLLOW EXACTLY)

```
1. Flutter: User authenticates via Appwrite SDK
2. Flutter → Python Service: POST /api/v1/upload/presign
   - Headers: X-API-Key, X-User-Id
   - Body: { name, size, mimeType, folderId?, description?, tags? }
3. Python Service → Appwrite Tables: Create file metadata record
4. Python Service → S3: Generate presigned upload URL
5. Python Service → Flutter: Return presigned URL + fileId
6. Flutter → S3 Storage: Upload file directly using presigned URL
7. Flutter → Python Service: POST /api/v1/upload/complete
   - Headers: X-API-Key, X-User-Id
   - Body: { fileId }
8. Python Service → S3: Download file from storage
9. Python Service: Extract text, compute hash, generate embedding
10. Python Service → FAISS: Store embedding in index
11. Python Service → Appwrite Tables: Update metadata (indexed=true, hash)
```

**Key Points:**
- Client NEVER directly accesses S3 credentials
- Client calls Python service directly (with API key authentication)
- All orchestration happens in Python service
- User authentication handled by Flutter Appwrite SDK

### Search Flow (MUST FOLLOW EXACTLY)

```
1. Flutter: User authenticates via Appwrite SDK
2. Flutter → Python Service: POST /api/v1/search
   - Headers: X-API-Key, X-User-Id
   - Body: { query, k?, folderId? }
3. Python Service: Generate query embedding
4. Python Service → FAISS: Find similar documents
5. Python Service → Appwrite Tables: Fetch file metadata for results (filtered by userId)
6. Python Service → Flutter: Return complete results with metadata
```

**Key Points:**
- Client calls Python service directly (with API key authentication)
- All search logic in Python service
- Results filtered by userId automatically
- Full file metadata included in response

### Photo Sync Flow (Android Only)

```
1. Background task (Workmanager) scans DCIM/Pictures directories
2. Filter images (by date, size, etc.)
3. Compute SHA-256 hash for each image
4. Flutter → Python Service: POST /api/v1/upload/presign (with hash check)
5. Python Service → Appwrite Tables: Check for existing hash
6. If new: Python Service returns presigned URL
7. Flutter → S3: Upload file directly
8. Flutter → Python Service: POST /api/v1/upload/complete
9. Python Service: Extract text, index, update metadata
```

**Key Points:**
- Android-only feature (iOS not supported)
- Uses Workmanager for background tasks
- Sync only on Wi-Fi and charging (configurable)
- Deduplication via SHA-256 hash

## Technology Stack

### Frontend
- **Framework:** Flutter (latest stable)
- **Platforms:** Android, Desktop (Windows/Linux/macOS)
- **State Management:** Provider or Riverpod (if needed)
- **File Handling:** Appwrite SDK, file_picker
- **Background Tasks:** Workmanager (Android only)
- **Permissions:** permission_handler
- **Crypto:** crypto (for SHA-256 hashing)

### Backend
- **Platform:** Appwrite Cloud (https://cloud.appwrite.io) - Authentication only
- **Database:** Appwrite Cloud Tables (metadata storage)
- **Storage:** S3-compatible storage (Backblaze B2 or Cloudflare R2)
- **Authentication:** Appwrite Auth (single-user) - handled by Flutter SDK
- **Python Service:** FastAPI (unified backend) - all business logic

### Semantic Search
- **Language:** Python 3.9+
- **Framework:** FastAPI (NOT Flask)
- **ML Models:** Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB:** FAISS IndexFlatL2
- **Embedding Dimension:** 384
- **Index Persistence:** Disk-based (faiss.index, meta.pkl)
- **Thread Safety:** Lock for index updates

### Infrastructure
- **Containerization:** Docker
- **File Storage:** S3-compatible (B2/R2) - only recurring cost
- **Vector Storage:** FAISS indices (disk-based, self-hosted)
- **Orchestration:** Appwrite Functions

## Security Architecture

### Authentication & Authorization
- Appwrite authentication for all user operations (handled by Flutter SDK)
- Single-user system (user-scoped data access only)
- API key authentication for Python service (X-API-Key header)
- User ID passed via X-User-Id header (set by Flutter after Appwrite auth)
- Python service uses Appwrite API key for Tables operations
- **NO public endpoints** (except /health and /)

### Data Protection
- **NEVER expose S3 credentials to Flutter client**
- Presigned URLs generated server-side (time-limited: 15 min upload, 1 hour download)
- Input validation and sanitization (file names, sizes, MIME types, search queries)
- File deduplication via SHA-256 hash

### Network Security
- HTTPS/TLS encryption for all communications
- **NO direct client → S3 communication** (presigned URLs only)
- **Direct client → Python Service communication** (with API key authentication)
- User authentication handled by Flutter Appwrite SDK
- Network isolation between services

## Storage Architecture

### File Organization
- **Photos:** `photos/YYYY/MM/filename.ext`
- **Documents:** `documents/user_id/filename.ext`
- Original filenames preserved in metadata

### File Metadata (Appwrite Tables)
- `fileId` (string, unique identifier)
- `name` (string, original filename)
- `hash` (string, SHA-256)
- `mimeType` (string, MIME type)
- `size` (int, bytes)
- `storagePath` (string, S3 key)
- `createdAt` (datetime)
- `userId` (string, Appwrite user ID)
- `folderId` (string, optional)
- `description` (string, optional)
- `tags` (array of strings, optional)
- `indexed` (boolean, default: false)
- `status` (string, default: "pending")

### Deduplication
- Check SHA-256 hash before upload
- If hash exists, reuse existing file
- Create new metadata entry with same storagePath

## Cost Optimization

### Recurring Costs
- **Storage**: S3-compatible storage (B2/R2) - recurring cost
- **Appwrite Cloud**: Free tier available, paid plans for production
- **Semantic Service**: Self-hosted (no recurring cost) or cloud hosting

### Storage Optimization
- Use cheapest S3-compatible storage (B2 or R2)
- Implement deduplication to minimize storage
- Clean up temporary files

### Compute Optimization
- Use serverless functions (Appwrite) where possible
- Optimize semantic service performance
- Cache embeddings when possible
- Use efficient algorithms (FAISS)

## Service Boundaries (STRICT)

### Communication Rules
- **Flutter client → Appwrite (via SDK)**: Authentication only
- **Flutter client → Python Service (via HTTP)**: All operations (with API key + X-User-Id)
- **Python Service → Appwrite Tables (via SDK)**: Metadata operations (using Appwrite API key)
- **Python Service → S3 (via boto3)**: Presigned URL generation, file operations
- ❌ **NEVER direct client → S3** (presigned URLs only)
- ✅ **Direct client → Python Service** (with proper authentication)

### Thin Client Principle (MANDATORY)
- Flutter client MUST remain lightweight
- **NO ML/AI processing in Flutter**
- All semantic search happens server-side
- All embeddings generated server-side
- Client only handles UI, file picking, and API calls
- User authentication via Appwrite SDK

## Build Order (DO NOT CHANGE)

1. Set up Appwrite Cloud account and project
2. Set up storage bucket (B2/R2)
3. Create Appwrite Cloud Tables schema
4. Deploy Python service (unified backend)
5. Implement Flutter upload flow (direct to Python service)
6. Implement search UI (direct to Python service)
7. Implement Android auto-sync
8. Add encryption (optional)

## API Design

### Python Service Endpoints

See [API.md](./backend/semantic/API.md) for complete API documentation.

**File Operations:**
- `POST /api/v1/upload/presign` - Generate presigned upload URL
- `POST /api/v1/upload/complete` - Complete upload and index
- `GET /api/v1/files` - List user's files
- `GET /api/v1/files/{file_id}` - Get file metadata
- `PUT /api/v1/files/{file_id}` - Update file metadata
- `DELETE /api/v1/files/{file_id}` - Delete file
- `GET /api/v1/files/{file_id}/download` - Get presigned download URL

**Search:**
- `POST /api/v1/search` - Semantic search

**System:**
- `GET /health` - Health check
- `GET /stats` - Service statistics
- `GET /` - API information

### Request/Response Format
- Request: JSON body with validated Pydantic schema
- Headers: `X-API-Key` (required), `X-User-Id` (required for user operations)
- Response: JSON with consistent structure
- Error responses: HTTPException with appropriate status codes
- Success responses: Consistent JSON structure per endpoint

## Android-Specific Architecture

### Photo Sync Platform
- **Android ONLY** (iOS not supported)
- Uses Workmanager for background tasks
- Frequency: 6 hours (configurable)
- Constraints: NetworkType.unmetered, requiresCharging

### Permissions Required
- READ_MEDIA_IMAGES for photo access
- FOREGROUND_SERVICE for background sync
- Request permissions at runtime
- Handle permission denial gracefully