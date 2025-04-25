import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/presentation/providers/auth_providers.dart';
import 'package:ai_story/features/auth/presentation/screens/login_screen.dart';
import 'package:ai_story/features/auth/presentation/screens/register_screen.dart';
import 'package:ai_story/features/auth/presentation/screens/forgot_password_screen.dart';
import 'package:ai_story/features/home/presentation/screens/home_screen.dart';
import 'package:ai_story/shared/widgets/error_screen.dart';

/// Routes for the application
abstract class AppRoutes {
  /// Home route
  static const home = '/';
  
  /// Login route
  static const login = '/login';
  
  /// Register route
  static const register = '/register';
  
  /// Forgot password route
  static const forgotPassword = '/forgot-password';
}

/// Provider for the application router
final appRouterProvider = Provider<GoRouter>((ref) {
  final authState = ref.watch(authNotifierProvider);
  
  return GoRouter(
    initialLocation: AppRoutes.home,
    debugLogDiagnostics: true,
    
    // Redirect based on authentication state
    redirect: (context, state) {
      // Set of public routes that don't require authentication
      final publicRoutes = {
        AppRoutes.login,
        AppRoutes.register,
        AppRoutes.forgotPassword,
      };
      
      // Check if user is in test mode
      final isTestMode = authState.isTestMode;
      
      // If route is public, allow access
      if (publicRoutes.contains(state.uri.path)) {
        // If user is already authenticated or in test mode and tries to access auth screens,
        // redirect to home
        if (authState is AuthenticatedState || isTestMode) {
          return AppRoutes.home;
        }
        // Otherwise allow access to public route
        return null;
      }

      // For protected routes, check authentication or test mode
      if ((authState is UnauthenticatedState || authState is ErrorAuthState) && !isTestMode) {
        // Redirect to login if not authenticated and not in test mode
        return AppRoutes.login;
      }

      // For LoadingAuthState, we could show a loading screen
      // but for simplicity, we'll keep the user on the current page
      if (authState is LoadingAuthState) {
        return null;
      }

      // Allow access to the route if authenticated or in test mode
      return null;
    },
    
    // Route configuration
    routes: [
      // Home route (protected)
      GoRoute(
        path: AppRoutes.home,
        name: 'home',
        builder: (context, state) => const HomeScreen(),
      ),
      
      // Login route
      GoRoute(
        path: AppRoutes.login,
        name: 'login',
        builder: (context, state) => const LoginScreen(),
      ),
      
      // Register route
      GoRoute(
        path: AppRoutes.register,
        name: 'register',
        builder: (context, state) => const RegisterScreen(),
      ),
      
      // Forgot password route
      GoRoute(
        path: AppRoutes.forgotPassword,
        name: 'forgotPassword',
        builder: (context, state) => const ForgotPasswordScreen(),
      ),
    ],
    
    // Error handling
    errorBuilder: (context, state) {
      logger.e('Navigation error: ${state.error}');
      return ErrorScreen(
        errorMessage: 'Page not found: ${state.error}',
      );
    },
  );
});