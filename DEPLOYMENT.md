# Deployment Guide

This document provides comprehensive instructions for deploying the Personal Drive application across different environments.

## Current Deployment Status

### ✅ Ready to Deploy
- **Semantic Search Service**: Fully implemented and ready for deployment
  - FastAPI application with all endpoints
  - FAISS index with disk persistence
  - Can be deployed standalone or via Docker

### 📋 Not Yet Ready
- **Appwrite Functions**: Code exists but needs deployment configuration
- **Flutter Client**: Basic structure exists, full implementation pending
- **S3 Storage Integration**: Configuration pending
- **Database Schema**: Setup pending

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Configuration](#configuration)
- [Monitoring](#monitoring)
- [Troubleshooting](#troubleshooting)

## Prerequisites

Before deploying, ensure you have the following installed:

- **Flutter SDK** (latest stable)
- **Python** (v3.9 or higher)
- **Docker** (for Semantic Service deployment, optional)
- **Git**
- **Appwrite Cloud Account** (sign up at https://cloud.appwrite.io)
- **S3-compatible storage account** (Backblaze B2 or Cloudflare R2)

### System Requirements

- **Minimum RAM**: 4GB
- **Recommended RAM**: 8GB+
- **Storage**: 10GB+ free space (for Semantic Service indices)
- **Operating System**: Linux, macOS, or Windows with WSL2
- **S3 Storage**: Backblaze B2 or Cloudflare R2 bucket configured
- **Appwrite Cloud**: Free tier available, paid plans for production

## Environment Setup

### 1. Clone the Repository

```bash
git clone https://github.com/const-nishant/personal-drive.git
cd personal-drive
```

### 2. Install Dependencies

#### Frontend Dependencies (Flutter)
```bash
cd frontend/personal_drive
flutter pub get
```

#### Backend Dependencies (Semantic Service)
```bash
cd backend/semantic
pip install -r requirements.txt
```

### 3. Environment Variables

#### Appwrite Environment Variables

Create environment variables in Appwrite Functions:

```env
# S3 Storage Configuration (NEVER expose to Flutter client)
S3_ENDPOINT=your_s3_endpoint
S3_ACCESS_KEY_ID=your_access_key
S3_SECRET_ACCESS_KEY=your_secret_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=your_region

# Semantic Service Configuration
# For Hugging Face Spaces, use your Space URL (e.g., https://username-space-name.hf.space)
SEMANTIC_SERVICE_URL=https://<your-rep>.hf.space
SEMANTIC_SERVICE_API_KEY=your_api_key  # Optional, if you add authentication

# File Limits
MAX_FILE_SIZE=104857600  # 100MB in bytes
ALLOWED_MIME_TYPES=application/pdf,image/jpeg,image/png,text/plain
```

#### Semantic Service Environment Variables

Create a `.env` file in `backend/semantic/`:

```env
# Index Configuration
INDEX_DIR=./index
MODEL_NAME=all-MiniLM-L6-v2
EMBEDDING_DIM=384

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Logging
LOG_LEVEL=INFO
```

#### Flutter Configuration

Update `frontend/personal_drive/lib/core/config.dart`:

```dart
class AppConfig {
  // Appwrite Cloud endpoint (e.g., https://cloud.appwrite.io/v1)
  static const String appwriteEndpoint = 'https://cloud.appwrite.io/v1';
  // Your Appwrite Cloud Project ID
  static const String appwriteProjectId = 'YOUR_PROJECT_ID';
  // NEVER include API keys or S3 credentials here
}
```

#### Appwrite Cloud Configuration

In Appwrite Cloud Console, configure:

1. **Project Settings**
   - Project ID (use in Flutter config)
   - API Endpoint (use in Flutter config)

2. **Functions Environment Variables**
   - Set in each function's settings:
     - `S3_ENDPOINT`
     - `S3_ACCESS_KEY_ID`
     - `S3_SECRET_ACCESS_KEY`
     - `S3_BUCKET_NAME`
     - `SEMANTIC_SERVICE_URL` (public URL of your semantic service)
       - **Hugging Face Spaces**: `https://{username}-{space-name}.hf.space`
       - **Self-hosted**: `http://your-server-ip:7860` or your domain
     - `SEMANTIC_SERVICE_API_KEY` (optional, if using API key authentication)

## Local Development

### Currently Available: Semantic Search Service

The Semantic Search Service is the only component currently ready for deployment:

#### Start Semantic Search Service
```bash
cd backend/semantic
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The service will be available at `http://localhost:8000` with:
- Health check: `GET http://localhost:8000/health`
- Stats: `GET http://localhost:8000/stats`
- Index document: `POST http://localhost:8000/index`
- Search: `POST http://localhost:8000/search`

See [backend/semantic/TESTING.md](./backend/semantic/TESTING.md) for testing instructions.

### Option 1: Docker Deployment (Semantic Service)

```bash
# Build Docker image
cd backend/semantic
docker build -t semantic-service .

# Run container
docker run -p 8000:8000 -v $(pwd)/index:/app/index semantic-service
```

### Option 2: Manual Setup (Semantic Service)

```bash
cd backend/semantic
pip install -r requirements.txt
python -m uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Planned Components (Not Yet Available)

#### Appwrite Cloud Setup (Planned)
1. Sign up at https://cloud.appwrite.io
2. Create a new project
3. Configure database collections
4. Deploy functions via Appwrite Console or CLI
5. Set environment variables in function settings

#### Flutter App (Planned)
```bash
cd frontend/personal_drive
flutter run
# For Android: flutter run -d android
# For Desktop: flutter run -d windows/linux/macos
```

## Production Deployment

### 1. Set Up S3-Compatible Storage

#### Backblaze B2 Setup
1. Create a B2 bucket
2. Generate Application Key with read/write permissions
3. Note endpoint URL (e.g., `s3.us-west-000.backblazeb2.com`)
4. Configure bucket as private

#### Cloudflare R2 Setup
1. Create an R2 bucket
2. Generate API token with read/write permissions
3. Note endpoint URL (e.g., `https://<account-id>.r2.cloudflarestorage.com`)
4. Configure bucket as private

### 2. Set Up Appwrite Cloud

1. **Create Appwrite Cloud Account**
   - Sign up at https://cloud.appwrite.io
   - Create a new project
   - Note your Project ID and API Endpoint

2. **Configure Appwrite Project**
   - Set up database collections (use `backend/appwrite/collections/files.schema.json`)
   - Configure authentication (Email/Password or OAuth)
   - Set up storage buckets (if using Appwrite Storage as temporary)

3. **Deploy Appwrite Functions**
   - Deploy `indexFile` function from `backend/appwrite/functions/indexFile/`
   - Deploy `search` function from `backend/appwrite/functions/search/`
   - Deploy `presignUpload` function from `backend/appwrite/functions/presignUpload/`
   - Configure environment variables in each function (see Configuration section)

4. **Get API Keys**
   - Generate API keys in Appwrite Console
   - Use Server API keys (not Client SDK keys) for Functions

### 3. Deploy Semantic Search Service

#### Option A: Hugging Face Spaces (Recommended)

1. **Create a Hugging Face Space**
   - Go to https://huggingface.co/spaces
   - Click "Create new Space"
   - Name: `personal-drive-semantic-service`
   - SDK: **Docker**
   - Visibility: Public or Private
   - Click "Create Space"

2. **Push your code to the Space**
   - Connect your GitHub repo or upload files directly
   - Ensure `Dockerfile` and `README.md` are in the root
   - Hugging Face will automatically build and deploy

3. **Find your Service Endpoint URL**
   - Once deployed, go to your Space page
   - The endpoint URL format is: `https://{username}-{space-name}.hf.space`
   - Example: `https://const-nishant-personal-drive-semantic-service.hf.space`
   - Or check the Space settings → "API" section for the exact URL

4. **Test the Service**
   ```bash
   # Replace with your actual Hugging Face Space URL
   curl https://const-nishant-personal-drive-semantic-service.hf.space/health
   ```

5. **Use in Appwrite Functions**
   - Set `SEMANTIC_SERVICE_URL` environment variable to your Hugging Face Space URL
   - Example: `SEMANTIC_SERVICE_URL=https://const-nishant-personal-drive-semantic-service.hf.space`

#### Option B: Self-Hosted Docker

```bash
cd backend/semantic
docker build -t semantic-service .
docker run -d \
  --name semantic-service \
  -p 7860:7860 \
  -v $(pwd)/index:/data/index \
  semantic-service
```

### 4. Build Flutter Application

```bash
# Build Android APK
cd frontend/personal_drive
flutter build apk --release

# Build Desktop (Windows)
flutter build windows --release

# Build Desktop (Linux)
flutter build linux --release

# Build Desktop (macOS)
flutter build macos --release
```

### 5. Configure Appwrite Functions

#### Deploy indexFile Function
```bash
cd backend/appwrite/functions/indexFile
# Upload via Appwrite Console or CLI
appwrite functions create \
  --functionId=indexFile \
  --name="Index File" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="SEMANTIC_SERVICE_URL=http://semantic-service:8000"
```

#### Deploy search Function
```bash
cd backend/appwrite/functions/search
appwrite functions create \
  --functionId=search \
  --name="Search" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="SEMANTIC_SERVICE_URL=http://semantic-service:8000"
```

#### Deploy presignUpload Function
```bash
cd backend/appwrite/functions/presignUpload
appwrite functions create \
  --functionId=presignUpload \
  --name="Presign Upload" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="S3_ENDPOINT=your_endpoint,S3_ACCESS_KEY_ID=your_key,S3_SECRET_ACCESS_KEY=your_secret,S3_BUCKET_NAME=your_bucket"
```

**IMPORTANT:** Set environment variables in Appwrite Functions console, NEVER in Flutter client code.

## Docker Deployment

### Docker Compose Configuration

Create a `docker-compose.prod.yml` file:

```yaml
version: '3.8'

services:
  appwrite:
    image: appwrite/appwrite:latest
    volumes:
      - appwrite-storage:/storage
      - appwrite-uploads:/uploads
      - appwrite-cache:/cache
      - appwrite-config:/config
      - appwrite-certificates:/ certificates
    ports:
      - "80:80"
      - "443:443"
    environment:
      - _APP_ENV=production

  semantic-service:
    build: ./backend/semantic
    ports:
      - "8000:8000"
    volumes:
      - ./backend/semantic/index:/app/index
    environment:
      - INDEX_DIR=/app/index
      - MODEL_NAME=all-MiniLM-L6-v2
      - LOG_LEVEL=INFO
    restart: unless-stopped

volumes:
  appwrite-storage:
  appwrite-uploads:
  appwrite-cache:
  appwrite-config:
  appwrite-certificates:
```

### Deploy with Docker Compose

```bash
# Production deployment
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f semantic-service
```

## Configuration

### Nginx Configuration (Optional - for reverse proxy)

Create `nginx.conf`:

```nginx
events {
    worker_connections 1024;
}

http {
    upstream appwrite {
        server appwrite:80;
    }

    upstream semantic-service {
        server semantic-service:8000;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Appwrite endpoints
        location / {
            proxy_pass http://appwrite;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Semantic service (internal only, not exposed to clients)
        location /semantic {
            proxy_pass http://semantic-service;
            proxy_set_header Host $host;
            # Add authentication header here
            proxy_set_header X-API-Key $semantic_api_key;
        }
    }
}
```

**Note:** Semantic service should NOT be directly exposed to clients. It should only be accessible via Appwrite Functions.

### SSL/TLS Configuration

```bash
# Generate SSL certificates with Let's Encrypt
sudo certbot --nginx -d yourdomain.com

# Or use self-signed certificates for testing
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout ./ssl/private.key -out ./ssl/certificate.crt
```

## Monitoring

### Health Checks

```bash
# Check Semantic Service status
curl http://localhost:8000/health

# Check Semantic Service stats
curl http://localhost:8000/stats

# Check Appwrite status
curl -H "X-Appwrite-Project: $APPWRITE_PROJECT_ID" $APPWRITE_ENDPOINT/health
```

### Log Management

```bash
# View Docker logs
docker-compose logs -f

# Set up centralized logging with ELK Stack
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 elasticsearch:7.15.0
docker run -d --name logstash --link elasticsearch:elasticsearch logstash:7.15.0
docker run -d --name kibana --link elasticsearch:elasticsearch -p 5601:5601 kibana:7.15.0
```

### Performance Monitoring

```bash
# Monitor resource usage
docker stats

# Set up Prometheus and Grafana
docker run -d --name prometheus -p 9090:9090 prom/prometheus
docker run -d --name grafana -p 3000:3000 grafana/grafana
```

## Troubleshooting

### Common Issues

#### 1. Port Conflicts

```bash
# Check which process is using a port
sudo lsof -i :3000
sudo netstat -tulpn | grep :3000

# Kill process
sudo kill -9 <PID>
```

#### 2. Docker Issues

```bash
# Restart Docker service
sudo systemctl restart docker

# Clean up Docker resources
docker system prune -a

# Rebuild images
docker-compose build --no-cache
```

#### 3. Appwrite Cloud Connection Issues

```bash
# Check Appwrite Cloud endpoint
curl https://cloud.appwrite.io/v1/health

# Verify API key permissions (use Server API key)
curl -H "X-Appwrite-Key: $APPWRITE_API_KEY" \
     -H "X-Appwrite-Project: $APPWRITE_PROJECT_ID" \
     https://cloud.appwrite.io/v1/account

# Check Flutter Appwrite client configuration
# Verify appwriteEndpoint (should be https://cloud.appwrite.io/v1)
# Verify appwriteProjectId matches your Appwrite Cloud project
```

#### 4. Semantic Service Connection Issues

**For Hugging Face Spaces:**
```bash
# Find your Space URL:
# 1. Go to https://huggingface.co/spaces/{your-username}/{your-space-name}
# 2. The endpoint URL is displayed in the Space page or Settings
# 3. Format: https://{username}-{space-name}.hf.space

# Test semantic service connection
curl https://const-nishant-personal-drive-semantic-service.hf.space/health

# Test root endpoint
curl https://const-nishant-personal-drive-semantic-service.hf.space/

# Test search endpoint
curl -X POST https://const-nishant-personal-drive-semantic-service.hf.space/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "k": 5}'
```

**For Self-Hosted Docker:**
```bash
# Test semantic service connection
curl http://localhost:7860/health

# Check semantic service logs
docker logs semantic-service

# Verify FAISS index exists
ls -la backend/semantic/index/

# Check if index is corrupted
python -c "import faiss; faiss.read_index('backend/semantic/index/faiss.index')"
```

#### 5. S3 Storage Connection Issues

```bash
# Test S3 connection (using AWS CLI or boto3)
aws s3 ls s3://your-bucket-name/ --endpoint-url=https://your-endpoint

# Verify presigned URL generation in Appwrite Functions
# Check function logs in Appwrite console
```

### Debug Mode

Enable debug logging:

```env
LOG_LEVEL=debug
NODE_ENV=development
```

### Support

For deployment issues:

1. Check the [GitHub Issues](https://github.com/const-nishant/personal-drive/issues)
2. Review the [Documentation](https://docs.yourdomain.com)
3. Contact support: support@yourdomain.com

## Backup and Recovery

### Appwrite Cloud Backup

Appwrite Cloud provides automatic backups:
- **Database**: Automatic backups managed by Appwrite Cloud
- **Storage**: Managed by Appwrite Cloud (if using Appwrite Storage)
- **Functions**: Code is versioned in Appwrite Console

**Manual Backup Options:**
- Export database collections via Appwrite Console
- Download function code from Appwrite Console
- Use Appwrite CLI for programmatic backups

**Note**: For production, consider Appwrite Cloud's backup and recovery features in paid plans.

### S3 Storage Backup

```bash
# Backup S3 bucket (B2)
b2 sync your-bucket-name b2://backup-bucket-name/

# Backup S3 bucket (R2)
aws s3 sync s3://your-bucket-name s3://backup-bucket-name/ --endpoint-url=https://your-r2-endpoint

# Restore files
# Use same commands with reversed source/destination
```

### FAISS Index Backup

```bash
# Backup FAISS index
cp -r backend/semantic/index /backup/location/index-$(date +%Y%m%d)

# Restore FAISS index
cp -r /backup/location/index-YYYYMMDD backend/semantic/index
```

### Disaster Recovery

1. **Regular backups**: Daily database and weekly full system backups
2. **Multi-region deployment**: Deploy across multiple regions for high availability
3. **Automated failover**: Set up load balancers with health checks
4. **Recovery testing**: Regularly test backup restoration procedures

## Updates and Maintenance

### Rolling Updates

```bash
# Update with zero downtime
docker-compose up -d --build
docker-compose exec backend npm run migrate
```

### Version Management

```bash
# Tag releases
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# Deploy specific version
git checkout v1.0.0
docker-compose up -d
```

This deployment guide provides a comprehensive overview of deploying Personal Drive in various environments. For specific cloud provider details, refer to their official documentation.