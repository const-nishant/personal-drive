import 'package:appwrite/appwrite.dart';
import 'package:personal_drive/core/config.dart';

/// Centralized Appwrite client used across the app.
class AppwriteClient {
  AppwriteClient._();

  static final Client client = Client()
    ..setEndpoint(AppConfig.appwriteEndpoint)
    ..setProject(AppConfig.appwriteProjectId)
    ..setSelfSigned();

  static final Account account = Account(client);
  static final Databases databases = Databases(client);
  static final TablesDB tables = TablesDB(client);
  static final Storage storage = Storage(client);
}
