import 'package:appwrite/appwrite.dart';
import 'package:flutter/foundation.dart';
import '../core/appwrite_client.dart';

class AuthService {
  final Account _account = Account(AppwriteClient.client);

  Future<dynamic> signUp({
    required String email,
    required String password,
    required String name,
  }) async {
    try {
      final user = await _account.create(
        userId: ID.unique(),
        email: email,
        password: password,
        name: name,
      );
      return user;
    } catch (e) {
      if (kDebugMode) {
        print('Sign up error: $e');
      }
      rethrow;
    }
  }

  Future<dynamic> signIn({
    required String email,
    required String password,
  }) async {
    try {
      final session = await _account.createEmailPasswordSession(
        email: email,
        password: password,
      );
      return session;
    } catch (e) {
      if (kDebugMode) {
        print('Sign in error: $e');
      }
      rethrow;
    }
  }

  Future<dynamic> signOut() async {
    try {
      final response = await _account.deleteSession(sessionId: 'current');
      return response;
    } catch (e) {
      if (kDebugMode) {
        print('Sign out error: $e');
      }
      rethrow;
    }
  }

  Future<dynamic> getCurrentUser() async {
    try {
      final user = await _account.get();
      return user;
    } catch (e) {
      if (kDebugMode) {
        print('Get current user error: $e');
      }
      return null;
    }
  }

  Future<bool> isLoggedIn() async {
    try {
      final user = await _account.get();
      return user != null;
    } catch (e) {
      return false;
    }
  }

  Future<dynamic> updateProfile({
    required String name,
    String? email,
    String? password,
  }) async {
    try {
      if (email != null) {
        await _account.updateEmail(email: email, password: password ?? '');
      }
      if (name.isNotEmpty) {
        await _account.updateName(name: name);
      }
      return await getCurrentUser();
    } catch (e) {
      if (kDebugMode) {
        print('Update profile error: $e');
      }
      rethrow;
    }
  }

  Future<dynamic> deleteAccount() async {
    try {
      final response = await _account.delete();
      return response;
    } catch (e) {
      if (kDebugMode) {
        print('Delete account error: $e');
      }
      rethrow;
    }
  }
}
