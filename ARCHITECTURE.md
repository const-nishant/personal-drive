# Personal Drive Architecture

## Overview

Personal Drive is a single-user, private Google-Drive-like system with semantic search and auto photo sync. The system follows a thin client architecture where the Flutter client handles only UI and API calls, while all ML/AI processing happens server-side. The goal is to minimize recurring costs, with only storage being a recurring expense.

## Implementation Status

### ✅ Completed
- **Python Service (Unified Backend)**: Fully implemented and tested
  - FastAPI application with comprehensive API endpoints
  - FAISS IndexFlatL2 with disk persistence
  - Sentence Transformer model (all-MiniLM-L6-v2)
  - Thread-safe operations with proper locking
  - Complete file management (upload, download, metadata CRUD)
  - S3 integration with presigned URLs
  - Appwrite Tables integration for metadata
  - API key authentication
  - Comprehensive API documentation

- **Flutter Client Structure**: Service-based architecture implemented
  - Appwrite SDK integration for authentication
  - Service layer (AuthService, FileService, SearchService, PhotoSyncService)
  - Direct Python service communication
  - Modern Flutter architecture

### 🔄 In Progress
- **Flutter UI**: User interface implementation
- **File Upload/Download UI**: Integration with Python service
- **Search Interface**: Flutter search UI components

### 📋 Planned
- **Android Photo Sync**: Background photo synchronization using Workmanager
- **File Preview**: In-app file preview functionality
- **Advanced Search UI**: Enhanced search with filters and sorting

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
         │                   │   │  - Search                    │  │
         │                   │   │  - Metadata Management      │  │
         │                   │   └──────────────────────────────┘  │
         │                   └──────────────────────────────────────┘
         │ Auth                          │              │              │
         ▼                               ▼              ▼              ▼
┌─────────────────┐         ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Appwrite      │         │   Appwrite  │ │ S3 Storage  │ │   FAISS     │
│   Authentication│         │   Tables    │ │  (B2/R2)    │ │   Index     │
│                 │         │   (Metadata)│ │             │ │ (Disk-based)│
└─────────────────┘         └─────────────┘ └─────────────┘ └─────────────┘
```

## Components

### 1. Frontend (Flutter - Thin Client) 🔄 **IN PROGRESS**

**Location:** `frontend/personal_drive/`

**Responsibilities:**
- User interface and user experience
- File upload and management (UI only)
- Search interface (UI only)
- Authentication handling (via Appwrite SDK)
- Android auto photo sync (Android only)

**Service Architecture:**
```
lib/
├── core/
│   ├── appwrite_client.dart    # Appwrite client initialization
│   ├── config.dart             # Configuration constants
│   └── utils/                  # Utility functions
├── services/
│   ├── auth_service.dart       # Authentication via Appwrite SDK
│   ├── file_service.dart       # File operations via Python service
│   ├── search_service.dart     # Search operations via Python service
│   └── photosync_service.dart  # Android photo sync
├── features/                   # Feature-specific UI and logic
└── ui/                        # Shared UI components
```

**Key Features:**
- Flutter-based cross-platform client (Android/Desktop)
- Appwrite SDK integration (authentication only)
- Direct API calls to Python service (with API key + user ID)
- File upload/download via presigned URLs
- Semantic search interface
- File preview capabilities
- **NO ML/AI processing** - all handled server-side
- **NO direct S3 access** - uses presigned URLs from Python service
- **NO Appwrite Functions** - all logic in Python service

**Architecture Principle:** Thin client - lightweight with no ML/AI processing

**Status:** Service layer complete, UI implementation in progress.

### 2. Backend (Appwrite Cloud) ✅ **AUTHENTICATION & METADATA**

**Location:** Appwrite Cloud (https://cloud.appwrite.io)

**Components:**

#### Appwrite Authentication
- **Email/Password**: User registration and login
- **OAuth Providers**: Optional OAuth integration (Google, GitHub, etc.)
- **Session Management**: JWT-based session tokens

#### Appwrite Tables (Database)
- **files collection**: Stores file metadata
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

**Responsibilities:**
- User authentication and authorization (single-user system)
- **NO orchestration** - Python service handles all operations
- **NO Functions** - removed from architecture
- Metadata storage via Appwrite Tables API (accessed by Python service)

**Architecture Principle:** Authentication and metadata storage only

**Status:** Tables configured, authentication working. No functions needed.

### 3. Python Service (Unified Backend) ✅ **COMPLETE**

**Location:** `backend/semantic/`

**Technology Stack:**
- FastAPI (Web framework)
- FAISS IndexFlatL2 (Vector database)
- Sentence Transformers (all-MiniLM-L6-v2 model, 384 dimensions)
- Appwrite Python SDK (Tables API)
- Boto3 (S3 operations)
- Thread-safe operations with Lock

**Module Structure:**
```
backend/semantic/
├── app.py                    # FastAPI application entry point
├── config.py                 # Configuration management
├── auth.py                   # API key authentication
├── requirements.txt          # Python dependencies
├── API.md                    # API documentation
├── TESTING.md                # Testing documentation
├── clients/
│   ├── __init__.py
│   ├── appwrite_client.py   # Appwrite Tables client
│   └── s3_client.py         # S3 storage client
├── models/
│   ├── __init__.py
│   ├── schemas.py           # Pydantic schemas
│   └── file_metadata.py     # File metadata models
├── services/
│   ├── __init__.py
│   ├── file_service.py      # File operations
│   └── semantic_indexer.py  # Semantic indexing and search
├── utils/
│   ├── __init__.py
│   ├── text_extractor.py    # Text extraction from files
│   └── hasher.py            # SHA-256 hashing
└── index/                   # FAISS index storage (created at runtime)
    ├── faiss.index          # FAISS index file
    └── meta.pkl             # Metadata pickle file
