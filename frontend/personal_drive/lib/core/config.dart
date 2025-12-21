import 'dart:math';

import 'package:flutter/foundation.dart';

class AppConfig {
  // Appwrite Configuration
  static const String appwriteEndpoint = String.fromEnvironment(
    'APPWRITE_ENDPOINT',
    defaultValue: 'https://cloud.appwrite.io/v1',
  );

  static const String appwriteProjectId = String.fromEnvironment(
    'APPWRITE_PROJECT_ID',
    defaultValue: '',
  );

  // API Configuration
  static const String apiEndpoint = String.fromEnvironment(
    'API_ENDPOINT',
    defaultValue: 'http://localhost:3001',
  );

  static const String semanticSearchEndpoint = String.fromEnvironment(
    'SEMANTIC_SEARCH_ENDPOINT',
    defaultValue: 'http://localhost:5001',
  );

  // File Upload Configuration
  static const int maxFileSize = 100 * 1024 * 1024; // 100MB
  static const List<String> allowedFileTypes = [
    'pdf',
    'doc',
    'docx',
    'txt',
    'jpg',
    'jpeg',
    'png',
    'gif',
    'mp4',
    'mov',
    'mp3',
    'wav',
  ];

  // Search Configuration
  static const int searchDebounceDuration = 500; // milliseconds
  static const int maxSearchResults = 50;

  // UI Configuration
  static const int itemsPerPage = 20;
  static const int gridCrossAxisCount = 2;
  static const double gridChildAspectRatio = 1.0;

  // PhotoSync Configuration
  static const int photoSyncBatchSize = 10;
  static const Duration photoSyncInterval = Duration(minutes: 30);

  // App Information
  static const String appName = 'Personal Drive';
  static const String appVersion = '1.0.0';
  static const String appDescription = 'AI-Powered Document Management System';

  // Development Settings
  static const bool debugMode = kDebugMode;
  static const bool enableLogging = kDebugMode;
  static const bool enableAnalytics = !kDebugMode;

  // Security
  static const bool enableEncryption = true;
  static const String encryptionAlgorithm = 'AES-256-GCM';

  // Validation Methods
  static bool isValidFileType(String fileName) {
    final extension = fileName.split('.').last.toLowerCase();
    return allowedFileTypes.contains(extension);
  }

  static bool isValidFileSize(int fileSize) {
    return fileSize <= maxFileSize;
  }

  static String formatFileSize(int bytes) {
    if (bytes <= 0) return '0 B';
    const suffixes = ['B', 'KB', 'MB', 'GB', 'TB'];
    var i = (log(bytes) / log(1024)).floor();
    return '${(bytes / pow(1024, i)).toStringAsFixed(1)} ${suffixes[i]}';
  }

  static Map<String, dynamic> toMap() {
    return {
      'appwriteEndpoint': appwriteEndpoint,
      'appwriteProjectId': appwriteProjectId,
      'apiEndpoint': apiEndpoint,
      'semanticSearchEndpoint': semanticSearchEndpoint,
      'maxFileSize': maxFileSize,
      'allowedFileTypes': allowedFileTypes,
      'searchDebounceDuration': searchDebounceDuration,
      'maxSearchResults': maxSearchResults,
      'itemsPerPage': itemsPerPage,
      'appName': appName,
      'appVersion': appVersion,
      'debugMode': debugMode,
      'enableLogging': enableLogging,
    };
  }

  @override
  String toString() {
    return 'AppConfig${toMap()}';
  }
}
