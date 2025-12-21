# Features

## Core Features

### File Management
- **Upload Files**: Upload multiple files simultaneously via Flutter file picker
- **File Organization**: View and organize files with metadata stored in Appwrite
- **File Preview**: Preview common file types (PDF, images, documents) without downloading
- **Secure Uploads**: Presigned URLs for secure direct-to-S3 uploads (no credentials exposed)
- **File Deduplication**: Automatic deduplication via SHA-256 hash checking
- **File Metadata**: Store file information (name, size, MIME type, hash, storage path)

### Search & Discovery
- **Semantic Search**: AI-powered search that understands meaning and context (server-side)
- **Natural Language Queries**: Search using natural language instead of exact keywords
- **Filter & Sort**: Filter by file type, date, size, and sort by various criteria
- **Recent Files**: Quick access to recently uploaded and accessed files
- **Search History**: Track search queries for quick access

### AI-Powered Features (Server-Side)
- **Document Indexing**: Automatic text extraction and indexing via Appwrite Functions
- **Vector Embeddings**: Generate embeddings using all-MiniLM-L6-v2 model (384 dimensions)
- **FAISS Search**: Fast similarity search using FAISS IndexFlatL2
- **Similar Document Detection**: Find documents with similar content or themes
- **Thread-Safe Operations**: Concurrent indexing and searching with proper locking

### User Experience
- **Cross-Platform**: Flutter app works on Android and Desktop (Windows/Linux/macOS)
- **Dark/Light Theme**: Toggle between themes for comfortable viewing
- **Progress Tracking**: Real-time upload/download progress
- **Error Handling**: Graceful error handling with user-friendly messages
- **Thin Client**: Lightweight client with no ML/AI processing (all server-side)

## Advanced Features

### Android Auto Photo Sync (Android Only)
- **Background Sync**: Automatic photo synchronization using Workmanager
- **Smart Filtering**: Filter images by date, size, and other criteria
- **Deduplication**: SHA-256 hash checking prevents duplicate uploads
- **Battery Optimization**: Sync only on Wi-Fi and charging (configurable)
- **Permission Handling**: Runtime permission requests with graceful handling
- **Sync Frequency**: Configurable sync interval (default: 6 hours)
- **Foreground Service**: Reliable background operation with foreground service

### Security & Privacy
- **Presigned URLs**: Time-limited upload/download URLs (15 min upload, 1 hour download)
- **No Credential Exposure**: S3 credentials never exposed to Flutter client
- **Input Validation**: All inputs validated and sanitized (file names, sizes, MIME types)
- **Authentication**: Appwrite authentication for all user operations
- **Single-User System**: User-scoped data access only
- **Audit Logging**: Comprehensive logging of all operations (server-side)

### Storage Architecture
- **S3-Compatible Storage**: Backblaze B2 or Cloudflare R2 integration
- **Cost Optimization**: Only storage is a recurring cost
- **File Organization**: Structured paths (photos/YYYY/MM/, documents/user_id/)
- **Metadata Storage**: File metadata stored in Appwrite database
- **Index Persistence**: FAISS index persisted to disk for reliability

### Performance
- **Chunked Uploads**: Large file uploads with automatic retry
- **Efficient Search**: FAISS IndexFlatL2 for fast similarity search
- **Thread-Safe Operations**: Concurrent operations with proper locking
- **Index Persistence**: Disk-based index for fast startup and reliability

## Platform Support

### Supported Platforms
- ✅ **Android**: Full support with auto photo sync
- ✅ **Desktop (Windows)**: Full file management and search
- ✅ **Desktop (Linux)**: Full file management and search
- ✅ **Desktop (macOS)**: Full file management and search
- ❌ **iOS**: Not currently supported (photo sync is Android-only)

### Feature Matrix

| Feature | Android | Desktop |
|---------|---------|---------|
| File Upload | ✅ | ✅ |
| File Download | ✅ | ✅ |
| Semantic Search | ✅ | ✅ |
| Photo Sync | ✅ | ❌ |
| File Preview | ✅ | ✅ |
| Dark/Light Theme | ✅ | ✅ |

## Feature Status

### ✅ Implemented
- **Semantic Search Service**: FastAPI service with FAISS indexing
  - Document indexing endpoint (`POST /index`)
  - Search endpoint (`POST /search`)
  - Health check endpoint (`GET /health`)
  - Stats endpoint (`GET /stats`)
  - FAISS IndexFlatL2 with disk persistence
  - Sentence Transformer model (all-MiniLM-L6-v2)
  - Thread-safe operations with Lock
  - Index persistence to disk (faiss.index, meta.pkl)

### 🔄 In Progress
- **Appwrite Functions**: indexFile, search, presignUpload functions
- **Flutter Client**: Basic UI structure and Appwrite integration

### 📋 Planned
- **File Management**: Upload, download, preview, delete
- **Search UI**: Flutter interface for semantic search
- **Android Photo Sync**: Background photo synchronization
- **File Metadata**: CRUD operations in Appwrite database
- **S3 Storage Integration**: Presigned URL generation and file storage

### 🔮 Future
- **Advanced Features**: Enhanced search UI, file preview improvements
- **Desktop Features**: Desktop-specific optimizations
- **iOS Support**: iOS app (without photo sync)

## Architecture Highlights

- **Thin Client**: Flutter client handles only UI and API calls
- **Server-Side ML**: All AI/ML processing happens server-side
- **Secure Architecture**: No credentials exposed to client
- **Cost-Effective**: Only storage is a recurring cost
- **Scalable**: Stateless design with disk-based index persistence