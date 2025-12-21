import 'package:appwrite/appwrite.dart';

class AppwriteClient {
  static Client? _client;
  static Account? _account;
  static Storage? _storage;
  static Databases? _databases;
  static Functions? _functions;

  static void init() {
    _client = Client()
      .setEndpoint('https://cloud.appwrite.io/v1')
      .setProject('personal-drive');

    _account = Account(_client!);
    _storage = Storage(_client!);
    _databases = Databases(_client!);
    _functions = Functions(_client!);
  }

  static Client get client {
    if (_client == null) {
      init();
    }
    return _client!;
  }

  static Account get account {
    if (_account == null) {
      init();
    }
    return _account!;
  }

  static Storage get storage {
    if (_storage == null) {
      init();
    }
    return _storage!;
  }

  static Databases get databases {
    if (_databases == null) {
      init();
    }
    return _databases!;
  }

  static Functions get functions {
    if (_functions == null) {
      init();
    }
    return _functions!;
  }
}
