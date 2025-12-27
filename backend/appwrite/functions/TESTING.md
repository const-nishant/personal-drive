# Testing Appwrite Functions

This guide covers how to test all deployed Appwrite Functions.

## Prerequisites

1. **Appwrite Cloud Project** - Functions deployed and active
2. **Environment Variables** - All required variables set in Appwrite Console
3. **Database & Collection** - Database created with `files` collection
4. **API Key** - Appwrite API key with appropriate permissions
5. **User Authentication** - Test user account created

---

## Testing Methods

### Method 1: Appwrite Console (Easiest)

### Method 2: API Calls (curl/Postman)

### Method 3: Flutter Client (Integration Testing)

---

## Method 1: Testing via Appwrite Console

### Step 1: Get Your Project Details

1. Go to https://cloud.appwrite.io
2. Select your project
3. Note your:
   - **Project ID** (from Settings → General)
   - **API Endpoint** (e.g., `https://sgp.cloud.appwrite.io/v1`)

### Step 2: Create a Test User

1. Go to **Auth** → **Users**
2. Click **Create User**
3. Create a test user and note the **User ID**

### Step 3: Get API Key

1. Go to **Settings** → **API Keys**
2. Create a new API key with **Functions** scope
3. Copy the **API Key** (you'll need this for testing)

### Step 4: Test Functions in Console

1. Go to **Functions** → Select a function
2. Click **Test** tab
3. Enter test data
4. Click **Execute**
5. View results and logs

---

## Method 2: Testing via API Calls

### Setup

You'll need:
- **Project ID**: `694f94f00016c4a31254` (from your config)
- **API Endpoint**: `https://sgp.cloud.appwrite.io/v1` (from your config)
- **API Key**: Your Appwrite API key
- **User ID**: Test user ID

### Test 1: presignUpload Function

**Purpose:** Generate presigned URL for file upload

**Request:**
```bash
curl -X POST "https://sgp.cloud.appwrite.io/v1/functions/presignUpload/executions" \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: 694f94f00016c4a31254" \
  -H "X-Appwrite-Key: YOUR_API_KEY" \
  -d '{
    "data": "{\"name\":\"test.pdf\",\"size\":1024,\"mimeType\":\"application/pdf\",\"userId\":\"YOUR_USER_ID\"}"
  }'
```

**Expected Response:**
```json
{
  "$id": "execution_id",
  "$createdAt": "2024-01-01T00:00:00.000+00:00",
  "$updatedAt": "2024-01-01T00:00:00.000+00:00",
  "$permissions": [],
  "functionId": "presignUpload",
  "trigger": "http",
  "status": "completed",
  "statusCode": 200,
  "response": "{\"success\":true,\"fileId\":\"unique_file_id\",\"presignedUrl\":\"https://s3...\",\"expiresIn\":900,\"metadata\":{...}}",
  "stdout": "",
  "stderr": "",
  "duration": 0.5
}
```

**What to Check:**
- ✅ Status is "completed"
- ✅ Status code is 200
- ✅ Response contains `presignedUrl`
- ✅ Response contains `fileId`
- ✅ Check database for new metadata record

**PowerShell Version:**
```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-Appwrite-Project" = "694f94f00016c4a31254"
    "X-Appwrite-Key" = "YOUR_API_KEY"
}

$body = @{
    data = '{"name":"test.pdf","size":1024,"mimeType":"application/pdf","userId":"YOUR_USER_ID"}'
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://sgp.cloud.appwrite.io/v1/functions/presignUpload/executions" -Method Post -Headers $headers -Body $body
```

---

### Test 2: Upload File to S3

**Purpose:** Test the presigned URL by uploading a file

**Request:**
```bash
# First, get presignedUrl from presignUpload response
# Then upload file using presigned URL

curl -X PUT "PRESIGNED_URL_FROM_STEP_1" \
  -H "Content-Type: application/pdf" \
  --data-binary "@test.pdf"
```

**What to Check:**
- ✅ Upload succeeds (200 or 204 status)
- ✅ File appears in S3 bucket at expected path

---

### Test 3: indexFile Function

**Purpose:** Index uploaded file for semantic search

**Request:**
```bash
curl -X POST "https://sgp.cloud.appwrite.io/v1/functions/indexFile/executions" \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: 694f94f00016c4a31254" \
  -H "X-Appwrite-Key: YOUR_API_KEY" \
  -d '{
    "data": "{\"fileId\":\"FILE_ID_FROM_PRESIGN_UPLOAD\",\"userId\":\"YOUR_USER_ID\"}"
  }'
```

**Expected Response:**
```json
{
  "status": "completed",
  "statusCode": 200,
  "response": "{\"success\":true,\"message\":\"File indexed successfully\",\"fileId\":\"...\",\"hash\":\"sha256_hash\",\"indexed\":true,\"textLength\":1234}"
}
```

**What to Check:**
- ✅ Status is "completed"
- ✅ Response contains `indexed: true`
- ✅ Response contains `hash`
- ✅ Check database - `indexed` field should be `true`
- ✅ Check database - `hash` field should be populated
- ✅ Check database - `status` should be "indexed"
- ✅ Check semantic service logs (if accessible)

**PowerShell Version:**
```powershell
$body = @{
    data = '{"fileId":"FILE_ID_FROM_PRESIGN_UPLOAD","userId":"YOUR_USER_ID"}'
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://sgp.cloud.appwrite.io/v1/functions/indexFile/executions" -Method Post -Headers $headers -Body $body
```

---

### Test 4: search Function

**Purpose:** Search indexed files

**Request:**
```bash
curl -X POST "https://sgp.cloud.appwrite.io/v1/functions/search/executions" \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: 694f94f00016c4a31254" \
  -H "X-Appwrite-Key: YOUR_API_KEY" \
  -d '{
    "data": "{\"query\":\"test document\",\"k\":5,\"userId\":\"YOUR_USER_ID\"}"
  }'
```

**Expected Response:**
```json
{
  "status": "completed",
  "statusCode": 200,
  "response": "{\"success\":true,\"query\":\"test document\",\"results\":[{\"fileId\":\"...\",\"name\":\"test.pdf\",\"mimeType\":\"application/pdf\",\"size\":1024,\"storagePath\":\"...\",\"createdAt\":\"...\",\"description\":\"\",\"tags\":[],\"folderId\":null}],\"count\":1}"
}
```

**What to Check:**
- ✅ Status is "completed"
- ✅ Response contains `results` array
- ✅ Results contain file metadata
- ✅ Results match search query (semantically)
- ✅ Only user's files are returned

**PowerShell Version:**
```powershell
$body = @{
    data = '{"query":"test document","k":5,"userId":"YOUR_USER_ID"}'
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://sgp.cloud.appwrite.io/v1/functions/search/executions" -Method Post -Headers $headers -Body $body
```

---

### Test 5: presignDownload Function

**Purpose:** Generate presigned URL for file download

**Request:**
```bash
curl -X POST "https://sgp.cloud.appwrite.io/v1/functions/presignDownload/executions" \
  -H "Content-Type: application/json" \
  -H "X-Appwrite-Project: 694f94f00016c4a31254" \
  -H "X-Appwrite-Key: YOUR_API_KEY" \
  -d '{
    "data": "{\"fileId\":\"FILE_ID_FROM_PRESIGN_UPLOAD\",\"userId\":\"YOUR_USER_ID\"}"
  }'
```

**Expected Response:**
```json
{
  "status": "completed",
  "statusCode": 200,
  "response": "{\"success\":true,\"fileId\":\"...\",\"presignedUrl\":\"https://s3...\",\"expiresIn\":3600,\"metadata\":{...}}"
}
```

**What to Check:**
- ✅ Status is "completed"
- ✅ Response contains `presignedUrl`
- ✅ URL expires in 1 hour (3600 seconds)
- ✅ Download works using presigned URL

**PowerShell Version:**
```powershell
$body = @{
    data = '{"fileId":"FILE_ID_FROM_PRESIGN_UPLOAD","userId":"YOUR_USER_ID"}'
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://sgp.cloud.appwrite.io/v1/functions/presignDownload/executions" -Method Post -Headers $headers -Body $body
```

---

## Method 3: Testing via Flutter Client

### Setup Flutter Client

1. Update `lib/core/config.dart` with your Appwrite endpoint and project ID
2. Ensure user is authenticated
3. Call functions via Appwrite SDK

### Example: Test presignUpload in Flutter

```dart
import 'package:appwrite/appwrite.dart';

final functions = Functions(client);

try {
  final result = await functions.createExecution(
    functionId: 'presignUpload',
    data: jsonEncode({
      'name': 'test.pdf',
      'size': 1024,
      'mimeType': 'application/pdf',
      'userId': userId,
    }),
  );
  
  print('Result: ${result.response}');
} catch (e) {
  print('Error: $e');
}
```

---

## Complete Test Flow

### End-to-End Test

1. **Create User** (if not exists)
2. **presignUpload** → Get presigned URL + fileId
3. **Upload to S3** → Use presigned URL to upload file
4. **indexFile** → Index the uploaded file
5. **search** → Search for the file
6. **presignDownload** → Get download URL
7. **Download from S3** → Verify file download

### Test Script (PowerShell)

```powershell
# Set variables
$projectId = "694f94f00016c4a31254"
$apiKey = "YOUR_API_KEY"
$userId = "YOUR_USER_ID"
$endpoint = "https://sgp.cloud.appwrite.io/v1"

$headers = @{
    "Content-Type" = "application/json"
    "X-Appwrite-Project" = $projectId
    "X-Appwrite-Key" = $apiKey
}

# Step 1: Get presigned URL
Write-Host "Step 1: Getting presigned URL..."
$uploadBody = @{
    data = "{\"name\":\"test.pdf\",\"size\":1024,\"mimeType\":\"application/pdf\",\"userId\":\"$userId\"}"
} | ConvertTo-Json

$uploadResult = Invoke-RestMethod -Uri "$endpoint/functions/presignUpload/executions" -Method Post -Headers $headers -Body $uploadBody
$response = $uploadResult.response | ConvertFrom-Json
$fileId = $response.fileId
$presignedUrl = $response.presignedUrl

Write-Host "File ID: $fileId"
Write-Host "Presigned URL: $presignedUrl"

# Step 2: Index file (after uploading to S3)
Write-Host "`nStep 2: Indexing file..."
$indexBody = @{
    data = "{\"fileId\":\"$fileId\",\"userId\":\"$userId\"}"
} | ConvertTo-Json

$indexResult = Invoke-RestMethod -Uri "$endpoint/functions/indexFile/executions" -Method Post -Headers $headers -Body $indexBody
Write-Host "Index Result: $($indexResult.response)"

# Step 3: Search
Write-Host "`nStep 3: Searching..."
$searchBody = @{
    data = "{\"query\":\"test document\",\"k\":5,\"userId\":\"$userId\"}"
} | ConvertTo-Json

$searchResult = Invoke-RestMethod -Uri "$endpoint/functions/search/executions" -Method Post -Headers $headers -Body $searchBody
Write-Host "Search Result: $($searchResult.response)"

# Step 4: Get download URL
Write-Host "`nStep 4: Getting download URL..."
$downloadBody = @{
    data = "{\"fileId\":\"$fileId\",\"userId\":\"$userId\"}"
} | ConvertTo-Json

$downloadResult = Invoke-RestMethod -Uri "$endpoint/functions/presignDownload/executions" -Method Post -Headers $headers -Body $downloadBody
$downloadResponse = $downloadResult.response | ConvertFrom-Json
Write-Host "Download URL: $($downloadResponse.presignedUrl)"
```

---

## Troubleshooting

### Function Execution Fails

1. **Check Logs:**
   - Go to Function → **Logs** tab in Appwrite Console
   - Look for error messages

2. **Check Environment Variables:**
   - Go to Function → **Settings** → **Environment Variables**
   - Ensure all required variables are set

3. **Check Permissions:**
   - Function should have `execute: users` permission
   - API key should have Functions scope

### Common Errors

- **"User authentication required"**: User ID not provided or invalid
- **"File not found"**: FileId doesn't exist in database
- **"Semantic service URL not configured"**: Missing `SEMANTIC_SERVICE_URL` env var
- **"S3 credentials not configured"**: Missing S3 environment variables
- **"Module not found"**: Dependencies not installed (check `node_modules`)

### Debug Tips

1. **Check Function Logs** in Appwrite Console
2. **Verify Environment Variables** are set correctly
3. **Test Semantic Service** directly (if accessible)
4. **Check Database** for metadata records
5. **Verify S3 Bucket** access and permissions

---

## Next Steps

After successful testing:
1. ✅ All functions working correctly
2. ✅ Environment variables configured
3. ✅ Database schema applied
4. ✅ Integration with Flutter client
5. ✅ Production deployment ready

