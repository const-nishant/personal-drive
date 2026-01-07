import 'package:flutter/material.dart';
import 'package:personal_drive/ui/widgets/appbottom_navigation.dart';
import 'package:provider/provider.dart';
import 'package:personal_drive/services/auth_service.dart';
import 'package:personal_drive/ui/screens/auth_screen.dart';

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AuthService>(
      builder: (context, authService, _) {
        // Show loading while initializing
        if (!authService.isInitialized || authService.isLoading) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }

        // Show home screen if authenticated, otherwise auth screen
        return authService.isAuthenticated
            ? const AppNavbar()
            : const AuthScreen();
      },
    );
  }
}
