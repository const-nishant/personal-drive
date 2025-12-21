import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/appwrite_client.dart';
import '../core/config.dart';

class SearchService {
  final AppwriteClient _appwriteClient = AppwriteClient();

  /// Search files using semantic search
  Future<List<Map<String, dynamic>>> semanticSearch(String query, {int limit = 20}) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConfig.semanticSearchEndpoint}/search'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer ${await _appwriteClient.getToken()}',
        },
        body: json.encode({
          'query': query,
          'top_k': limit,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['results'] ?? []);
      } else {
        throw Exception('Search failed: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Search error: $e');
    }
  }

  /// Search files using traditional text search
  Future<List<Map<String, dynamic>>> textSearch(String query, {int limit = 20}) async {
    try {
      final databases = _appwriteClient.databases;

      final result = await databases.listDocuments(
        databaseId: AppConfig.databaseId,
        collectionId: AppConfig.filesCollectionId,
        queries: [
          'name.contains("$query")',
          'description.contains("$query")',
          'tags.contains("$query")',
        ],
        limit: limit,
      );

      return result.documents.map((doc) => doc.data).toList();
    } catch (e) {
      throw Exception('Text search error: $e');
    }
  }

  /// Search files by tags
  Future<List<Map<String, dynamic>>> searchByTags(List<String> tags, {int limit = 20}) async {
    try {
      final databases = _appwriteClient.databases;

      final result = await databases.listDocuments(
        databaseId: Config.databaseId,
        collectionId: Config.filesCollectionId,
        queries: tags.map((tag) => 'tags.contains("$tag")').toList(),
        limit: limit,
      );

      return result.documents.map((doc) => doc.data).toList();
    } catch (e) {
      throw Exception('Tag search error: $e');
    }
  }

  /// Search files by file type
  Future<List<Map<String, dynamic>>> searchByType(String mimeType, {int limit = 20}) async {
    try {
      final databases = _appwriteClient.databases;

      final result = await databases.listDocuments(
        databaseId: Config.databaseId,
        collectionId: Config.filesCollectionId,
        queries: ['mimeType.equal("$mimeType")'],
        limit: limit,
      );

      return result.documents.map((doc) => doc.data).toList();
    } catch (e) {
      throw Exception('Type search error: $e');
    }
  }

  /// Get recent files
  Future<List<Map<String, dynamic>>> getRecentFiles({int limit = 20}) async {
    try {
      final databases = _appwriteClient.databases;

      final result = await databases.listDocuments(
        databaseId: Config.databaseId,
        collectionId: Config.filesCollectionId,
        queries: ['orderDesc("_createdAt")'],
        limit: limit,
      );

      return result.documents.map((doc) => doc.data).toList();
    } catch (e) {
      throw Exception('Recent files error: $e');
    }
  }

  /// Advanced search with multiple filters
  Future<List<Map<String, dynamic>>> advancedSearch({
    String? query,
    List<String>? tags,
    String? mimeType,
    String? folderId,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 20,
  }) async {
    try {
      final databases = _appwriteClient.databases;
      final queries = <String>[];

      if (query != null && query.isNotEmpty) {
        queries.add('name.contains("$query")');
      }

      if (tags != null && tags.isNotEmpty) {
        queries.addAll(tags.map((tag) => 'tags.contains("$tag")'));
      }

      if (mimeType != null && mimeType.isNotEmpty) {
        queries.add('mimeType.equal("$mimeType")');
      }

      if (folderId != null && folderId.isNotEmpty) {
        queries.add('folderId.equal("$folderId")');
      }

      if (startDate != null) {
        queries.add('_createdAt.greaterThan("${startDate.toIso8601String()}")');
      }

      if (endDate != null) {
        queries.add('_createdAt.lessThan("${endDate.toIso8601String()}")');
      }

      final result = await databases.listDocuments(
        databaseId: Config.databaseId,
        collectionId: Config.filesCollectionId,
        queries: queries,
        limit: limit,
      );

      return result.documents.map((doc) => doc.data).toList();
    } catch (e) {
      throw Exception('Advanced search error: $e');
    }
  }
}
