import 'dart:io';
import 'package:appwrite/appwrite.dart';
import '../core/appwrite_client.dart';

class FileService {
  final Storage _storage = AppwriteClient.storage;
  final Databases _database = AppwriteClient.databases;

  static const String bucketId = 'files';
  static const String collectionId = 'files';

  // Upload file with progress tracking
  Future<Map<String, dynamic>> uploadFile({
    required File file,
    required String userId,
    String? folderId,
    String? description,
    List<String>? tags,
    Function(double)? onProgress,
  }) async {
    try {
      // Generate unique file ID
      final String fileId = ID.unique();
      final String fileName = file.path.split('/').last;
      final int fileSize = await file.length();

      // Get MIME type
      final String mimeType = _getMimeType(fileName);

      // Create pre-signed URL for upload
      final uploadResponse = await _storage.createFile(
        bucketId: bucketId,
        fileId: fileId,
        file: InputFile.fromPath(path: file.path, filename: fileName),
        onProgress: (progress) {
          if (onProgress != null) {
            onProgress(progress.progress / 100);
          }
        },
      );

      // Create file record in database
      final document = await _database.createDocument(
        collectionId: collectionId,
        documentId: fileId,
        data: {
          'name': fileName,
          'size': fileSize,
          'mimeType': mimeType,
          'fileId': fileId,
          'userId': userId,
          'folderId': folderId,
          'description': description ?? '',
          'tags': tags ?? [],
          'indexed': false,
          'vectorId': null,
          'createdAt': DateTime.now().toIso8601String(),
          'updatedAt': DateTime.now().toIso8601String(),
        },
      );

      return {
        'success': true,
        'file': document.data,
        'uploadResponse': uploadResponse,
      };
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Get file download URL
  Future<String?> getFileDownloadUrl(String fileId) async {
    try {
      final response = await _storage.getFileDownload(
        bucketId: bucketId,
        fileId: fileId,
      );
      return response.toString();
    } catch (e) {
      return null;
    }
  }

  // Get file preview URL
  Future<String?> getFilePreviewUrl({
    required String fileId,
    int? width,
    int? height,
  }) async {
    try {
      final response = await _storage.getFilePreview(
        bucketId: bucketId,
        fileId: fileId,
        width: width,
        height: height,
      );
      return response.toString();
    } catch (e) {
      return null;
    }
  }

  // Get user files with pagination
  Future<Map<String, dynamic>> getUserFiles({
    required String userId,
    String? folderId,
    int limit = 20,
    int offset = 0,
    String? sortField = 'createdAt',
    String? sortOrder = 'DESC',
  }) async {
    try {
      List<String> queries = [Query.equal('userId', userId)];

      if (folderId != null) {
        queries.add(Query.equal('folderId', folderId));
      }

      queries.addAll([
        Query.limit(limit),
        Query.offset(offset),
        Query.orderDesc(sortField!),
      ]);

      final response = await _database.listDocuments(
        collectionId: collectionId,
        queries: queries,
      );

      return {
        'success': true,
        'files': response.documents,
        'total': response.total,
      };
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Delete file
  Future<Map<String, dynamic>> deleteFile({
    required String fileId,
    required String userId,
  }) async {
    try {
      // Verify user owns the file
      final document = await _database.getDocument(
        collectionId: collectionId,
        documentId: fileId,
      );

      if (document.data['userId'] != userId) {
        throw Exception('Unauthorized to delete this file');
      }

      // Delete from storage
      await _storage.deleteFile(bucketId: bucketId, fileId: fileId);

      // Delete from database
      await _database.deleteDocument(
        collectionId: collectionId,
        documentId: fileId,
      );

      return {'success': true, 'message': 'File deleted successfully'};
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Update file metadata
  Future<Map<String, dynamic>> updateFileMetadata({
    required String fileId,
    required String userId,
    String? name,
    String? description,
    List<String>? tags,
    String? folderId,
  }) async {
    try {
      // Verify user owns the file
      final document = await _database.getDocument(
        collectionId: collectionId,
        documentId: fileId,
      );

      if (document.data['userId'] != userId) {
        throw Exception('Unauthorized to update this file');
      }

      // Prepare update data
      Map<String, dynamic> updateData = {
        'updatedAt': DateTime.now().toIso8601String(),
      };

      if (name != null) updateData['name'] = name;
      if (description != null) updateData['description'] = description;
      if (tags != null) updateData['tags'] = tags;
      if (folderId != null) updateData['folderId'] = folderId;

      // Update document
      final response = await _database.updateDocument(
        collectionId: collectionId,
        documentId: fileId,
        data: updateData,
      );

      return {'success': true, 'file': response.data};
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Get file by ID
  Future<Map<String, dynamic>> getFileById({
    required String fileId,
    required String userId,
  }) async {
    try {
      final document = await _database.getDocument(
        collectionId: collectionId,
        documentId: fileId,
      );

      if (document.data['userId'] != userId) {
        throw Exception('Unauthorized to access this file');
      }

      return {'success': true, 'file': document.data};
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Bulk delete files
  Future<Map<String, dynamic>> bulkDeleteFiles({
    required List<String> fileIds,
    required String userId,
  }) async {
    try {
      int successCount = 0;
      int failCount = 0;
      List<String> errors = [];

      for (String fileId in fileIds) {
        try {
          await deleteFile(fileId: fileId, userId: userId);
          successCount++;
        } catch (e) {
          failCount++;
          errors.add('File $fileId: ${e.toString()}');
        }
      }

      return {
        'success': true,
        'deletedCount': successCount,
        'failedCount': failCount,
        'errors': errors,
      };
    } catch (e) {
      return {'success': false, 'error': e.toString()};
    }
  }

  // Get MIME type from file extension
  String _getMimeType(String fileName) {
    final extension = fileName.split('.').last.toLowerCase();

    switch (extension) {
      case 'pdf':
        return 'application/pdf';
      case 'jpg':
      case 'jpeg':
        return 'image/jpeg';
      case 'png':
        return 'image/png';
      case 'gif':
        return 'image/gif';
      case 'txt':
        return 'text/plain';
      case 'doc':
        return 'application/msword';
      case 'docx':
        return 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
      case 'xls':
        return 'application/vnd.ms-excel';
      case 'xlsx':
        return 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
      case 'ppt':
        return 'application/vnd.ms-powerpoint';
      case 'pptx':
        return 'application/vnd.openxmlformats-officedocument.presentationml.presentation';
      case 'zip':
        return 'application/zip';
      case 'mp4':
        return 'video/mp4';
      case 'mp3':
        return 'audio/mpeg';
      default:
        return 'application/octet-stream';
    }
  }
}