```

**Responsibilities:**
- **File Operations**: Upload presigned URLs, download presigned URLs, file metadata CRUD
- **Text Extraction**: PDF, DOCX, TXT, and other file formats
- **Semantic Indexing**: Vector embedding generation and FAISS index management
- **Search**: Semantic search with file metadata filtering
- **S3 Integration**: Presigned URL generation, file upload/download coordination
- **Appwrite Tables**: Metadata storage and retrieval
- **Direct client access** - Flutter client calls Python service directly (with API key + user ID)

**Architecture Principle:** Unified backend - all business logic in one service

**Status:** Fully implemented with comprehensive API.

## Data Flow

### File Upload Flow (MUST FOLLOW EXACTLY)

```
1. Flutter: User authenticates via Appwrite SDK
   └─► Returns: user ID and session token

2. Flutter → Python Service: POST /api/v1/upload/presign
   Headers: X-API-Key, X-User-Id
   Body: { name, size, mimeType, folderId?, description?, tags? }
   └─► Python Service:
       ├─► Validates API key and user ID
       ├─► Validates file (size, MIME type)
       ├─► Creates metadata record in Appwrite Tables
       ├─► Generates presigned S3 upload URL
       └─► Returns: { fileId, upload: { url, expiresIn } }

3. Flutter → S3 Storage: PUT (upload file directly)
   Uses presigned URL from step 2
   └─► S3: Stores file at generated key

4. Flutter → Python Service: POST /api/v1/upload/complete
   Headers: X-API-Key, X-User-Id
   Body: { fileId }
   └─► Python Service:
       ├─► Downloads file from S3
       ├─► Computes SHA-256 hash
       ├─► Extracts text content
       ├─► Generates embedding (if text extracted)
       ├─► Adds embedding to FAISS index
       ├─► Updates metadata in Appwrite Tables
       │   (indexed=true, hash, status="completed")
       └─► Returns: { status: "indexed", fileId, hash }

5. Python Service → FAISS: Store embedding
   └─► Updates index on disk (faiss.index, meta.pkl)
```

**Key Points:**
- Client NEVER directly accesses S3 credentials
- Client calls Python service directly (with API key + user ID authentication)
- All orchestration happens in Python service
- User authentication handled by Flutter Appwrite SDK
- Text extraction and indexing happen asynchronously

### Search Flow (MUST FOLLOW EXACTLY)

```
1. Flutter: User authenticates via Appwrite SDK
   └─► Returns: user ID and session token

2. Flutter → Python Service: POST /api/v1/search
   Headers: X-API-Key, X-User-Id
   Body: { query, k?, folderId? }
   └─► Python Service:
       ├─► Validates API key and user ID
       ├─► Generates query embedding
       ├─► Searches FAISS index
       ├─► Filters results by user ID (from Appwrite Tables)
       ├─► Ranks results by similarity score
       └─► Returns: { results: [...], query, total }

3. Python Service → FAISS: Find similar documents
   └─► Returns: list of (file_id, score) tuples

4. Python Service → Appwrite Tables: Fetch file metadata
   └─► Returns: complete file metadata for each result

5. Python Service → Flutter: Return complete results
   └─► Includes: file metadata + similarity scores
```

**Key Points:**
- Client calls Python service directly (with API key + user ID authentication)
- All search logic in Python service
- Results filtered by userId automatically
- Full file metadata included in response

### Photo Sync Flow (Android Only)

```
1. Background task (Workmanager) scans DCIM/Pictures directories
   └─► Finds new/changed images

2. For each image:
   ├─► Compute SHA-256 hash
   ├─► Flutter → Python Service: POST /api/v1/upload/presign
   │   Headers: X-API-Key, X-User-Id
   │   Body: { name, size, mimeType, hash }
   │   └─► Python Service:
   │       ├─► Checks Appwrite Tables for existing hash
   │       ├─► If exists: returns existing fileId (skip upload)
   │       └─► If new: creates metadata, generates presigned URL
   │
   ├─► If new file:
   │   ├─► Flutter → S3: Upload file using presigned URL
   │   └─► Flutter → Python Service: POST /api/v1/upload/complete
   │       └─► Python Service: Extract text, index, update metadata
   │
   └─► If existing file:
       └─► Skip upload (deduplication working)
