import 'package:appwrite/appwrite.dart';
import 'package:flutter/foundation.dart';
import 'package:personal_drive/core/appwrite_client.dart';
import 'package:personal_drive/core/config.dart';

enum DatabaseStatus { idle, loading, success, error }

class DatabaseService extends ChangeNotifier {
  final TablesDB _tablesDB = AppwriteClient.tables;

  DatabaseStatus _status = DatabaseStatus.idle;
  String? _error;
  List<dynamic> _items = [];
  Map<String, dynamic>? _currentItem;

  DatabaseStatus get status => _status;
  String? get error => _error;
  List<dynamic> get items => _items;
  Map<String, dynamic>? get currentItem => _currentItem;
  bool get isLoading => _status == DatabaseStatus.loading;

  /// Create a new row in a table
  Future<Map<String, dynamic>?> createRow({
    required String tableId,
    required String rowId,
    required Map<String, dynamic> data,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      final row = await _tablesDB.createRow(
        rowId: rowId,
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        data: data,
      );

      _currentItem = row.data;
      _setStatus(DatabaseStatus.success);
      return row.data;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to create row';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Get a row by ID
  Future<Map<String, dynamic>?> getRow({
    required String tableId,
    required String rowId,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      final row = await _tablesDB.getRow(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        rowId: rowId,
      );

      _currentItem = row.data;
      _setStatus(DatabaseStatus.success);
      return row.data;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to get row';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// List rows from a table with optional filters
  Future<List<dynamic>> listRows({
    required String tableId,
    List<String>? queries,
    int limit = 25,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      final response = await _tablesDB.listRows(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        queries: queries ?? [],
      );

      _items = response.rows.map((row) => row.data).toList();
      _setStatus(DatabaseStatus.success);
      return _items;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to list rows';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Update a row
  Future<Map<String, dynamic>?> updateRow({
    required String tableId,
    required String rowId,
    required Map<String, dynamic> data,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      final row = await _tablesDB.updateRow(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        rowId: rowId,
        data: data,
      );

      _currentItem = row.data;
      _setStatus(DatabaseStatus.success);
      return row.data;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to update row';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Delete a row
  Future<void> deleteRow({
    required String tableId,
    required String rowId,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      await _tablesDB.deleteRow(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        rowId: rowId,
      );

      _currentItem = null;
      _setStatus(DatabaseStatus.success);
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to delete row';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Batch create rows
  Future<List<Map<String, dynamic>>> batchCreateRows({
    required String tableId,
    required List<Map<String, dynamic>> dataList,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;
    final createdRows = <Map<String, dynamic>>[];

    try {
      for (final data in dataList) {
        final row = await _tablesDB.createRow(
          rowId: ID.unique(),
          databaseId: AppConfig.databaseId,
          tableId: tableId,
          data: data,
        );
        createdRows.add(row.data);
      }

      _items = createdRows;
      _setStatus(DatabaseStatus.success);
      return createdRows;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to batch create rows';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Search rows with query filters
  Future<List<dynamic>> searchRows({
    required String tableId,
    required String searchField,
    required String searchQuery,
    List<String>? additionalQueries,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      final queries = [
        Query.search(searchField, searchQuery),
        ...?additionalQueries,
      ];

      final response = await _tablesDB.listRows(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        queries: queries,
      );

      _items = response.rows.map((row) => row.data).toList();
      _setStatus(DatabaseStatus.success);
      return _items;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Search failed';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Query rows with filters and sorting
  Future<List<dynamic>> queryRows({
    required String tableId,
    List<String>? queries,
    int? limit,
    int? offset,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      final finalQueries = <String>[...?queries];

      if (limit != null) {
        finalQueries.add(Query.limit(limit));
      }
      if (offset != null) {
        finalQueries.add(Query.offset(offset));
      }

      final response = await _tablesDB.listRows(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        queries: finalQueries,
      );

      _items = response.rows.map((row) => row.data).toList();
      _setStatus(DatabaseStatus.success);
      return _items;
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Query failed';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Update row permissions
  Future<void> updateRowPermissions({
    required String tableId,
    required String rowId,
    required List<String> permissions,
  }) async {
    _setStatus(DatabaseStatus.loading);
    _error = null;

    try {
      await _tablesDB.updateRow(
        databaseId: AppConfig.databaseId,
        tableId: tableId,
        rowId: rowId,
        permissions: permissions,
      );

      _setStatus(DatabaseStatus.success);
    } on AppwriteException catch (e) {
      _error = e.message ?? 'Failed to update permissions';
      _setStatus(DatabaseStatus.error);
      rethrow;
    } catch (e) {
      _error = e.toString();
      _setStatus(DatabaseStatus.error);
      rethrow;
    }
  }

  /// Clear current item and reset error
  void clear() {
    _currentItem = null;
    _error = null;
    _items = [];
    _setStatus(DatabaseStatus.idle);
    notifyListeners();
  }

  /// Reset error state
  void clearError() {
    _error = null;
    notifyListeners();
  }

  void _setStatus(DatabaseStatus status) {
    _status = status;
    notifyListeners();
  }
}
