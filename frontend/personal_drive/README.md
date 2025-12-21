# Personal Drive - Flutter Client

A Flutter-based thin client for Personal Drive, providing cross-platform file management and semantic search capabilities.

## Overview

This Flutter application serves as a **thin client** for the Personal Drive system. It handles only UI and API calls, with all ML/AI processing happening server-side. The app supports Android and Desktop platforms (Windows, Linux, macOS).

## Architecture

### Thin Client Principle

The Flutter client follows a strict thin client architecture:

- ✅ **UI Rendering**: All user interface components
- ✅ **File Picking**: File selection using `file_picker`
- ✅ **API Calls**: Communication with Appwrite via SDK
- ✅ **Authentication**: User authentication via Appwrite
- ❌ **NO ML/AI Processing**: All semantic search happens server-side
- ❌ **NO Direct S3 Access**: Uses presigned URLs only
- ❌ **NO Direct Semantic Service Access**: Goes through Appwrite Functions

### Service Boundaries

```
Flutter Client → Appwrite (via SDK) → Semantic Service → Storage
```

**NEVER** bypass Appwrite to access Semantic Service or S3 directly.

## Project Structure

```
lib/
├── core/
│   ├── appwrite_client.dart    # Appwrite client initialization
│   ├── config.dart             # Configuration (endpoint, project ID)
│   └── utils/
│       └── utils.dart          # Utility functions
├── features/
│   ├── files/                  # File management feature
│   ├── photosync/              # Android photo sync feature
│   ├── search/                 # Search feature
│   └── settings/               # Settings feature
├── services/
│   ├── auth_service.dart       # Authentication service
│   ├── file_service.dart       # File operations service
│   ├── photosync_service.dart  # Photo sync service (Android only)
│   └── search_service.dart     # Search service
├── ui/
│   ├── screens/                # Screen widgets
│   └── widgets/                # Reusable widgets
└── main.dart                   # Application entry point
```

## Prerequisites