```

**Key Points:**
- Android-only feature (iOS not supported)
- Uses Workmanager for background tasks
- Sync only on Wi-Fi and charging (configurable)
- Deduplication via SHA-256 hash
- No duplicate uploads for identical files

## Technology Stack

### Frontend
- **Framework:** Flutter (latest stable)
- **Platforms:** Android, Desktop (Windows/Linux/macOS)
- **State Management:** Provider or Riverpod (if needed)
- **File Handling:** Appwrite SDK, image_picker
- **Background Tasks:** Workmanager (Android only)
- **Permissions:** permission_handler (planned)
- **HTTP Client:** http or dio (for Python service calls)

### Backend
- **Platform:** Appwrite Cloud (https://cloud.appwrite.io) - Authentication & Metadata
- **Database:** Appwrite Cloud Tables (metadata storage)
- **Storage:** S3-compatible storage (Backblaze B2 or Cloudflare R2)
- **Authentication:** Appwrite Auth (single-user) - handled by Flutter SDK
- **Python Service:** FastAPI (unified backend) - all business logic

### Semantic Search
- **Language:** Python 3.9+
- **Framework:** FastAPI
- **ML Models:** Sentence Transformers (all-MiniLM-L6-v2)
- **Vector DB:** FAISS IndexFlatL2
- **Embedding Dimension:** 384
- **Index Persistence:** Disk-based (faiss.index, meta.pkl)
- **Thread Safety:** Lock for index updates

### Infrastructure
- **Containerization:** Docker (optional)
- **File Storage:** S3-compatible (B2/R2) - only recurring cost
- **Vector Storage:** FAISS indices (disk-based, self-hosted)
- **Authentication:** Appwrite Cloud

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
- **NEVER expose Appwrite API keys to Flutter client**
- Presigned URLs generated server-side (time-limited: 15 min upload, 1 hour download)
- Input validation and sanitization (file names, sizes, MIME types, search queries)
- File deduplication via SHA-256 hash
- API key rotation recommended for production

### Network Security
- HTTPS/TLS encryption for all communications
- **NO direct client → S3 communication** (presigned URLs only)
- **Direct client → Python Service communication** (with API key + user ID authentication)
- User authentication handled by Flutter Appwrite SDK
- Network isolation between services

### Security Headers
```
X-API-Key: your-service-api-key        # Python service authentication
X-User-Id: user-id-from-appwrite       # User context (set by Flutter)
```

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
- **Storage**: S3-compatible storage (B2/R2) - recurring cost (~$5/TB/month)
- **Appwrite Cloud**: Free tier available (up to 25K reads/day), paid plans for production
- **Python Service Hosting**: Self-hosted (no cost) or cloud hosting (varies)

### Storage Optimization
- Use cheapest S3-compatible storage (B2 or R2)
- Implement deduplication to minimize storage
- Clean up temporary files
- Compress text embeddings in FAISS index

### Compute Optimization
- Use serverless functions where possible (not applicable in current architecture)
- Optimize semantic service performance (batch processing)
- Cache embeddings when possible
- Use efficient algorithms (FAISS IndexFlatL2)

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

## Deployment Architecture

### Development
```
Local Machine:
├─ Flutter App (hot reload)
├─ Python Service (uvicorn --reload)
└─ Appwrite Cloud (remote)
   ├─ Authentication
   └─ Tables (metadata)
S3 Storage (remote)
```

### Production
```
Cloud Infrastructure:
├─ Flutter App (compiled, distributed via Play Store/GitHub)
├─ Python Service (Docker container on VPS/cloud)
├─ Appwrite Cloud (remote)
│  ├─ Authentication
│  └─ Tables (metadata)
└─ S3 Storage (B2/R2)
   └─ FAISS Index (disk-based, backed up to S3)
```

## Performance Considerations

### Index Size
- FAISS IndexFlatL2: O(n) search time
- 384-dimensional embeddings
- ~1.5KB per document embedding
- 1000 documents = ~1.5MB index
- 10000 documents = ~15MB index

### Search Performance
- Linear search with FAISS IndexFlatL2
- Suitable for single-user system (up to 10K documents)
- For larger datasets, consider FAISS IVF or HNSW indexes

### Upload Performance
- Presigned URLs enable direct S3 upload (bypasses Python service)
- Text extraction and indexing happen asynchronously
- No blocking on upload completion

### Caching Strategy
- Cache presigned URLs client-side (15-minute expiry)
- Cache file metadata in Flutter app
- FAISS index cached in memory (Python service)
```
