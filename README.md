---
title: Personal Drive Semantic Service
sdk: docker
---


# Personal Drive - AI-Powered Document Management System

Personal Drive is a single-user, private Google-Drive-like system with semantic search and auto photo sync. Built with Flutter (thin client), Appwrite (authentication), FastAPI (unified backend), and S3-compatible storage (B2/R2), it provides secure file storage with intelligent semantic search capabilities. The system is designed to minimize recurring costs, with only storage being a recurring expense.

## 🚀 Features

- **Semantic Search Service**: ✅ **Complete** - FastAPI service with FAISS indexing and search
- **Secure File Storage**: ✅ **Complete** - Upload and manage files with user authentication via Appwrite
- **AI-Powered Indexing**: ✅ **Complete** - Automatic document processing and embedding generation (FastAPI + FAISS)
- **S3-Compatible Storage**: ✅ **Complete** - Files stored in Backblaze B2 or Cloudflare R2
- **Presigned Uploads**: ✅ **Complete** - Secure direct-to-S3 uploads with time-limited URLs
- **Flutter Services Layer**: ✅ **Complete** - All service classes for API integration
- **Android Photo Sync**: 📋 **Planned** - Automatic background photo synchronization (Android only)
- **Thin Client Architecture**: ✅ **Complete** - Flutter client handles only UI, all ML/AI processing server-side
- **Cost-Effective**: Only storage and Appwrite Cloud are recurring costs

## 📊 Current Status

### ✅ Completed Components

#### **Python Service (Unified Backend)** - 100% Complete
- ✅ FastAPI application with all endpoints
- ✅ FAISS IndexFlatL2 implementation
- ✅ Sentence Transformer model integration
- ✅ Thread-safe operations with Lock
- ✅ Index persistence to disk
- ✅ Health check and stats endpoints
- ✅ Complete file management API
- ✅ S3 integration with presigned URLs
- ✅ Appwrite Tables integration for metadata
- ✅ Comprehensive API documentation

#### **Flutter Services Layer** - 100% Complete
- ✅ AuthService (Appwrite authentication)
- ✅ FileService (file operations, metadata management)
- ✅ SearchService (semantic and traditional search)
- ✅ PhotoSyncService (photo sync functionality)
- ✅ Appwrite client configuration
- ✅ Service architecture with error handling

### 🔄 In Progress

#### **Flutter UI Implementation** - 0% Complete
- 📋 Authentication screens (sign up, sign in, profile)
- 📋 File management screens (upload, browse, delete)
- 📋 Search interface (semantic search UI)
- 📋 Dashboard and navigation
- 📋 Settings and configuration
- 📋 Photo sync settings (Android)

### 📋 Planned

- **Android Photo Sync**: Background photo synchronization using WorkManager
- **File Preview**: In-app file preview functionality
- **Advanced Search**: Enhanced search UI with filters

## 🏗️ Architecture

The system consists of four main components:

1. **Flutter Client (Thin)**: Cross-platform UI for Android and Desktop - handles only UI and API calls
2. **Python Service (Unified Backend)**: FastAPI service handling all operations (file management, semantic search, S3 integration)
3. **Appwrite (Authentication & Metadata)**: User authentication via SDK, metadata storage via Tables API
4. **S3-Compatible Storage (B2/R2)**: File persistence layer

**Key Architecture Principles:**
- **Thin Client**: Flutter client has NO ML/AI processing
- **Unified Backend**: All business logic in Python service (no Appwrite Functions)
- **Service Boundaries**: Client → Python Service → Appwrite Tables / S3 (direct communication)
- **Security**: No credentials exposed to client, presigned URLs only, API key authentication
- **Cost Optimization**: Only storage is recurring cost

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🛠️ Technology Stack

### Frontend
- **Flutter**: Cross-platform framework (Android, Desktop)
- **Dart**: Programming language
- **Appwrite SDK**: Authentication integration
- **Workmanager**: Background tasks (Android only)
- **image_picker**: File and image selection

### Backend
- **Appwrite Cloud**: Authentication (via SDK) and metadata storage (Tables API)
- **Python 3.9+**: Unified backend service (all operations)
- **FastAPI**: Web framework for Python service
- **Appwrite Python SDK**: Tables API integration
- **Boto3**: S3 operations (presigned URLs, file management)

### AI/ML (Server-Side Only)
- **Sentence Transformers**: Document embedding generation
- **FAISS IndexFlatL2**: Vector similarity search
- **all-MiniLM-L6-v2**: Pre-trained language model (384 dimensions)
- **Thread-Safe Operations**: Lock for concurrent index updates

### Storage
- **S3-Compatible**: Backblaze B2 or Cloudflare R2
- **Appwrite Database**: File metadata storage
- **FAISS Index**: Disk-based index persistence

## 📦 Installation

