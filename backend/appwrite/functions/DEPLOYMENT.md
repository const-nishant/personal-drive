# Deploying Appwrite Functions to Appwrite Cloud

This guide walks you through deploying all Appwrite Functions to Appwrite Cloud.

## Prerequisites

1. **Appwrite Cloud Account**
   - Sign up at https://cloud.appwrite.io
   - Create a new project (or use existing)
   - Note your Project ID and API Endpoint

2. **Appwrite CLI** (Recommended)
   ```bash
   npm install -g appwrite-cli
   ```

3. **Node.js 18+** (for installing dependencies locally)

---

## Step 1: Install Dependencies

Install dependencies for each function:

```bash
# Navigate to functions directory
cd backend/appwrite/functions

# Install dependencies for each function
cd presignUpload && npm install && cd ..
cd indexFile && npm install && cd ..
cd search && npm install && cd ..
cd presignDownload && npm install && cd ..
```

---

## Step 2: Login to Appwrite CLI

```bash
appwrite login
```

Follow the prompts to authenticate with your Appwrite Cloud account.

---

## Step 3: Set Your Project

```bash
appwrite client --endpoint https://cloud.appwrite.io/v1
appwrite client --project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual Appwrite Cloud project ID.

---

## Step 4: Create Functions in Appwrite Cloud

### Option A: Using Appwrite CLI (Recommended)

#### 4.1 Create presignUpload Function

```bash
cd backend/appwrite/functions/presignUpload

appwrite functions create \
  --function-id=presignUpload \
  --name="Presign Upload" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="S3_ENDPOINT=your_s3_endpoint,S3_ACCESS_KEY_ID=your_key,S3_SECRET_ACCESS_KEY=your_secret,S3_BUCKET_NAME=your_bucket,S3_REGION=your_region"
```

#### 4.2 Create indexFile Function

```bash
cd ../indexFile

appwrite functions create \
  --function-id=indexFile \
  --name="Index File" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="SEMANTIC_SERVICE_URL=your_semantic_service_url,SEMANTIC_SERVICE_API_KEY=your_api_key"
```

#### 4.3 Create search Function

```bash
cd ../search

appwrite functions create \
  --function-id=search \
  --name="Search" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="SEMANTIC_SERVICE_URL=your_semantic_service_url,SEMANTIC_SERVICE_API_KEY=your_api_key"
```

#### 4.4 Create presignDownload Function

```bash
cd ../presignDownload

appwrite functions create \
  --function-id=presignDownload \
  --name="Presign Download" \
  --runtime=node-18.0 \
  --execute="users" \
  --vars="S3_ENDPOINT=your_s3_endpoint,S3_ACCESS_KEY_ID=your_key,S3_SECRET_ACCESS_KEY=your_secret,S3_BUCKET_NAME=your_bucket,S3_REGION=your_region"
```

### Option B: Using Appwrite Console (Web UI)

1. Go to https://cloud.appwrite.io
2. Select your project
3. Navigate to **Functions** in the left sidebar
4. Click **Create Function**
5. Fill in the details:
   - **Function ID**: `presignUpload` (or `indexFile`, `search`, `presignDownload`)
   - **Name**: "Presign Upload" (or appropriate name)
   - **Runtime**: Node.js 18.0
   - **Execute**: Users
6. Click **Create**
7. Repeat for each function

---

## Step 5: Deploy Functions

### Using Appwrite CLI

For each function, deploy it:

```bash
# Deploy presignUpload
cd backend/appwrite/functions/presignUpload
appwrite functions create-deployment \
  --function-id=presignUpload \
  --entrypoint="index.js" \
  --code="." \
  --activate=true

# Deploy indexFile
cd ../indexFile
appwrite functions create-deployment \
  --function-id=indexFile \
  --entrypoint="index.js" \
  --code="." \
  --activate=true

# Deploy search
cd ../search
appwrite functions create-deployment \
  --function-id=search \
  --entrypoint="index.js" \
  --code="." \
  --activate=true

# Deploy presignDownload
cd ../presignDownload
appwrite functions create-deployment \
  --function-id=presignDownload \
  --entrypoint="index.js" \
  --code="." \
  --activate=true
