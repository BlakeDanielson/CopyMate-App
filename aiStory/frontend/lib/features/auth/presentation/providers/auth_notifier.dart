import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:ai_story/core/utils/logger.dart';
import 'package:ai_story/features/auth/data/dtos/auth_request.dart';
import 'package:ai_story/features/auth/domain/models/auth_state.dart';
import 'package:ai_story/features/auth/domain/models/user.dart';
import 'package:ai_story/features/auth/domain/repositories/auth_repository.dart';

/// Notifier for handling authentication state
class AuthNotifier extends StateNotifier<AuthState> {
  /// Auth repository instance
  final AuthRepository _authRepository;

  /// Creates a new [AuthNotifier] instance
  AuthNotifier({required AuthRepository authRepository})
      : _authRepository = authRepository,
        super(const AuthState.loading()) {
    // Initialize authentication state
    _initializeAuthState();
  }

  /// Initialize authentication state by checking if the user is already logged in
  Future<void> _initializeAuthState() async {
    try {
      final isAuthenticated = await _authRepository.isAuthenticated();
      
      if (isAuthenticated) {
        final user = await _authRepository.getCurrentUser();
        
        if (user != null) {
          // Get tokens from storage (implementation is handled by repository)
          final accessToken = await _getAccessToken();
          final refreshToken = await _getRefreshToken();
          
          state = AuthState.authenticated(
            user: user,
            accessToken: accessToken,
            refreshToken: refreshToken,
          );
          
          logger.i('User already authenticated: ${user.username}');
        } else {
          state = const AuthState.unauthenticated();
        }
      } else {
        state = const AuthState.unauthenticated();
      }
    } catch (e) {
      logger.e('Error initializing auth state', e);
      state = AuthState.error(message: 'Authentication initialization failed');
    }
  }

  /// Helper method to get access token from repository
  Future<String> _getAccessToken() async {
    try {
      // This would be implemented in a real repository
      // For now, return a placeholder
      return 'access_token';
    } catch (e) {
      logger.e('Error getting access token', e);
      return '';
    }
  }

  /// Helper method to get refresh token from repository
  Future<String> _getRefreshToken() async {
    try {
      // This would be implemented in a real repository
      // For now, return a placeholder
      return 'refresh_token';
    } catch (e) {
      logger.e('Error getting refresh token', e);
      return '';
    }
  }

  /// Login with username/email and password
  Future<void> login({required String username, required String password}) async {
    try {
      state = const AuthState.loading();
      
      final request = LoginRequest(username: username, password: password);
      final response = await _authRepository.login(request);
      
      state = AuthState.authenticated(
        user: response.user,
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );
      
      logger.i('User logged in: $username');
    } catch (e) {
      logger.e('Login error', e);
      state = AuthState.error(
        message: 'Login failed. Please check your credentials.',
      );
    }
  }

  /// Register a new user
  Future<void> register({
    required String username,
    required String email,
    required String password,
    String? firstName,
    String? lastName,
  }) async {
    try {
      state = const AuthState.loading();
      
      final request = RegisterRequest(
        username: username,
        email: email,
        password: password,
        firstName: firstName,
        lastName: lastName,
      );
      
      final response = await _authRepository.register(request);
      
      state = AuthState.authenticated(
        user: response.user,
        accessToken: response.accessToken,
        refreshToken: response.refreshToken,
      );
      
      logger.i('User registered: $username');
    } catch (e) {
      logger.e('Registration error', e);
      state = AuthState.error(
        message: 'Registration failed. Please try again.',
      );
    }
  }

  /// Logout the current user
  Future<void> logout() async {
    try {
      await _authRepository.logout();
      state = const AuthState.unauthenticated();
      logger.i('User logged out');
    } catch (e) {
      logger.e('Logout error', e);
      // Even if logout fails, we consider the user logged out on the client side
      state = const AuthState.unauthenticated();
    }
  }

  /// Request password reset
  Future<void> requestPasswordReset(String email) async {
    try {
      state = const AuthState.loading();
      await _authRepository.requestPasswordReset(email);
      state = const AuthState.unauthenticated();
      logger.i('Password reset requested for: $email');
    } catch (e) {
      logger.e('Password reset request error', e);
      state = AuthState.error(
        message: 'Password reset request failed. Please try again.',
      );
    }
  }

  /// Check if user is authenticated
  bool isAuthenticated() {
    return state is AuthState && state.maybeMap(
      authenticated: (_) => true,
      orElse: () => false,
    );
  }

  /// Get the current authenticated user
  User? get currentUser {
    return state.maybeMap(
      authenticated: (authenticatedState) => authenticatedState.user,
      orElse: () => null,
    );
  }

  /// Get the current access token
  String? get accessToken {
    return state.maybeMap(
      authenticated: (authenticatedState) => authenticatedState.accessToken,
      orElse: () => null,
    );
  }
  
  /// Enter test mode with mock user data
  Future<void> enterTestMode() async {
    try {
      final mockUser = MockUserData.getMockUser();
      state = AuthState.testMode(user: mockUser);
      logger.i('Entered test mode with mock user: ${mockUser.username}');
    } catch (e) {
      logger.e('Error entering test mode', e);
      state = AuthState.error(message: 'Failed to enter test mode');
    }
  }
  
  /// Exit test mode and return to unauthenticated state
  Future<void> exitTestMode() async {
    try {
      state = const AuthState.unauthenticated();
      logger.i('Exited test mode');
    } catch (e) {
      logger.e('Error exiting test mode', e);
      // Even if there's an error, we'll still try to set to unauthenticated
      state = const AuthState.unauthenticated();
    }
  }
}