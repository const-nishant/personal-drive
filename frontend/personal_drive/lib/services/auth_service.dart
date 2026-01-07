import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:appwrite/appwrite.dart';
import 'package:appwrite/models.dart' as appwrite_models;
import 'package:personal_drive/core/appwrite_client.dart';
import 'package:personal_drive/core/config.dart';
import 'package:personal_drive/services/database_service.dart';

class AuthService extends ChangeNotifier {
  final GoogleSignIn _googleSignIn = GoogleSignIn();
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final Account _appwriteAccount = AppwriteClient.account;
  final DatabaseService _databaseService = DatabaseService();

  User? _user;
  appwrite_models.User? _appwriteUser;
  bool _isLoading = false;
  bool _isInitialized = false;
  String? _error;

  // Getters
  Account get appwriteAccount => _appwriteAccount;
  User? get user => _user;
  appwrite_models.User? get appwriteUser => _appwriteUser;
  bool get isLoading => _isLoading;
  bool get isInitialized => _isInitialized;
  String? get error => _error;
  bool get isAuthenticated => _user != null && _appwriteUser != null;
  String? get userId => _user?.uid;

  AuthService() {
    _initializeAuth();
  }

  /// Initialize authentication by restoring sessions
  Future<void> _initializeAuth() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Listen to Firebase auth state changes
      _firebaseAuth.authStateChanges().listen((User? user) async {
        _user = user;
        if (user != null) {
          // Firebase user exists, restore Appwrite session
          await _restoreAppwriteSession();
        }
        notifyListeners();
      });