```

### Using Appwrite Console

1. Go to your function in Appwrite Console
2. Click **Deployments** tab
3. Click **Create Deployment**
4. Upload the function directory (including `node_modules` and `package.json`)
5. Set **Entrypoint** to `index.js`
6. Click **Deploy**

**Note:** Make sure to include `node_modules` folder when deploying. Appwrite will bundle everything.

---

## Step 6: Configure Environment Variables

### Using Appwrite Console (Recommended)

For each function, set environment variables:

1. Go to your function in Appwrite Console
2. Click **Settings** tab
3. Scroll to **Environment Variables**
4. Add each variable:

#### For presignUpload and presignDownload:

```
S3_ENDPOINT=your_s3_endpoint
S3_ACCESS_KEY_ID=your_access_key_id
S3_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=us-east-1 (optional, defaults to us-east-1)
APPWRITE_DATABASE_ID=default (optional, defaults to 'default')
FILES_COLLECTION_ID=files (optional, defaults to 'files')
MAX_FILE_SIZE=1073741824 (optional, defaults to 1GB)
ALLOWED_MIME_TYPES=application/pdf,image/jpeg,image/png,image/jpg,image/gif,text/plain,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document (optional)
```

#### For indexFile:

```
S3_ENDPOINT=your_s3_endpoint
S3_ACCESS_KEY_ID=your_access_key_id
S3_SECRET_ACCESS_KEY=your_secret_access_key
S3_BUCKET_NAME=your_bucket_name
S3_REGION=us-east-1 (optional, defaults to us-east-1)
SEMANTIC_SERVICE_URL=https://your-semantic-service-url
SEMANTIC_SERVICE_API_KEY=your_semantic_service_api_key
APPWRITE_DATABASE_ID=default (optional, defaults to 'default')
FILES_COLLECTION_ID=files (optional, defaults to 'files')
```

#### For search:

```
SEMANTIC_SERVICE_URL=https://your-semantic-service-url
SEMANTIC_SERVICE_API_KEY=your_semantic_service_api_key
APPWRITE_DATABASE_ID=default (optional, defaults to 'default')
FILES_COLLECTION_ID=files (optional, defaults to 'files')
```

### Using Appwrite CLI

```bash
# Set environment variables for presignUpload
appwrite functions update \
  --function-id=presignUpload \
  --vars="S3_ENDPOINT=your_endpoint,S3_ACCESS_KEY_ID=your_key,S3_SECRET_ACCESS_KEY=your_secret,S3_BUCKET_NAME=your_bucket"

# Set environment variables for indexFile
appwrite functions update \
  --function-id=indexFile \
  --vars="SEMANTIC_SERVICE_URL=your_url,SEMANTIC_SERVICE_API_KEY=your_key"

# Set environment variables for search
appwrite functions update \
  --function-id=search \
  --vars="SEMANTIC_SERVICE_URL=your_url,SEMANTIC_SERVICE_API_KEY=your_key"

# Set environment variables for presignDownload
appwrite functions update \
  --function-id=presignDownload \
  --vars="S3_ENDPOINT=your_endpoint,S3_ACCESS_KEY_ID=your_key,S3_SECRET_ACCESS_KEY=your_secret,S3_BUCKET_NAME=your_bucket"
```

---

## Step 7: Create Database and Collection

Before using the functions, you need to create the database and collection:

### Using Appwrite Console

1. Go to **Databases** in Appwrite Console
2. Create a new database (or use existing)
3. Note the Database ID
4. Create a collection with ID `files`
5. Import the schema from `backend/appwrite/collections/files.schema.json`:
   - Go to your collection
   - Click **Settings** tab
   - Click **Import Attributes**
   - Paste the attributes from `files.schema.json`

### Using Appwrite CLI

```bash
# Create database
appwrite databases create \
  --databaseId=default \
  --name="Personal Drive"

# Create collection (you'll need to import attributes manually via console)
appwrite databases createCollection \
  --databaseId=default \
  --collectionId=files \
  --name="Files"
```

Then import attributes from `files.schema.json` via the console.

---

## Step 8: Test Functions

### Test presignUpload

```bash
curl -X POST https://cloud.appwrite.io/v1/functions/presignUpload/executions \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: YOUR_PROJECT_ID" \
  -H "X-Appwrite-Key: YOUR_API_KEY" \
  -d '{
    "data": "{\"name\":\"test.pdf\",\"size\":1024,\"mimeType\":\"application/pdf\",\"userId\":\"user_id\"}"
  }'
```

### Test search

```bash
curl -X POST https://cloud.appwrite.io/v1/functions/search/executions \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: YOUR_PROJECT_ID" \
  -H "X-Appwrite-Key: YOUR_API_KEY" \
  -d '{
    "data": "{\"query\":\"test search\",\"k\":5}"
  }'
```

---

## Troubleshooting

### Function Deployment Fails

1. **Check dependencies**: Make sure `node_modules` is included
2. **Check entrypoint**: Should be `index.js`
3. **Check runtime**: Should be Node.js 18.0 or later
4. **Check file size**: Appwrite has limits on function size

### Function Execution Fails

1. **Check environment variables**: All required variables must be set
2. **Check logs**: Go to function → **Logs** tab in Appwrite Console
3. **Check permissions**: Function must have `execute: users` permission
4. **Check authentication**: User must be authenticated when calling function

### Common Issues

- **"Module not found"**: Dependencies not installed or not included in deployment
- **"Environment variable not set"**: Check function settings for environment variables
- **"Unauthorized"**: Check user authentication and function execute permissions
- **"Database not found"**: Create database and collection first

---

## Quick Deployment Script

Create a `deploy.sh` script:

```bash
#!/bin/bash

PROJECT_ID="your_project_id"
API_KEY="your_api_key"

# Login (one-time)
# appwrite login

# Set project
appwrite client --endpoint https://cloud.appwrite.io/v1
appwrite client --project $PROJECT_ID

# Deploy all functions
cd backend/appwrite/functions

for func in presignUpload indexFile search presignDownload; do
  echo "Deploying $func..."
  cd $func
  appwrite functions create-deployment \
    --function-id=$func \
    --entrypoint="index.js" \
    --code="." \
    --activate=true
  cd ..
done

echo "Deployment complete!"
```

Make it executable:
```bash
chmod +x deploy.sh
./deploy.sh
```

---

## Next Steps

1. ✅ Functions deployed
2. ✅ Environment variables configured
3. ✅ Database and collection created
4. ✅ Test functions
5. ✅ Integrate with Flutter client

For Flutter integration, see the main README.md in the project root.

