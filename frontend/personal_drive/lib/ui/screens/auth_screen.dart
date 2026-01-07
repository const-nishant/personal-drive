import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:personal_drive/services/auth_service.dart';

class AuthScreen extends StatelessWidget {
  const AuthScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Consumer<AuthService>(
        builder: (context, authService, _) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Text(
                  'Personal Drive',
                  style: TextStyle(fontSize: 32, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 48),
                ElevatedButton.icon(
                  onPressed: authService.isLoading
                      ? null
                      : () => _handleSignIn(context, authService),
                  icon: authService.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : const Icon(Icons.login),
                  label: Text(
                    authService.isLoading
                        ? 'Signing in...'
                        : 'Sign in with Google',
                  ),
                ),
                if (authService.error != null) ...[
                  const SizedBox(height: 24),
                  Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      authService.error!,
                      style: const TextStyle(color: Colors.red),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _handleSignIn(
    BuildContext context,
    AuthService authService,
  ) async {
    await authService.login();
    // AuthWrapper will automatically show HomeScreen on successful login
  }
}