### Prerequisites
- Flutter SDK (latest stable)
- Python 3.9+
- Docker (optional, for Python service deployment)
- Git
- Appwrite Cloud account (sign up at https://cloud.appwrite.io)
- S3-compatible storage account (Backblaze B2 or Cloudflare R2)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/const-nishant/personal-drive.git
cd personal-drive
```

2. **Install dependencies**
```bash
# Install Flutter dependencies
cd frontend/personal_drive
flutter pub get

# Install Python dependencies
cd ../../backend/semantic
pip install -r requirements.txt
```

3. **Set up Appwrite Cloud**
   - Sign up at https://cloud.appwrite.io
   - Create a new project
   - Note your Project ID and API Endpoint
   - Create a database and table for file metadata
   - Configure authentication (Email/Password or OAuth)

4. **Configure S3 Storage**
   - Create bucket in Backblaze B2 or Cloudflare R2
   - Generate access keys
   - Configure in Python service environment variables

5. **Configure Python Service**
   - Create `.env` file in `backend/semantic/`:
     ```env
     # API Key (generate with: openssl rand -hex 32)
     API_KEY=your-service-api-key
     
     # Appwrite Configuration
     APPWRITE_ENDPOINT=https://sgp.cloud.appwrite.io/v1
     APPWRITE_PROJECT_ID=your-project-id
     APPWRITE_API_KEY=your-appwrite-api-key
     APPWRITE_DATABASE_ID=your-database-id
     APPWRITE_TABLE_ID=your-table-id
     
     # S3 Configuration
     S3_ENDPOINT=your-s3-endpoint
     S3_ACCESS_KEY_ID=your-access-key
     S3_SECRET_ACCESS_KEY=your-secret-key
     S3_BUCKET_NAME=your-bucket-name
     S3_REGION=us-east-1
     
     # Optional Configuration
     MAX_FILE_SIZE=104857600
     PRESIGNED_UPLOAD_EXPIRES_IN=900
     PRESIGNED_DOWNLOAD_EXPIRES_IN=3600
     ```

6. **Configure Flutter app**
   - Update `frontend/personal_drive/lib/core/config.dart`:
     ```dart
     const String appwriteEndpoint = 'https://cloud.appwrite.io/v1';
     const String appwriteProjectId = 'your-project-id';
     const String pythonServiceUrl = 'http://localhost:8000'; // or your deployed URL
     const String pythonServiceApiKey = 'your-service-api-key'; // Same as API_KEY in .env
     ```
   - **NEVER include S3 credentials or Appwrite API keys in Flutter code**

7. **Start the services**
```bash
# Start Python service (in one terminal)
cd backend/semantic
python -m uvicorn app:app --reload

# Start Flutter app (in another terminal)
cd frontend/personal_drive
flutter run
```

## 📖 Usage

### Backend is Ready to Use

**Python Service is fully functional:**

1. **Start the Python Service**
```bash
cd backend/semantic
python -m uvicorn app:app --reload
```

2. **Test the Service**
```bash
# Health check
curl http://localhost:8000/health

# Index a document
curl -X POST http://localhost:8000/api/v1/upload/presign \
  -H "X-API-Key: your-api-key" \
  -H "X-User-Id: test-user" \
  -H "Content-Type: application/json" \
  -d '{"name": "test.pdf", "size": 1024, "mimeType": "application/pdf"}'

# Search documents
curl -X POST http://localhost:8000/api/v1/search \
  -H "X-API-Key: your-api-key" \
  -H "X-User-Id: test-user" \
  -H "Content-Type: application/json" \
  -d '{"query": "test document", "k": 5}'
```

See [backend/semantic/API.md](./backend/semantic/API.md) for detailed API documentation.

### Flutter UI Coming Soon

The Flutter UI is currently in development and will include:

1. **Authentication**: Sign up, sign in, and profile management
2. **File Management**: Upload, browse, download, and delete files
3. **Search**: Natural language semantic search interface
4. **Dashboard**: Overview of files and storage usage
5. **Settings**: Configuration for photo sync and preferences
6. **Android Photo Sync**: Automatic background photo backup

### For Developers

- **Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- **Features**: See [FEATURES.md](./FEATURES.md) for feature documentation
- **API Documentation**: See [backend/semantic/API.md](./backend/semantic/API.md) for complete API reference
- **Deployment**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions
- **Security**: See [SECURITY.md](./SECURITY.md) for security guidelines
- **Testing**: See [backend/semantic/TESTING.md](./backend/semantic/TESTING.md) for testing patterns

## 🔒 Security

Security is a top priority. The system includes:
- **Appwrite Authentication**: All user operations require authentication
- **API Key Authentication**: Python service protected with API keys
- **Presigned URLs**: Time-limited upload/download URLs (no credentials exposed)
- **Input Validation**: All inputs validated and sanitized (file names, sizes, MIME types)
- **Service Boundaries**: Client → Python Service → Appwrite/S3 (strict boundaries)
- **No Credential Exposure**: S3 credentials and API keys never exposed to Flutter client
- **Single-User System**: User-scoped data access only

**Critical Security Rules:**
- ❌ NEVER expose S3 credentials to Flutter client
- ❌ NEVER expose Appwrite API keys to Flutter client
- ✅ ALWAYS use presigned URLs for file operations
- ✅ ALWAYS validate and sanitize all inputs
- ✅ ALWAYS verify API key and user ID in Python service

For detailed security information, see [SECURITY.md](./SECURITY.md).

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Read the Rules**: See `.cursor/rules/base-rules.mdc` for architecture and coding rules
2. **Follow Architecture**: Maintain thin client principle and service boundaries
3. **Security First**: Never expose credentials, always validate inputs
4. **Code Style**: Follow Dart style guide for Flutter, PEP 8 for Python
5. **Testing**: Add tests for new features

**Current Priority: Flutter UI Development**

We're currently focused on building the Flutter UI. If you'd like to contribute:
- UI/UX design and implementation
- Screen navigation and state management
- Integration with existing services
- Widget development

**Contribution Process:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## 📞 Support

- **Documentation**: Check the `/docs` directory
- **Issues**: Report bugs or request features on GitHub Issues
- **Discussions**: Join our community discussions

## 🗺️ Roadmap

See [ROADMAP.md](./ROADMAP.md) for upcoming features and development plans.

---

## Quick Links

- [Architecture](./ARCHITECTURE.md)
- [Features](./FEATURES.md)
- [Security](./SECURITY.md)
- [Deployment](./DEPLOYMENT.md)
- [API Documentation](./backend/semantic/API.md)
- [Roadmap](./ROADMAP.md)
- [License](./LICENSE)

**Built with ❤️ by the Personal Drive Team**