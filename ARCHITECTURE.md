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
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter       │    │   Appwrite      │    │   Semantic      │
│   Client        │◄──►│   (Backend)     │◄──►│   Service       │
│   (Thin)        │    │   (Orchestrator)│    │   (FastAPI)     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
        │                       │                       │
        │                       │                       │
        ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────┐
│                     Infrastructure Layer                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Docker    │  │   S3 Storage│  │   FAISS Index       │  │
│  │  Containers │  │   (B2/R2)   │  │   (Disk-based)      │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
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
- Appwrite SDK integration
- Semantic search interface (queries Appwrite Functions)
- File preview capabilities
- **NO ML/AI processing** - all handled server-side
- **NO direct S3 access** - uses presigned URLs
- **NO direct semantic service access** - goes through Appwrite Functions

**Architecture Principle:** Thin client - lightweight with no ML/AI processing

**Status:** Basic structure exists, full implementation pending.

### 2. Backend (Appwrite) 🔄 **IN PROGRESS**

**Location:** `backend/appwrite/`

**Components:**

#### Appwrite Functions
- **indexFile:** Processes uploaded files for semantic indexing (calls semantic service) - 📋 Planned
- **search:** Handles search queries and coordinates with semantic service - 📋 Planned
- **presignUpload:** Generates pre-signed URLs for secure S3 uploads - 📋 Planned

#### Database Collections
- **files:** Stores file metadata (fileId, name, hash, mime, size, storagePath, createdAt, owner) - 📋 Planned

**Responsibilities:**
- User authentication and authorization (single-user system)
- Metadata storage and management
- Function orchestration (coordinates between client, semantic service, and storage)
- Presigned URL generation for S3-compatible storage
- **NO direct file storage** - files stored in S3-compatible storage (B2/R2)

**Architecture Principle:** Orchestration layer - coordinates between services

**Status:** Function code exists but needs deployment and integration with semantic service.

### 3. Semantic Search Service (Python) ✅ **COMPLETE**

**Location:** `backend/semantic/`

**Technology Stack:**
- FastAPI (Web framework)
- FAISS IndexFlatL2 (Vector database)
- Sentence Transformers (all-MiniLM-L6-v2 model, 384 dimensions)
- Thread-safe operations with Lock

**Responsibilities:**
- Vector embedding generation (server-side only)
- Semantic index management (FAISS index persisted to disk)
- Search query processing
- Document similarity matching
- **NO direct client access** - only accessible via Appwrite Functions

**Architecture Principle:** Stateless service with disk-based index persistence

**Status:** Fully implemented with all endpoints, testing, and documentation complete.

## Data Flow

### File Upload Flow (MUST FOLLOW EXACTLY)

```
1. Client → Appwrite Function (presignUpload): Request presigned URL
2. Appwrite Function → Client: Return presigned URL (time-limited, 15 minutes)
3. Client → S3 Storage (B2/R2): Upload file directly using presigned URL
4. Storage → Appwrite Function (indexFile): Trigger via webhook/event
5. Appwrite Function → Semantic Service: POST /index with file_id and text
6. Semantic Service → FAISS: Generate embedding and store in index
7. Semantic Service → Appwrite Function: Return success status
8. Appwrite → Database: Save file metadata (fileId, hash, storagePath, etc.)
```

**Key Points:**
- Client NEVER directly accesses S3 credentials
- Client NEVER directly accesses semantic service
- All orchestration happens through Appwrite Functions

### Search Flow (MUST FOLLOW EXACTLY)

```
1. Client → Appwrite Function (search): POST search request with query
2. Appwrite Function → Semantic Service: POST /search with query and k
3. Semantic Service → FAISS: Generate query embedding and find similar documents
4. Semantic Service → Appwrite Function: Return file_ids array
5. Appwrite → Database: Fetch file metadata for returned file_ids
6. Appwrite → Client: Return complete results with metadata
```

**Key Points:**
- Client NEVER directly queries semantic service
- All search goes through Appwrite Functions
- Results include full file metadata from Appwrite database

### Photo Sync Flow (Android Only)

```
1. Background task (Workmanager) scans DCIM/Pictures directories
2. Filter images (by date, size, etc.)
3. Compute SHA-256 hash for each image
4. Check Appwrite DB for existing hash
5. If new: Upload via presigned URL (same as file upload flow)
6. Save metadata in Appwrite database
7. Trigger indexing automatically via indexFile function
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
- **Platform:** Appwrite Cloud (https://cloud.appwrite.io)
- **Functions:** Node.js (JavaScript) - deployed to Appwrite Cloud
- **Database:** Appwrite Cloud Databases (metadata only)
- **Storage:** S3-compatible storage (Backblaze B2 or Cloudflare R2)
- **Authentication:** Appwrite Auth (single-user)

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
- Appwrite authentication for all user operations
- Single-user system (user-scoped data access only)
- Server API keys for Appwrite Functions → Semantic Service communication
- **NO public endpoints** (except health checks)

### Data Protection
- **NEVER expose S3 credentials to Flutter client**
- Presigned URLs generated server-side (time-limited: 15 min upload, 1 hour download)
- Input validation and sanitization (file names, sizes, MIME types, search queries)
- File deduplication via SHA-256 hash

### Network Security
- HTTPS/TLS encryption for all communications
- **NO direct client → S3 communication** (presigned URLs only)
- **NO direct client → Semantic Service communication** (Appwrite Functions only)
- Network isolation between services

## Storage Architecture

### File Organization
- **Photos:** `photos/YYYY/MM/filename.ext`
- **Documents:** `documents/user_id/filename.ext`
- Original filenames preserved in metadata

### File Metadata (Appwrite Database)
- `fileId` (string, primary key)
- `name` (string, original filename)
- `hash` (string, SHA-256)
- `mime` (string, MIME type)
- `size` (int, bytes)
- `storagePath` (string, S3 key)
- `createdAt` (datetime)
- `owner` (string, Appwrite user ID)

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
- **Flutter client → Appwrite (via SDK) ONLY**
- **Appwrite Functions → Semantic Service (via HTTP) ONLY**
- **Semantic Service → Storage (via S3 API, indirect through Appwrite)**
- ❌ **NEVER direct client → Semantic Service**
- ❌ **NEVER direct client → S3**

### Thin Client Principle (MANDATORY)
- Flutter client MUST remain lightweight
- **NO ML/AI processing in Flutter**
- All semantic search happens server-side
- All embeddings generated server-side
- Client only handles UI, file picking, and API calls

## Build Order (DO NOT CHANGE)

1. Set up Appwrite Cloud account and project
2. Set up storage bucket (B2/R2)
3. Create Appwrite Cloud database schema
4. Implement metadata CRUD operations
5. Deploy semantic service
6. Create and deploy Appwrite Cloud functions
7. Implement Flutter upload flow
8. Implement search UI
9. Implement Android auto-sync
10. Add encryption (optional)

## API Design

### Semantic Service Endpoints (MUST HAVE)
- `POST /index` - Index a document (file_id, text)
- `POST /search` - Search documents (query, k)
- `GET /health` - Health check
- `GET /stats` - Service statistics

### Request/Response Format
- Request: JSON body with validated Pydantic schema
- Response: JSON with consistent structure
- Error responses: HTTPException with appropriate status codes
- Success responses: `{"status": "indexed"}` or SearchResponse model

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