- Flutter SDK (latest stable)
- Dart SDK (comes with Flutter)
- Android Studio / VS Code with Flutter extensions
- Appwrite Cloud account (sign up at https://cloud.appwrite.io)
- S3-compatible storage configured (Backblaze B2 or Cloudflare R2)

## Installation

1. **Install Flutter dependencies**
```bash
cd frontend/personal_drive
flutter pub get
```

2. **Configure Appwrite**
   - Update `lib/core/config.dart` with your Appwrite endpoint and project ID
   - **NEVER** include API keys or S3 credentials in this file

3. **Run the app**
```bash
# Android
flutter run -d android

# Desktop (Windows)
flutter run -d windows

# Desktop (Linux)
flutter run -d linux

# Desktop (macOS)
flutter run -d macos
```

## Configuration

### Appwrite Cloud Configuration

Edit `lib/core/config.dart`:

```dart
class AppConfig {
  // Appwrite Cloud endpoint (https://cloud.appwrite.io/v1)
  static const String appwriteEndpoint = 'https://cloud.appwrite.io/v1';
  // Your Appwrite Cloud Project ID (from Appwrite Console)
  static const String appwriteProjectId = 'YOUR_PROJECT_ID';
  // NEVER include API keys or S3 credentials here
}
```

**Getting Your Project ID:**
1. Sign in to https://cloud.appwrite.io
2. Select your project
3. Go to Settings → General
4. Copy the Project ID

### Android Configuration

For Android photo sync, ensure these permissions are in `android/app/src/main/AndroidManifest.xml`:

```xml
<uses-permission android:name="android.permission.READ_MEDIA_IMAGES" />
<uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
```

## Features

### File Management

- **Upload Files**: Select and upload files via presigned URLs
- **Download Files**: Download files via presigned URLs
- **File List**: View all files with metadata
- **File Preview**: Preview images and documents
- **File Deletion**: Delete files with metadata cleanup

### Semantic Search

- **Natural Language Search**: Search using natural language queries
- **Search Results**: Display search results with file metadata
- **Search History**: Track recent searches
- **Advanced Filters**: Filter by file type, date, size

### Android Photo Sync

- **Background Sync**: Automatic photo synchronization using Workmanager
- **Smart Filtering**: Filter images by date, size
- **Deduplication**: SHA-256 hash checking prevents duplicates
- **Battery Optimization**: Sync only on Wi-Fi and charging (configurable)
- **Permission Handling**: Runtime permission requests

## Code Style

Follow Dart style guide:

- **Variables**: `lowerCamelCase`
- **Classes**: `UpperCamelCase`
- **Files**: `lowercase_with_underscores`
- **Constants**: `lowerCamelCase` (or `UPPER_SNAKE_CASE` for true constants)
- **Maximum line length**: 80 characters
- **Prefer `const` constructors** where possible
- **Use `final`** for variables that don't change
- **Use `async/await`** instead of `Future.then()`

## Security Rules

### Critical Security Rules

1. **NEVER expose S3 credentials or API keys to Flutter client**
   - All secrets must be server-side only
   - Use Appwrite Functions to generate presigned URLs

2. **ALWAYS validate inputs**
   - File names must be sanitized
   - File sizes must be validated (max 100MB)
   - Search queries must be length-limited (max 500 chars)

3. **ALWAYS use presigned URLs**
   - Never access S3 directly
   - Presigned URLs are time-limited (15 min upload, 1 hour download)

4. **ALWAYS go through Appwrite Functions**
   - Never access Semantic Service directly
   - All search queries go through Appwrite Functions

## Testing

### Unit Tests

```bash
flutter test
```

### Widget Tests

```bash
flutter test test/widget_test.dart
```

### Integration Tests

```bash
flutter test integration_test/
```

## Building for Production

### Android APK

```bash
flutter build apk --release
```

### Android App Bundle

```bash
flutter build appbundle --release
```

### Desktop (Windows)

```bash
flutter build windows --release
```

### Desktop (Linux)

```bash
flutter build linux --release
```

### Desktop (macOS)

```bash
flutter build macos --release
```

## Android Photo Sync Setup

### Workmanager Configuration

The photo sync uses Workmanager for background tasks:

```dart
// Register periodic task
Workmanager().registerPeriodicTask(
  "photoSync",
  "photoSyncTask",
  frequency: Duration(hours: 6),
  constraints: Constraints(
    networkType: NetworkType.unmetered,
    requiresCharging: true,
  ),
);
```

### Permissions

Request permissions at runtime:

```dart
// Request photo access permission
await Permission.photos.request();
```

### Background Task

The background task:
1. Scans DCIM/Pictures directories
2. Filters images (by date, size)
3. Computes SHA-256 hash
4. Checks Appwrite DB for existing hash
5. Uploads new photos via presigned URL
6. Saves metadata in Appwrite
7. Triggers indexing via Appwrite Function

## Troubleshooting

### Appwrite Cloud Connection Issues

- Verify `appwriteEndpoint` is set to `https://cloud.appwrite.io/v1`
- Verify `appwriteProjectId` matches your Appwrite Cloud project ID
- Check Appwrite Cloud project is active and accessible
- Verify network connectivity
- Check Appwrite Cloud status page if issues persist

### File Upload Issues

- Check presigned URL is valid (not expired)
- Verify file size is within limits (100MB)
- Check MIME type is allowed

### Search Issues

- Verify Appwrite Functions are deployed
- Check Semantic Service is running
- Verify search query is not empty and within length limit

### Android Photo Sync Issues

- Check permissions are granted
- Verify Workmanager is registered
- Check battery optimization settings
- Verify Wi-Fi and charging constraints

## Dependencies

Key dependencies:

- `appwrite`: Appwrite SDK for backend communication
- `file_picker`: File selection
- `workmanager`: Background tasks (Android)
- `permission_handler`: Runtime permissions
- `crypto`: SHA-256 hashing
- `path_provider`: File system paths

See `pubspec.yaml` for complete list.

## Contributing

When contributing to the Flutter client:

1. **Follow thin client principle**: No ML/AI processing
2. **Maintain service boundaries**: Always go through Appwrite
3. **Validate inputs**: All user inputs must be validated
4. **Handle errors gracefully**: User-friendly error messages
5. **Follow Dart style guide**: Consistent code style
6. **Add tests**: Unit and widget tests for new features

## Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Dart Style Guide](https://dart.dev/guides/language/effective-dart/style)
- [Appwrite Flutter SDK](https://appwrite.io/docs/sdks/flutter)
- [Architecture Documentation](../ARCHITECTURE.md)
- [Security Guidelines](../SECURITY.md)
