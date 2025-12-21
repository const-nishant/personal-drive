import 'dart:io';
import 'package:appwrite/appwrite.dart';
import 'package:image_picker/image_picker.dart';
import '../core/appwrite_client.dart';

class PhotoSyncService {
  final Storage _storage;
  final String _bucketId;

  PhotoSyncService() : _storage = AppwriteClient.storage, _bucketId = 'photos';

  /// Upload a single photo
  Future<String> uploadPhoto(XFile photo) async {
    try {
      final file = InputFile.fromPath(
        path: photo.path,
        filename: _generateFileName(photo.name),
      );

      final response = await _storage.createFile(
        bucketId: _bucketId,
        fileId: ID.unique(),
        file: file,
      );

      return response.$id;
    } catch (e) {
      throw Exception('Failed to upload photo: $e');
    }
  }

  /// Upload multiple photos
  Future<List<String>> uploadPhotos(List<XFile> photos) async {
    final uploadedIds = <String>[];

    for (final photo in photos) {
      try {
        final fileId = await uploadPhoto(photo);
        uploadedIds.add(fileId);
      } catch (e) {
        print('Failed to upload ${photo.name}: $e');
      }
    }

    return uploadedIds;
  }

  /// Get photo download URL
  Future<String> getPhotoUrl(String fileId) async {
    try {
      final response = await _storage.getFileDownload(
        bucketId: _bucketId,
        fileId: fileId,
      );
      return response.toString();
    } catch (e) {
      throw Exception('Failed to get photo URL: $e');
    }
  }

  /// Get photo preview URL
  Future<String> getPhotoPreview(
    String fileId, {
    int width = 300,
    int height = 300,
  }) async {
    try {
      final response = await _storage.getFilePreview(
        bucketId: _bucketId,
        fileId: fileId,
        width: width,
        height: height,
      );
      return response.toString();
    } catch (e) {
      throw Exception('Failed to get photo preview: $e');
    }
  }

  /// Delete a photo
  Future<void> deletePhoto(String fileId) async {
    try {
      await _storage.deleteFile(bucketId: _bucketId, fileId: fileId);
    } catch (e) {
      throw Exception('Failed to delete photo: $e');
    }
  }

  /// Get list of all photos
  Future<List<dynamic>> getAllPhotos() async {
    try {
      final response = await _storage.listFiles(bucketId: _bucketId);
      return response.files;
    } catch (e) {
      throw Exception('Failed to get photos: $e');
    }
  }

  /// Get photos by date range
  Future<List<dynamic>> getPhotosByDateRange(
    DateTime startDate,
    DateTime endDate,
  ) async {
    try {
      final allPhotos = await getAllPhotos();

      return allPhotos.where((file) {
        final fileDate = DateTime.parse(file.$createdAt);
        return fileDate.isAfter(startDate) && fileDate.isBefore(endDate);
      }).toList();
    } catch (e) {
      throw Exception('Failed to get photos by date range: $e');
    }
  }

  /// Auto-sync photos from device gallery
  Future<List<String>> autoSyncFromGallery() async {
    try {
      final picker = ImagePicker();
      final List<XFile>? images = await picker.pickMultiImage(
        maxWidth: 1920,
        maxHeight: 1080,
        imageQuality: 85,
      );

      if (images == null || images.isEmpty) {
        return [];
      }

      return await uploadPhotos(images);
    } catch (e) {
      throw Exception('Failed to sync from gallery: $e');
    }
  }

  /// Get storage usage statistics
  Future<Map<String, dynamic>> getStorageStats() async {
    try {
      final files = await getAllPhotos();

      int totalSize = 0;
      for (final file in files) {
        totalSize += file.size;
      }

      return {
        'totalFiles': files.length,
        'totalSize': totalSize,
        'totalSizeMB': (totalSize / (1024 * 1024)).toStringAsFixed(2),
      };
    } catch (e) {
      throw Exception('Failed to get storage stats: $e');
    }
  }

  /// Generate unique file name
  String _generateFileName(String originalName) {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final extension = originalName.split('.').last;
    return 'photo_$timestamp.$extension';
  }
}