      // Initial session check
      _user = _firebaseAuth.currentUser;
      if (_user != null) {
        await _restoreAppwriteSession();
      }
    } catch (e) {
      debugPrint('Session initialization error: $e');
      _error = e.toString();
    } finally {
      _isLoading = false;
      _isInitialized = true;
      notifyListeners();
    }
  }
  //fix the auth flow

  /// Restore Appwrite session if exists
  Future<void> _restoreAppwriteSession() async {
    if (_user == null) return;

    try {
      debugPrint('Restoring Appwrite session...');

      // Try to get current Appwrite session
      _appwriteUser = await _appwriteAccount.get();
      debugPrint('Appwrite session restored: ${_appwriteUser!.email}');
    } on AppwriteException catch (e) {
      debugPrint('No active Appwrite session: ${e.message}');

      // If no session exists, try to create one using Firebase UID
      if (e.code == 401) {
        try {
          await _createOrLinkAppwriteAccount(
            email: _user!.email!,
            name: _user!.displayName ?? _user!.email!.split('@')[0],
            firebaseUid: _user!.uid,
          );
        } catch (sessionError) {
          debugPrint('Failed to restore Appwrite session: $sessionError');
          _appwriteUser = null;
        }
      }
    } catch (e) {
      debugPrint('Unexpected error restoring session: $e');
      _appwriteUser = null;
    }
  }

  Future<void> login() async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      // Step 1: Native Google Sign-In (stays in-app)
      debugPrint('Starting native Google Sign-In...');
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        _isLoading = false;
        notifyListeners();
        return;
      }
      debugPrint('Google Sign-In successful: ${googleUser.email}');

      // Step 2: Get Google authentication details
      final GoogleSignInAuthentication googleAuth =
          await googleUser.authentication;
      final credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      // Step 3: Firebase Authentication - Create Firebase user session
      debugPrint('Signing in to Firebase...');
      final userCredential = await _firebaseAuth.signInWithCredential(
        credential,
      );
      _user = userCredential.user;

      if (_user == null) {
        throw Exception('Firebase sign-in failed');
      }
      debugPrint('Firebase sign-in successful: ${_user!.email}');

      // Step 4: Appwrite Account - Create/link using Firebase UID
      debugPrint('Creating/linking Appwrite account...');
      await _createOrLinkAppwriteAccount(
        email: _user!.email!,
        name: _user!.displayName ?? _user!.email!.split('@')[0],
        firebaseUid: _user!.uid,
      );
      debugPrint('Dual authentication successful!');

      _error = null;
    } catch (e) {
      debugPrint('Authentication error: $e');
      _error = e.toString();
      _user = null;
      _appwriteUser = null;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  /// Creates or links Appwrite account using Firebase UID as identifier
  Future<void> _createOrLinkAppwriteAccount({
    required String email,
    required String name,
    required String firebaseUid,
  }) async {
    // Use Firebase UID as password (secure since it's unique and not user-facing)
    final password = 'firebase_$firebaseUid';

    try {
      // Try to create new Appwrite account
      debugPrint('Creating Appwrite account with ID: $firebaseUid');
      await _appwriteAccount.create(
        userId: firebaseUid,
        email: email,
        password: password,
        name: name,
      );
      debugPrint('Appwrite account created successfully');
    } on AppwriteException catch (e) {
      // Account already exists
      if (e.code == 409 || e.message?.contains('already exists') == true) {
        debugPrint('Appwrite account already exists, will login');
      } else {
        rethrow;
      }
    }

    // Create Appwrite session
    try {
      debugPrint('Creating Appwrite session...');
      await _appwriteAccount.createEmailPasswordSession(
        email: email,
        password: password,
      );
      debugPrint('Appwrite session created');

      // Get Appwrite user details
      _appwriteUser = await _appwriteAccount.get();
      debugPrint('Appwrite user loaded: ${_appwriteUser!.email}');

      // Create user profile in database
      await _createUserProfile(userId: firebaseUid, email: email, name: name);
    } catch (e) {
      debugPrint('Appwrite session creation error: $e');
      rethrow;
    }
  }

  /// Creates or updates user profile in Appwrite database
  Future<void> _createUserProfile({
    required String userId,
    required String email,
    required String name,
  }) async {
    final now = DateTime.now().toUtc().toIso8601String();
    final userData = {
      'userId': userId,
      'email': email,
      'name': name,
      'status': _appwriteUser?.status ?? true,
      'createdAt': now,
      'updatedAt': now,
    };

    try {
      debugPrint('Creating user profile in database...');
      await _databaseService.createRow(
        tableId: AppConfig.usersCollectionId,
        rowId: userId,
        data: userData,
      );
      debugPrint('User profile created in database');
    } on AppwriteException catch (e) {
      // Profile might already exist, try updating
      if (e.code == 409 || e.message?.contains('already exists') == true) {
        debugPrint('User profile exists, updating...');
        try {
          await _databaseService.updateRow(
            tableId: AppConfig.usersCollectionId,
            rowId: userId,
            data: {...userData, 'updatedAt': now},
          );
          debugPrint('User profile updated');
        } catch (updateError) {
          debugPrint('Failed to update user profile: $updateError');
        }
      } else {
        debugPrint('Failed to create user profile: ${e.message}');
      }
    } catch (e) {
      debugPrint('Unexpected error creating user profile: $e');
    }
  }

  /// Validates both Firebase and Appwrite sessions are active
  Future<bool> validateSession() async {
    try {
      // Check Firebase session
      if (_firebaseAuth.currentUser == null) {
        debugPrint('No active Firebase session');
        return false;
      }

      // Check Appwrite session
      try {
        final appwriteUser = await _appwriteAccount.get();
        _appwriteUser = appwriteUser;
        debugPrint('Both sessions validated successfully');
        return true;
      } on AppwriteException catch (e) {
        debugPrint('Appwrite session invalid: ${e.message}');

        // Try to restore Appwrite session
        await _restoreAppwriteSession();
        return _appwriteUser != null;
      }
    } catch (e) {
      debugPrint('Session validation error: $e');
      return false;
    }
  }

  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      // Sign out from all services
      await _appwriteAccount.deleteSessions().catchError((e) {
        debugPrint('Appwrite logout error: $e');
      });
      await _firebaseAuth.signOut();
      await _googleSignIn.signOut();

      // Clear session state
      _user = null;
      _appwriteUser = null;
      _error = null;

      debugPrint('Logged out from all services');
    } catch (e) {
      debugPrint('Logout error: $e');
      _error = e.toString();
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
