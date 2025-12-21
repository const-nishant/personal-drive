
# Personal Drive - AI-Powered Document Management System

Personal Drive is a single-user, private Google-Drive-like system with semantic search and auto photo sync. Built with Flutter (thin client), Appwrite (orchestration), FastAPI (semantic search), and S3-compatible storage (B2/R2), it provides secure file storage with intelligent semantic search capabilities. The system is designed to minimize recurring costs, with only storage being a recurring expense.

## 🚀 Features

- **Semantic Search Service**: ✅ **Complete** - FastAPI service with FAISS indexing and search
- **Secure File Storage**: 📋 **Planned** - Upload and manage files with user authentication via Appwrite
- **AI-Powered Indexing**: ✅ **Complete** - Automatic document processing and embedding generation (FastAPI + FAISS)
- **S3-Compatible Storage**: 📋 **Planned** - Files stored in Backblaze B2 or Cloudflare R2
- **Presigned Uploads**: 📋 **Planned** - Secure direct-to-S3 uploads with time-limited URLs
- **Android Photo Sync**: 📋 **Planned** - Automatic background photo synchronization (Android only)
- **Thin Client Architecture**: 🔄 **In Progress** - Flutter client handles only UI, all ML/AI processing server-side
- **Cost-Effective**: Only storage and Appwrite Cloud are recurring costs

## 📊 Current Status

### ✅ Completed Components
- **Semantic Search Service (FastAPI)**
  - FastAPI application with all endpoints
  - FAISS IndexFlatL2 implementation
  - Sentence Transformer model integration
  - Thread-safe operations
  - Index persistence to disk
  - Health check and stats endpoints
  - Comprehensive testing documentation

### 🔄 In Progress
- **Appwrite Functions**: Functions for file indexing, search, and presigned URL generation
- **Flutter Client**: Basic structure and Appwrite SDK integration

### 📋 Planned
- **Appwrite Cloud Setup**: Account creation and project configuration
- **S3 Storage**: Backblaze B2 or Cloudflare R2 integration
- **Database Schema**: File metadata collection in Appwrite
- **File Management**: Upload, download, preview, delete functionality
- **Search UI**: Flutter interface for semantic search
- **Android Photo Sync**: Background photo synchronization

## 🏗️ Architecture

The system consists of four main components:

1. **Flutter Client (Thin)**: Cross-platform UI for Android and Desktop - handles only UI and API calls
2. **Appwrite (Orchestrator)**: Authentication, metadata storage, and serverless function orchestration
3. **Semantic Search Service (FastAPI)**: Python-based AI service for document indexing and search
4. **S3-Compatible Storage (B2/R2)**: File persistence layer

**Key Architecture Principles:**
- **Thin Client**: Flutter client has NO ML/AI processing
- **Service Boundaries**: Client → Appwrite → Semantic Service → Storage (strict boundaries)
- **Security**: No credentials exposed to client, presigned URLs only
- **Cost Optimization**: Only storage is recurring cost

For detailed architecture information, see [ARCHITECTURE.md](./ARCHITECTURE.md).

## 🛠️ Technology Stack

### Frontend
- **Flutter**: Cross-platform framework (Android, Desktop)
- **Dart**: Programming language
- **Appwrite SDK**: Backend integration
- **Workmanager**: Background tasks (Android only)
- **file_picker**: File selection
- **permission_handler**: Runtime permissions

### Backend
- **Appwrite**: Authentication, metadata database, and function orchestration
- **Node.js**: Appwrite Functions for coordination
- **Python 3.9+**: Semantic search service
- **FastAPI**: Web framework for semantic service (NOT Flask)

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
- Docker (optional, for Semantic Service deployment)
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
   - Configure authentication (Email/Password or OAuth)

4. **Configure S3 Storage**
   - Create bucket in Backblaze B2 or Cloudflare R2
   - Generate access keys
   - Configure in Appwrite Functions environment variables

5. **Configure Flutter app**
   - Update `frontend/personal_drive/lib/core/config.dart`:
     - Set `appwriteEndpoint` to `https://cloud.appwrite.io/v1`
     - Set `appwriteProjectId` to your Appwrite Cloud project ID
   - **NEVER include S3 credentials or API keys in Flutter code**

6. **Start the services**
```bash
# Start semantic search service
cd backend/semantic
python -m uvicorn app:app --reload

# Start Flutter app (in a new terminal)
cd frontend/personal_drive
flutter run
```

## 📖 Usage

### Current Capabilities

**Semantic Search Service is ready to use:**

1. **Start the Semantic Service**
```bash
cd backend/semantic
python -m uvicorn app:app --reload
```

2. **Test the Service**
```bash
# Health check
curl http://localhost:8000/health

# Index a document
curl -X POST http://localhost:8000/index \
  -H "Content-Type: application/json" \
  -d '{"file_id": "test123", "text": "This is a test document."}'

# Search documents
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test document", "k": 5}'
```

See [backend/semantic/TESTING.md](./backend/semantic/TESTING.md) for detailed testing instructions.

### Planned Features (Not Yet Implemented)

1. **Sign Up/Login**: Create an account or log in with existing credentials via Appwrite
2. **Upload Files**: Select files using the file picker and upload securely
3. **Search**: Use natural language to search through your documents (semantic search)
4. **Android Photo Sync**: Enable automatic photo sync in settings (Android only)
5. **Manage**: View, download, or delete files from your dashboard

### For Developers

- **Architecture**: See [ARCHITECTURE.md](./ARCHITECTURE.md) for system design
- **Features**: See [FEATURES.md](./FEATURES.md) for feature documentation
- **Deployment**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for deployment instructions
- **Security**: See [SECURITY.md](./SECURITY.md) for security guidelines
- **Testing**: See [backend/semantic/TESTING.md](./backend/semantic/TESTING.md) for testing patterns

## 🔒 Security

Security is a top priority. The system includes:
- **Appwrite Authentication**: All user operations require authentication
- **Presigned URLs**: Time-limited upload/download URLs (no credentials exposed)
- **Input Validation**: All inputs validated and sanitized (file names, sizes, MIME types)
- **Service Boundaries**: Client → Appwrite → Semantic Service (strict boundaries)
- **No Credential Exposure**: S3 credentials and API keys never exposed to Flutter client
- **Single-User System**: User-scoped data access only

**Critical Security Rules:**
- ❌ NEVER expose S3 credentials to Flutter client
- ❌ NEVER allow direct client → S3 or client → Semantic Service communication
- ✅ ALWAYS use presigned URLs for file operations
- ✅ ALWAYS validate and sanitize all inputs

For detailed security information, see [SECURITY.md](./SECURITY.md).

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Read the Rules**: See `.cursor/rules/base-rules.mdc` for architecture and coding rules
2. **Follow Architecture**: Maintain thin client principle and service boundaries
3. **Security First**: Never expose credentials, always validate inputs
4. **Code Style**: Follow Dart style guide for Flutter, PEP 8 for Python
5. **Testing**: Add tests for new features

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
- [Roadmap](./ROADMAP.md)
- [License](./LICENSE)

**Built with ❤️ by the Personal Drive Team**
